"""Apresentação do orçamento: resumo no terminal e arquivo CSV.

Separar isso das classes de cálculo mantém cada classe com uma única
responsabilidade: Orcamento calcula, RelatorioOrcamento apresenta.
"""

import csv
import re
import unicodedata
from decimal import Decimal

from orcamento import Orcamento


def formatar_moeda(valor: Decimal) -> str:
    """Formata como moeda brasileira: R$ 1.234,56."""
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def formatar_decimal_csv(valor: Decimal) -> str:
    """Decimal com vírgula (padrão do Excel em português), sem símbolo de moeda."""
    return f"{valor:.2f}".replace(".", ",")


def nome_para_arquivo(nome: str) -> str:
    """Transforma 'João da Silva' em 'joao_da_silva' (seguro para nome de arquivo)."""
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", sem_acento.lower()).strip("_") or "cliente"


class RelatorioOrcamento:
    """Gera o resumo em texto e o CSV de projeção de um Orcamento."""

    CABECALHO_CSV = [
        "Mes",
        "Aluguel base (R$)",
        "Adicionais (R$)",
        "Desconto (R$)",
        "Aluguel mensal (R$)",
        "Parcela taxa contratual (R$)",
        "Total do mes (R$)",
    ]

    def __init__(self, orcamento: Orcamento):
        self.orcamento = orcamento

    def resumo(self) -> str:
        o = self.orcamento
        imovel, taxa = o.imovel, o.taxa
        linha = "=" * 58
        separador = "-" * 58
        saida = [
            linha,
            "  R.M IMÓVEIS - ORÇAMENTO DE LOCAÇÃO (RentSmart)",
            linha,
            f"Cliente: {o.cliente}",
            f"Imóvel : {imovel.descricao()}",
            "",
            "ALUGUEL MENSAL",
            separador,
            f"  {'Aluguel-base':<38}{formatar_moeda(imovel.aluguel_base):>18}",
        ]
        for item in imovel.adicionais():
            saida.append(f"  {'+ ' + item.descricao:<38}{formatar_moeda(item.valor):>18}")
        saida.append(f"  {'Subtotal':<38}{formatar_moeda(imovel.subtotal()):>18}")
        if imovel.desconto() > 0:
            saida.append(
                f"  {'- ' + imovel.descricao_desconto():<38}{formatar_moeda(imovel.desconto()):>18}"
            )
        saida += [
            separador,
            f"  {'VALOR MENSAL DO ALUGUEL':<38}{formatar_moeda(imovel.aluguel_mensal()):>18}",
            "",
            "TAXA CONTRATUAL (cobrada à parte do aluguel)",
            separador,
            f"  {'Valor total da taxa':<38}{formatar_moeda(taxa.valor):>18}",
        ]
        valores = taxa.valores_das_parcelas()
        if taxa.parcelas == 1:
            saida.append(f"  {'Pagamento':<38}{'à vista':>18}")
        else:
            saida.append(f"  {'Parcelamento':<38}{f'{taxa.parcelas}x sem juros':>18}")
            saida.append(f"  {'Valor da parcela':<38}{formatar_moeda(valores[0]):>18}")
            if valores[-1] != valores[0]:
                saida.append(
                    f"  {'Última parcela (ajuste de centavos)':<38}{formatar_moeda(valores[-1]):>18}"
                )
        saida += [
            "",
            "PROJEÇÃO DO PRIMEIRO ANO",
            separador,
            f"  {'Total de aluguéis (12 meses)':<38}{formatar_moeda(imovel.aluguel_mensal() * 12):>18}",
            f"  {'Taxa contratual':<38}{formatar_moeda(taxa.valor):>18}",
            f"  {'TOTAL NO 1º ANO':<38}{formatar_moeda(o.total_periodo(12)):>18}",
            linha,
        ]
        return "\n".join(saida)

    def exportar_csv(self, caminho: str, meses: int = 12) -> str:
        """Grava a projeção em CSV (separador ';', decimal ',' e UTF-8 com BOM
        para abrir corretamente no Excel em português). Retorna o caminho."""
        linhas = self.orcamento.projecao(meses)
        with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(self.CABECALHO_CSV)
            for l in linhas:
                escritor.writerow(
                    [
                        l.mes,
                        formatar_decimal_csv(l.aluguel_base),
                        formatar_decimal_csv(l.adicionais),
                        formatar_decimal_csv(l.desconto),
                        formatar_decimal_csv(l.aluguel_mensal),
                        formatar_decimal_csv(l.parcela_taxa),
                        formatar_decimal_csv(l.total_do_mes),
                    ]
                )
            escritor.writerow(
                [
                    "TOTAL",
                    "",
                    "",
                    "",
                    formatar_decimal_csv(sum((l.aluguel_mensal for l in linhas), Decimal("0"))),
                    formatar_decimal_csv(sum((l.parcela_taxa for l in linhas), Decimal("0"))),
                    formatar_decimal_csv(sum((l.total_do_mes for l in linhas), Decimal("0"))),
                ]
            )
        return caminho
