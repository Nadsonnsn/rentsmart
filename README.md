# RentSmart — Sistema de Orçamento de Locação (R.M Imóveis)

Aplicação em **Python** com **Programação Orientada a Objetos** que calcula o orçamento
de locação de casas, apartamentos e estúdios da R.M Imóveis, mostra um resumo detalhado
no terminal e gera um **CSV com a projeção dos 12 primeiros meses** de contrato.

Trabalho da disciplina *Algorithmic Thinking & Introduction to Object-Oriented Programming*.

## Requisitos

- Python 3.10 ou superior (testado com 3.12)
- Nenhuma biblioteca externa (usa apenas a biblioteca padrão)

## Como executar

```bash
python main.py
```

O programa pergunta, nesta ordem: nome do cliente, tipo de imóvel, quartos, garagem /
vagas, se possui crianças (apenas apartamento) e em quantas parcelas será paga a taxa
contratual. Ao final mostra o orçamento e salva o arquivo
`projecao_12_meses_<nome_do_cliente>.csv` na pasta atual.

Para rodar os testes automatizados:

```bash
python -m unittest -v
```

## Regras de negócio implementadas

| Item | Regra |
|---|---|
| Aluguel-base | Apartamento 1 quarto R$ 700 · Casa 1 quarto R$ 900 · Estúdio R$ 1.200 |
| 2º quarto | Apartamento +R$ 200 · Casa +R$ 250 (estúdio não tem opção de quartos) |
| Garagem | Casa/apartamento: 1 vaga por +R$ 300 |
| Estacionamento do estúdio | Pacote de 2 vagas R$ 250 + R$ 60 por vaga adicional |
| Desconto | Apenas apartamento, 5% sem crianças, **sobre aluguel-base + adicionais** |
| Taxa contratual | R$ 2.000 em 1 a 5 parcelas, sem juros, **separada do aluguel** |

### Interpretações adotadas (o enunciado deixa em aberto)

1. **Estúdio sem vagas:** o estacionamento é opcional. Com 0 vagas não há cobrança; com 1 ou
   2 vagas paga-se o pacote de R$ 250; a partir da 3ª vaga soma-se R$ 60 por vaga extra.
2. **Casa e apartamento:** aceitam no máximo 1 vaga (o enunciado só prevê "uma vaga").
3. **Desconto de 5%:** incide sobre o aluguel já com 2º quarto e garagem, e **não** sobre a
   taxa contratual.
4. **Parcelamento da taxa:** sem juros. Quando a divisão não é exata (ex.: 3x), a última
   parcela absorve a diferença de centavos (666,67 + 666,67 + 666,66 = 2.000,00).
5. **CSV:** o aluguel é cobrado nos 12 meses; a parcela da taxa aparece apenas nos meses
   parcelados. Usa separador `;`, decimal `,` e UTF-8 com BOM para abrir direto no Excel em
   português.

## Estrutura do projeto

```
rentsmart/
├── main.py                 # interface de terminal e validação das entradas
├── imoveis.py              # Imovel (abstrata), ImovelResidencial, Apartamento, Casa, Estudio
├── orcamento.py            # TaxaContratual, LinhaProjecao, Orcamento
├── relatorio.py            # RelatorioOrcamento (resumo em texto e CSV)
├── test_rentsmart.py       # 23 testes automatizados (unittest)
├── exemplo_projecao_12_meses_maria_souza.csv   # exemplo de arquivo gerado
└── README.md
```

### Classes principais

- **`Imovel`** (abstrata): contrato comum — `adicionais()`, `subtotal()`, `desconto()`, `aluguel_mensal()`.
- **`ImovelResidencial`**: regras compartilhadas por casas e apartamentos (1–2 quartos, 0–1 vaga).
- **`Apartamento`**, **`Casa`**, **`Estudio`**: aluguel-base e regras específicas de cada tipo (polimorfismo).
- **`TaxaContratual`**: valor, número de parcelas e cálculo das parcelas.
- **`Orcamento`**: junta cliente + imóvel + taxa e gera a projeção mensal.
- **`RelatorioOrcamento`**: formata o resumo e exporta o CSV (separa apresentação de cálculo).

## Autor

<seu nome> — <seu RA / curso>
