# Guia do dataset e pipeline

## Fonte e divergência nominal

O dataset externo é o Lending Club publicado no Kaggle sob o slug `ethon0426/lending-club-20072020q1`. O membro validado chama-se `Loan_status_2007-2020Q3.gzip` e contém dados até setembro de 2020; portanto, o conteúdo confirma Q3 apesar do slug terminar em Q1.

| Artefato | Tamanho | SHA-256 |
|---|---:|---|
| ZIP do Kaggle | 505.408.012 bytes | `2d11fedfb54381bf0708b41ca906b047349e35957ec9718d790dcff63d692941` |
| CSV publicado com sufixo `.gzip` | 1.773.470.505 bytes | `5878af2a088f8ab5214c9337289fb8b5eb6c6338fd3f417b6cdc18513dc6f` |

O CSV possui 2.925.493 linhas, 142 colunas e período 2007-06–2020-09. O ZIP também contém `LCDataDictionary.xlsx`. O arquivo `.gzip` é CSV sem compressão adicional; o pipeline detecta o formato pela assinatura binária.

## Segurança e layout

Dados e credenciais nunca devem ser versionados:

```text
data/
└── raw/
    ├── lending-club-20072020q1.zip
    └── Loan_status_2007-2020Q3.gzip
```

`data/`, `*.gzip`, `*.zip`, `kaggle.json` e `.env*` são ignorados. Confirme com:

```bash
git check-ignore data/raw/Loan_status_2007-2020Q3.gzip
```

Credenciais Kaggle devem permanecer na configuração do usuário ou na sessão temporária do Colab. O notebook não baixa dados automaticamente.

## Aquisição

Com a CLI Kaggle autenticada fora do repositório:

```bash
mkdir -p data/raw
kaggle datasets download \
  -d ethon0426/lending-club-20072020q1 \
  -p data/raw
unzip -n data/raw/lending-club-20072020q1.zip \
  Loan_status_2007-2020Q3.gzip \
  -d data/raw
```

Se o download for manual, preserve o nome publicado e valide o hash. Uma republicação no mesmo slug deve ser tratada como fonte nova até que hash, shape e período sejam confirmados.

## Resolução do caminho

O pipeline usa esta precedência:

1. `--dataset` ou `DataPipelineConfig.dataset_path`;
2. variável `LENDING_CLUB_DATA_PATH`;
3. descoberta de exatamente um arquivo compatível em `data/raw/`.

São aceitos `.csv`, `.gz`, `.gzip` e `.zip`. Caminho ausente, formato incompatível ou múltiplos candidatos produzem erro antes do processamento caro. ZIPs com múltiplos membros devem ser extraídos previamente.

## Contrato de esquema

O cabeçalho completo é inspecionado antes da leitura dos registros. O pipeline exige 51 colunas, união das necessidades da EDA, PoC 1 e PoC 2. O contrato compartilhado da modelagem está em `src/tcc_reconstruction/schema.py`; `data.py` acrescenta somente colunas específicas das fases anteriores.

Tipos textuais são declarados explicitamente para identificadores, categorias, taxa e datas. Demais colunas são lidas com tipos inferidos pelo pandas e convertidas de maneira controlada. Todas as colunas ausentes são listadas em uma única falha legível.

## Ordem das operações

Cada bloco segue esta sequência:

1. leitura somente das 51 colunas necessárias;
2. contagem das linhas brutas;
3. filtro para `Fully Paid`, `Charged Off` e `Default`;
4. contagem por `verification_status`;
5. filtro padrão para `Verified` e `Source Verified`;
6. conversão de `int_rate` para percentual numérico;
7. conversão de `issue_d` e derivação de `year`;
8. conversão dos limites FICO e derivação de `fico`;
9. contagem de ausências e erros;
10. retenção determinística da amostra solicitada.

Falhas de conversão em valores originalmente não nulos encerram por padrão. O modo tolerante precisa ser solicitado explicitamente e registra os erros como ausências. Nenhuma imputação, codificação, divisão, seleção ou reamostragem ocorre nessa fase.

## FICO e valores ausentes

A reconstrução define:

```text
fico = (fico_range_low + fico_range_high) / 2
```

Se um limite estiver ausente, `fico` permanece ausente. A hipótese é explícita porque o notebook recuperado usa `fico` sem criá-la. Colunas com ausência ≥ 90% são sinalizadas, não removidas; a execução real não encontrou nenhuma entre as 51 selecionadas.

## Amostragem e memória

O padrão usa blocos de 100.000 linhas e retém 10.000 registros com semente 42. A prioridade combina identificador, posição global e semente por hash, tornando a seleção independente do tamanho dos blocos. A amostra limita memória e renderização, mas os contadores do manifesto percorrem o arquivo completo.

`--sample-size 0` carrega todos os 1.272.273 registros filtrados e deve ser usado somente com memória suficiente. Para desenvolvimento, mantenha a amostra padrão.

## Uso pela CLI

```bash
python scripts/prepare_dataset.py \
  --dataset data/raw/Loan_status_2007-2020Q3.gzip \
  --sample-size 10000 \
  --seed 42 \
  --hash-source
```

O hash completo exige uma segunda leitura do arquivo. A saída JSON contém apenas manifesto, contagens e estatísticas agregadas; não inclui linhas ou caminho absoluto.

## Uso pela API

```python
from tcc_reconstruction import DataPipelineConfig, run_data_pipeline

result = run_data_pipeline(
    DataPipelineConfig(
        dataset_path="data/raw/Loan_status_2007-2020Q3.gzip",
        sample_size=10_000,
        random_seed=42,
    )
)

frame = result.frame
summary = result.summary.to_dict()
manifest = result.manifest
```

## Resultado validado

| Etapa | Registros |
|---|---:|
| bruto | 2.925.493 |
| status finais | 1.860.764 |
| renda verificada | 1.272.273 |
| amostra padrão | 10.000 |

Status finais: 1.497.783 `Fully Paid`, 362.548 `Charged Off` e 433 `Default`. Após o filtro de renda: 734.249 `Source Verified` e 538.024 `Verified`; 588.491 `Not Verified` foram excluídos. Não houve conversão inválida na execução validada.

O manifesto agregado versionado está em `provenance/dataset-manifest.json`. Execute `make test` e `make validate` após alterações no pipeline.
