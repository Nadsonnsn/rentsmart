"""Modelo de domínio dos imóveis da R.M Imóveis.

Hierarquia de classes:

    Imovel (abstrata)
    ├── ImovelResidencial (abstrata: casas e apartamentos)
    │   ├── Apartamento
    │   └── Casa
    └── Estudio

Cada subclasse conhece suas próprias regras (aluguel-base, adicionais,
desconto). Quem usa a classe (o Orcamento) não precisa saber qual é o tipo
do imóvel: basta chamar os mesmos métodos (polimorfismo).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

CENTAVO = Decimal("0.01")
ZERO = Decimal("0.00")


def moeda(valor) -> Decimal:
    """Arredonda qualquer valor para centavos (Decimal evita erros de float)."""
    return Decimal(valor).quantize(CENTAVO, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class ItemOrcamento:
    """Uma linha do orçamento: descrição + valor mensal."""

    descricao: str
    valor: Decimal


class Imovel(ABC):
    """Classe base: define o que todo imóvel precisa saber calcular."""

    tipo: str = ""
    aluguel_base: Decimal = ZERO

    def __init__(self, vagas: int = 0):
        if not isinstance(vagas, int) or isinstance(vagas, bool) or vagas < 0:
            raise ValueError("O número de vagas deve ser um inteiro maior ou igual a 0.")
        self.vagas = vagas

    @abstractmethod
    def descricao(self) -> str:
        """Texto curto que identifica o imóvel (ex.: 'Apartamento de 2 quartos')."""

    @abstractmethod
    def adicionais(self) -> list[ItemOrcamento]:
        """Lista de acréscimos mensais que se aplicam a este imóvel."""

    def total_adicionais(self) -> Decimal:
        return moeda(sum((item.valor for item in self.adicionais()), ZERO))

    def subtotal(self) -> Decimal:
        """Aluguel-base + adicionais (valor sobre o qual o desconto incide)."""
        return moeda(self.aluguel_base + self.total_adicionais())

    def desconto(self) -> Decimal:
        """Por padrão não há desconto; subclasses sobrescrevem se houver."""
        return ZERO

    def descricao_desconto(self) -> str:
        return ""

    def aluguel_mensal(self) -> Decimal:
        return moeda(self.subtotal() - self.desconto())


class ImovelResidencial(Imovel):
    """Regras comuns a casas e apartamentos: 1 ou 2 quartos e 0 ou 1 vaga."""

    adicional_segundo_quarto: Decimal = ZERO
    valor_vaga: Decimal = Decimal("300.00")
    max_vagas: int = 1

    def __init__(self, quartos: int = 1, vagas: int = 0):
        super().__init__(vagas)
        if quartos not in (1, 2):
            raise ValueError("Casas e apartamentos podem ter 1 ou 2 quartos.")
        if vagas > self.max_vagas:
            raise ValueError(
                f"{self.tipo} aceita no máximo {self.max_vagas} vaga de garagem."
            )
        self.quartos = quartos

    def descricao(self) -> str:
        plural = "quarto" if self.quartos == 1 else "quartos"
        return f"{self.tipo} de {self.quartos} {plural}"

    def adicionais(self) -> list[ItemOrcamento]:
        itens = []
        if self.quartos == 2:
            itens.append(ItemOrcamento("Adicional de 2º quarto", self.adicional_segundo_quarto))
        if self.vagas == 1:
            itens.append(ItemOrcamento("Vaga de garagem", self.valor_vaga))
        return itens


class Apartamento(ImovelResidencial):
    tipo = "Apartamento"
    aluguel_base = Decimal("700.00")
    adicional_segundo_quarto = Decimal("200.00")
    percentual_desconto = Decimal("0.05")

    def __init__(self, quartos: int = 1, vagas: int = 0, tem_criancas: bool = True):
        super().__init__(quartos, vagas)
        self.tem_criancas = tem_criancas

    def desconto(self) -> Decimal:
        """5% sobre (aluguel-base + adicionais) para clientes sem crianças."""
        if self.tem_criancas:
            return ZERO
        return moeda(self.subtotal() * self.percentual_desconto)

    def descricao_desconto(self) -> str:
        return "Desconto de 5% (cliente sem crianças)" if not self.tem_criancas else ""


class Casa(ImovelResidencial):
    tipo = "Casa"
    aluguel_base = Decimal("900.00")
    adicional_segundo_quarto = Decimal("250.00")


class Estudio(Imovel):
    """Estúdio: sem opção de quartos; estacionamento em pacote de 2 vagas."""

    tipo = "Estúdio"
    aluguel_base = Decimal("1200.00")
    valor_pacote_vagas = Decimal("250.00")
    vagas_no_pacote = 2
    valor_vaga_adicional = Decimal("60.00")

    def descricao(self) -> str:
        return "Estúdio"

    def adicionais(self) -> list[ItemOrcamento]:
        itens = []
        if self.vagas > 0:
            itens.append(
                ItemOrcamento(
                    f"Pacote de estacionamento ({self.vagas_no_pacote} vagas)",
                    self.valor_pacote_vagas,
                )
            )
        extras = max(0, self.vagas - self.vagas_no_pacote)
        if extras:
            itens.append(
                ItemOrcamento(
                    f"{extras} vaga(s) adicional(is) x R$ 60,00",
                    self.valor_vaga_adicional * extras,
                )
            )
        return itens
