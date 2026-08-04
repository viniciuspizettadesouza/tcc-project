# Aquisição e armazenamento do dataset

## Fonte registrada no plano

- Página informada: <https://www.kaggle.com/datasets/ethon0426/lending-club-20072020q1>
- Tese: Lending Club, 2.925.493 linhas, 142 colunas, período de 2007 ao terceiro trimestre de 2020.
- Notebook recuperado: caminho absoluto `/content/Loan_status_2007-2020Q3.gzip`.

Há uma divergência entre o identificador `20072020q1` da página informada e as referências a `2020Q3` na tese e no nome utilizado pelo notebook. O arquivo exato, seu hash, tamanho, esquema e período efetivo devem ser registrados na primeira execução. Não se deve assumir que versões distintas do dataset produzem os mesmos resultados.

## Layout local proposto

```text
data/
├── raw/          # arquivo original baixado, nunca versionado
├── interim/      # cache opcional de desenvolvimento, nunca versionado
└── README.md     # opcional: metadados sem dados pessoais nem conteúdo do dataset
```

O código deverá aceitar, nesta ordem:

1. argumento/configuração explícita do notebook;
2. variável de ambiente `LENDING_CLUB_DATA_PATH`;
3. caminho relativo documentado em `data/raw/`.

Nenhum caminho `/content/...` deve ser obrigatório. No Colab, o usuário poderá apontar a configuração para um arquivo carregado na sessão ou armazenado no próprio Drive.

## Download sugerido

Depois que a proteção do repositório for confirmada e o acesso ao Kaggle estiver configurado localmente:

```bash
mkdir -p data/raw
kaggle datasets download -d ethon0426/lending-club-20072020q1 -p data/raw
```

As credenciais devem ficar fora do repositório, no local padrão da ferramenta Kaggle. Não copiar `kaggle.json` para este projeto.

O nome interno do arquivo compactado deve ser inspecionado após o download. A implementação não deve codificar um nome presumido antes dessa inspeção.

## Manifesto da fonte

Na primeira aquisição autorizada, registrar sem versionar os dados:

| Campo | Valor a registrar |
|---|---|
| URL/slug Kaggle | `ethon0426/lending-club-20072020q1` |
| data do download | pendente |
| nome do arquivo | pendente |
| tamanho em bytes | pendente |
| SHA-256 | pendente |
| número de linhas | esperado pela tese: 2.925.493; confirmar |
| número de colunas | esperado pela tese: 142 antes de `year`; confirmar |
| menor/maior `issue_d` | pendente |
| status encontrados | pendente |

## Validação mínima do esquema

Antes da reconstrução, confirmar pelo menos:

- identificadores e datas: `id`, `issue_d`;
- alvo: `loan_status`;
- valores financeiros: `loan_amnt`, `funded_amnt`, `int_rate`, `installment`, `annual_inc`, `dti`;
- crédito: `fico_range_low`, `fico_range_high`, `grade`, `sub_grade`, `open_acc`, `total_acc`;
- PoC 1: `all_util`, `acc_open_past_24mths`;
- segmentação: `home_ownership`, `application_type`, `addr_state`;
- demais atributos da PoC 2 listados em `docs/reconstruction-analysis.md`.

A coluna `fico` não é uma coluna Lending Club confirmada pelo notebook recuperado. Ela precisa ser derivada de `fico_range_low` e `fico_range_high` por regra documentada, provavelmente a média dos limites, e essa hipótese deve ser validada antes do treinamento.

## Carregamento consciente de memória

A fase de pipeline deverá:

- inspecionar apenas cabeçalho/esquema inicialmente;
- carregar somente as colunas necessárias por etapa;
- declarar tipos quando isso reduzir memória com segurança;
- filtrar status o mais cedo possível;
- oferecer amostra determinística para desenvolvimento;
- exibir contagem de linhas e memória estimada antes/depois de cada filtro;
- falhar com mensagem clara quando colunas obrigatórias estiverem ausentes.
