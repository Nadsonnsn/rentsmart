"""Classes de orçamento: taxa contratual, projeção mensal e o Orcamento em si."""

from dataclasses import dataclass
from decimal import Decimal

from imoveis import Imovel, ZERO, moeda


class TaxaContratual:
    """Taxa de contrato (R$ 2.000,00) parcelável em até 5 vezes, sem juros."""

    VALOR = Decimal("2000.00")
    MAX_PARCELAS = 5

    def __init__(self, parcelas: int = 1):
        if not isinstance(parcelas, int) or isinstance(parcelas, bool):
            raise ValueError("O número de parcelas deve ser um inteiro.")
        if not 1 <= parcelas <= self.MAX_PARCELAS:
            raise ValueError(f"A taxa pode ser paga em 1 a {self.MAX_PARCELAS} parcelas.")
        self.valor = self.VALOR
        self.parcelas = parcelas

    def valor_parcela(self) -> Decimal:
        """Valor da parcela padrão (arredondado para centavos)."""
        return moeda(self.valor / self.parcelas)

    def valores_das_parcelas(self) -> list[Decimal]:
        """Lista com o valor de cada parcela.

        A última parcela absorve a diferença de arredondamento para que a
        soma seja sempre exatamente R$ 2.000,00 (ex.: 3x = 666,67 + 666,67 + 666,66).
        """
        padrao = self.valor_parcela()
        valores = [padrao] * (self.parcelas - 1)
        valores.append(moeda(self.valor - sum(valores, ZERO)))
        return valores


@dataclass(frozen=True)
class LinhaProjecao:
    """Um mês da projeção contratual."""

    mes: int
    aluguel_base: Decimal
    adicionais: Decimal
    desconto: Decimal
    aluguel_mensal: Decimal
    parcela_taxa: Decimal

    @property
    def total_do_mes(self) -> Decimal:
        return moeda(self.aluguel_mensal + self.parcela_taxa)


class Orcamento:
    """Reúne cliente, imóvel e taxa contratual e calcula a projeção mensal."""

    def __init__(self, cliente: str, imovel: Imovel, taxa: TaxaContratual):
        cliente = cliente.strip()
        if not cliente:
            raise ValueError("O nome do cliente não pode ficar em branco.")
        self.cliente = cliente
        self.imovel = imovel
        self.taxa = taxa

    def projecao(self, meses: int = 12) -> list[LinhaProjecao]:
        """Gera a projeção mês a mês (o aluguel é fixo; a taxa só aparece nas parcelas)."""
        parcelas = self.taxa.valores_das_parcelas()
        linhas = []
        for mes in range(1, meses + 1):
            parcela = parcelas[mes - 1] if mes <= len(parcelas) else ZERO
            linhas.append(
                LinhaProjecao(
                    mes=mes,
                    aluguel_base=self.imovel.aluguel_base,
                    adicionais=self.imovel.total_adicionais(),
                    desconto=self.imovel.desconto(),
                    aluguel_mensal=self.imovel.aluguel_mensal(),
                    parcela_taxa=parcela,
                )
            )
        return linhas

    def total_periodo(self, meses: int = 12) -> Decimal:
        return moeda(sum((l.total_do_mes for l in self.projecao(meses)), ZERO))
