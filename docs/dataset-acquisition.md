# Aquisição e armazenamento do dataset

## Fonte registrada no plano

- Página informada: <https://www.kaggle.com/datasets/ethon0426/lending-club-20072020q1>
- Tese: Lending Club, 2.925.493 linhas, 142 colunas, período de 2007 ao terceiro trimestre de 2020.
- Notebook recuperado: caminho absoluto `/content/Loan_status_2007-2020Q3.gzip`.

Há uma divergência nominal entre o identificador `20072020q1` da página e as referências a `2020Q3` na tese e no notebook. A aquisição de 4 de agosto de 2026 resolveu essa divergência para o artefato atual: o ZIP contém `Loan_status_2007-2020Q3.gzip`, com `issue_d` de junho de 2007 a setembro de 2020. O slug é Q1, mas o conteúdo publicado cobre Q3. Versões futuras ainda deverão ser conferidas pelo hash.

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

Essa resolução está implementada em `src/tcc_reconstruction/data.py`. Quando houver mais de um arquivo em `data/raw/`, a seleção explícita é obrigatória para impedir o uso acidental da versão errada.

## Download sugerido

Depois que a proteção do repositório for confirmada e o acesso ao Kaggle estiver configurado localmente:

```bash
mkdir -p data/raw
kaggle datasets download -d ethon0426/lending-club-20072020q1 -p data/raw
```

As credenciais devem ficar fora do repositório, no local padrão da ferramenta Kaggle. Não copiar `kaggle.json` para este projeto.

Extraia somente o CSV necessário:

```bash
unzip -n data/raw/lending-club-20072020q1.zip \
  Loan_status_2007-2020Q3.gzip \
  -d data/raw
git check-ignore data/raw/Loan_status_2007-2020Q3.gzip
```

O ZIP também contém `LCDataDictionary.xlsx`. O membro `.gzip` tem nome histórico enganoso: sua assinatura identifica CSV ASCII sem compressão adicional. O pipeline detecta compressão pela assinatura binária, não apenas pela extensão.

## Manifesto da fonte

Na primeira aquisição autorizada, registrar sem versionar os dados:

| Campo | Valor a registrar |
|---|---|
| URL/slug Kaggle | `ethon0426/lending-club-20072020q1` |
| validação local | 4 de agosto de 2026 |
| ZIP | `lending-club-20072020q1.zip`; 505.408.012 bytes; SHA-256 `2d11fedfb54381bf0708b41ca906b047349e35957ec9718d790dcff63d692941` |
| arquivo de dados | `Loan_status_2007-2020Q3.gzip`; CSV; 1.773.470.505 bytes |
| SHA-256 dos dados | `5878af2a088f8ab5214c9337289fb8b5eb6c6338fd3f417b6cdc18513dc6f` |
| número de linhas | 2.925.493, igual à tese |
| número de colunas | 142, igual à tese |
| menor/maior `issue_d` | junho de 2007 / setembro de 2020 |
| resolução Q1/Q3 | conteúdo confirmado até Q3 de 2020 |

Gere o manifesto e o resumo do processamento com:

```bash
python scripts/prepare_dataset.py \
  --dataset data/raw/Loan_status_2007-2020Q3.gzip \
  --hash-source
```

A saída JSON contém somente metadados, nomes de colunas e contagens agregadas. O caminho absoluto não é incluído.
Os resultados reproduzidos e próprios para versionamento estão em [`../provenance/dataset-manifest.json`](../provenance/dataset-manifest.json).

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

O pipeline implementado:

- inspecionar apenas cabeçalho/esquema inicialmente;
- carregar somente as colunas necessárias por etapa;
- declarar tipos quando isso reduzir memória com segurança;
- filtrar status o mais cedo possível;
- oferecer amostra determinística para desenvolvimento;
- exibir contagem de linhas e memória estimada antes/depois de cada filtro;
- falhar com mensagem clara quando colunas obrigatórias estiverem ausentes.

Por padrão, são lidos blocos de 100.000 linhas e mantida em memória uma amostra determinística de 10.000 registros. Todos os blocos ainda são percorridos para que as contagens antes/depois e a análise de valores ausentes representem o arquivo inteiro.

Valores ausentes não são imputados nesta fase. O pipeline apenas os contabiliza e sinaliza colunas com pelo menos 90% de ausência; removê-las ou imputá-las antes da separação treino/teste poderia repetir o erro observado no notebook recuperado e provocar vazamento nas fases de modelagem.
