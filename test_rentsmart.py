"""Testes das regras da R.M Imóveis.  Execute com:  python -m unittest -v"""

import csv
import os
import tempfile
import unittest
from decimal import Decimal

from imoveis import Apartamento, Casa, Estudio
from orcamento import Orcamento, TaxaContratual
from relatorio import RelatorioOrcamento, formatar_moeda, nome_para_arquivo

D = Decimal


class TestApartamento(unittest.TestCase):
    def test_1_quarto_sem_adicionais_com_criancas(self):
        self.assertEqual(Apartamento(1, 0, True).aluguel_mensal(), D("700.00"))

    def test_1_quarto_sem_criancas_tem_desconto(self):
        self.assertEqual(Apartamento(1, 0, False).aluguel_mensal(), D("665.00"))

    def test_2_quartos_garagem_sem_criancas(self):
        # (700 + 200 + 300) = 1200 ; 5% = 60 ; 1140
        apto = Apartamento(2, 1, False)
        self.assertEqual(apto.subtotal(), D("1200.00"))
        self.assertEqual(apto.desconto(), D("60.00"))
        self.assertEqual(apto.aluguel_mensal(), D("1140.00"))

    def test_2_quartos_garagem_com_criancas(self):
        self.assertEqual(Apartamento(2, 1, True).aluguel_mensal(), D("1200.00"))


class TestCasa(unittest.TestCase):
    def test_1_quarto(self):
        self.assertEqual(Casa(1, 0).aluguel_mensal(), D("900.00"))

    def test_2_quartos_com_garagem(self):
        self.assertEqual(Casa(2, 1).aluguel_mensal(), D("1450.00"))

    def test_casa_nunca_tem_desconto(self):
        self.assertEqual(Casa(2, 1).desconto(), D("0.00"))


class TestEstudio(unittest.TestCase):
    def test_sem_vagas(self):
        self.assertEqual(Estudio(vagas=0).aluguel_mensal(), D("1200.00"))

    def test_pacote_de_duas_vagas(self):
        self.assertEqual(Estudio(vagas=2).aluguel_mensal(), D("1450.00"))

    def test_vagas_adicionais(self):
        # 1200 + 250 + 2 x 60 = 1570
        self.assertEqual(Estudio(vagas=4).aluguel_mensal(), D("1570.00"))


class TestValidacao(unittest.TestCase):
    def test_quartos_invalidos(self):
        with self.assertRaises(ValueError):
            Casa(3, 0)

    def test_residencial_aceita_so_uma_vaga(self):
        with self.assertRaises(ValueError):
            Apartamento(1, 2, True)

    def test_vagas_negativas(self):
        with self.assertRaises(ValueError):
            Estudio(vagas=-1)

    def test_parcelas_fora_do_limite(self):
        for invalido in (0, 6):
            with self.assertRaises(ValueError):
                TaxaContratual(invalido)

    def test_cliente_em_branco(self):
        with self.assertRaises(ValueError):
            Orcamento("   ", Casa(), TaxaContratual(1))


class TestTaxaContratual(unittest.TestCase):
    def test_soma_das_parcelas_e_sempre_2000(self):
        for n in range(1, 6):
            self.assertEqual(sum(TaxaContratual(n).valores_das_parcelas()), D("2000.00"))

    def test_ajuste_de_centavos_na_ultima_parcela(self):
        self.assertEqual(
            TaxaContratual(3).valores_das_parcelas(),
            [D("666.67"), D("666.67"), D("666.66")],
        )


class TestProjecaoECsv(unittest.TestCase):
    def setUp(self):
        self.orc = Orcamento("Maria Souza", Apartamento(2, 1, False), TaxaContratual(5))

    def test_projecao_tem_12_meses(self):
        self.assertEqual(len(self.orc.projecao()), 12)

    def test_taxa_so_aparece_nos_meses_parcelados(self):
        linhas = self.orc.projecao()
        self.assertTrue(all(l.parcela_taxa == D("400.00") for l in linhas[:5]))
        self.assertTrue(all(l.parcela_taxa == D("0.00") for l in linhas[5:]))

    def test_total_do_primeiro_ano(self):
        # 12 x 1140 + 2000
        self.assertEqual(self.orc.total_periodo(), D("15680.00"))

    def test_csv_gerado(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "teste.csv")
            RelatorioOrcamento(self.orc).exportar_csv(caminho)
            with open(caminho, newline="", encoding="utf-8-sig") as f:
                linhas = list(csv.reader(f, delimiter=";"))
        self.assertEqual(len(linhas), 1 + 12 + 1)  # cabeçalho + 12 meses + total
        self.assertEqual(linhas[1][4], "1140,00")
        self.assertEqual(linhas[-1][6], "15680,00")


class TestFormatacao(unittest.TestCase):
    def test_moeda_brasileira(self):
        self.assertEqual(formatar_moeda(D("1234.5")), "R$ 1.234,50")

    def test_nome_para_arquivo(self):
        self.assertEqual(nome_para_arquivo("João da Silva"), "joao_da_silva")


if __name__ == "__main__":
    unittest.main()
