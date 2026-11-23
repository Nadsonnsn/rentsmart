"""RentSmart - Sistema de Orçamento de Locação da R.M Imóveis.

Execute com:  python main.py
"""

from imoveis import Apartamento, Casa, Estudio, Imovel
from orcamento import Orcamento, TaxaContratual
from relatorio import RelatorioOrcamento, nome_para_arquivo


# ---------------------------------------------------------------------------
# Funções de entrada (cada uma repete a pergunta até receber um valor válido)
# ---------------------------------------------------------------------------
def pedir_texto(pergunta: str) -> str:
    while True:
        resposta = input(pergunta).strip()
        if resposta:
            return resposta
        print("  ! O campo não pode ficar em branco.")


def pedir_inteiro(pergunta: str, minimo: int, maximo: int | None = None) -> int:
    while True:
        resposta = input(pergunta).strip()
        try:
            numero = int(resposta)
        except ValueError:
            print("  ! Digite um número inteiro.")
            continue
        if numero < minimo or (maximo is not None and numero > maximo):
            faixa = f"entre {minimo} e {maximo}" if maximo is not None else f"a partir de {minimo}"
            print(f"  ! Valor inválido. Digite um número {faixa}.")
            continue
        return numero


def pedir_sim_nao(pergunta: str) -> bool:
    while True:
        resposta = input(pergunta + " (s/n): ").strip().lower()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao", "não"):
            return False
        print("  ! Responda com 's' ou 'n'.")


# ---------------------------------------------------------------------------
# Montagem do imóvel conforme as escolhas do cliente
# ---------------------------------------------------------------------------
def montar_imovel() -> Imovel:
    print("\nTipos de imóvel:")
    print("  1 - Apartamento (a partir de R$ 700,00)")
    print("  2 - Casa        (a partir de R$ 900,00)")
    print("  3 - Estúdio     (a partir de R$ 1.200,00)")
    tipo = pedir_inteiro("Escolha o tipo (1-3): ", 1, 3)

    if tipo == 3:
        print("Estúdio: pacote de 2 vagas por R$ 250,00 (+ R$ 60,00 por vaga adicional).")
        vagas = pedir_inteiro("Quantas vagas de estacionamento (0 = nenhuma): ", 0)
        return Estudio(vagas=vagas)

    quartos = pedir_inteiro("Número de quartos (1 ou 2): ", 1, 2)
    vagas = 1 if pedir_sim_nao("Deseja vaga de garagem (+ R$ 300,00)?") else 0

    if tipo == 1:
        tem_criancas = pedir_sim_nao("Possui crianças?")
        return Apartamento(quartos, vagas, tem_criancas)
    return Casa(quartos, vagas)


def montar_taxa() -> TaxaContratual:
    print("\nA taxa contratual é de R$ 2.000,00 e pode ser parcelada em até 5 vezes sem juros.")
    parcelas = pedir_inteiro("Em quantas parcelas deseja pagar (1-5)? ", 1, TaxaContratual.MAX_PARCELAS)
    return TaxaContratual(parcelas)


def novo_orcamento() -> None:
    cliente = pedir_texto("Nome do cliente: ")
    imovel = montar_imovel()
    taxa = montar_taxa()

    orcamento = Orcamento(cliente, imovel, taxa)
    relatorio = RelatorioOrcamento(orcamento)

    print()
    print(relatorio.resumo())

    caminho = f"projecao_12_meses_{nome_para_arquivo(cliente)}.csv"
    relatorio.exportar_csv(caminho)
    print(f"\nArquivo CSV com a projeção de 12 meses gerado: {caminho}")


def main() -> None:
    print("=" * 58)
    print("  RentSmart - R.M Imóveis")
    print("=" * 58)
    while True:
        novo_orcamento()
        if not pedir_sim_nao("\nDeseja fazer outro orçamento?"):
            break
    print("\nObrigado por usar o RentSmart!")


if __name__ == "__main__":
    main()
