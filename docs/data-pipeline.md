# Pipeline de dados — Fase 2

## Escopo e proveniência

O pipeline em `src/tcc_reconstruction/data.py` é código **novo de reconstrução**, guiado pela tese e pelas células 6–8 e 26–51 do notebook recuperado. Ele corrige caminhos absolutos, acesso a colunas removidas e ajustes feitos antes do split, mas não antecipa imputação, codificação ou modelagem das fases seguintes.

O dataset completo permanece externo ao Git. A implementação foi validada com fixtures sintéticas e com uma leitura integral do arquivo real; somente hashes, esquema e contagens agregadas foram versionados em `provenance/dataset-manifest.json`.

## Resolução do arquivo

Ordem determinística:

1. `DataPipelineConfig(dataset_path=...)` ou `--dataset`;
2. variável `LENDING_CLUB_DATA_PATH`;
3. exatamente um arquivo em `data/raw/`.

Extensões aceitas: `.csv`, `.gz`, `.gzip` e `.zip`. A compressão efetiva é identificada pela assinatura binária, pois o arquivo real tem extensão `.gzip`, mas conteúdo CSV sem compressão. Arquivo ausente, formato não suportado ou múltiplos candidatos produzem erro legível antes do processamento. O ZIP publicado possui dois membros e precisa ser extraído antes da leitura.

## Contrato de esquema

O cabeçalho é lido isoladamente e validado antes da leitura completa. As 51 colunas exigidas são a união de:

- identificadores, datas, status e valores financeiros básicos;
- variáveis das Figuras 9–19;
- `annual_inc`, `all_util`, `acc_open_past_24mths` e `grade` da PoC 1;
- as 43 variáveis originais documentadas para a PoC 2;
- `fico_range_low` e `fico_range_high`, necessários para construir `fico`.

A lista executável e ordenável está em `REQUIRED_COLUMNS`. A mensagem de erro apresenta todas as colunas ausentes, evitando uma sequência de `KeyError` durante a limpeza.

## Ordem das operações

Para cada bloco:

1. ler apenas as 51 colunas requeridas;
2. contar os status originais;
3. manter `Fully Paid`, `Charged Off` e `Default`;
4. contar os status de verificação após o filtro de empréstimo;
5. por padrão, manter `Verified` e `Source Verified`;
6. converter `int_rate`, removendo `%` quando existir;
7. converter `issue_d` em data e derivar `year`;
8. converter os limites FICO e derivar `fico`;
9. contabilizar ausências, memória e intervalo de anos;
10. atualizar a amostra ou acumular o resultado completo solicitado.

Conversões inválidas de valores originalmente não nulos interrompem a execução por padrão. `--allow-conversion-errors` converte esses casos em ausentes e registra as quantidades no resumo.

## Definição de FICO

```text
fico = (fico_range_low + fico_range_high) / 2
```

Essa é uma decisão explícita da reconstrução porque o notebook usa `fico` sem criá-la e o Anexo A solicita que sua relação com os limites seja especificada. Se qualquer limite estiver ausente, `fico` também permanece ausente. A hipótese deverá ser reavaliada caso o dataset real contenha uma coluna `fico` independente ou documentação diferente.

## Valores ausentes

Esta fase não remove colunas nem imputa valores. O resumo apresenta, após os filtros:

- quantidade e percentual ausente por coluna;
- candidatas com ausência maior ou igual a 90%;
- falhas de conversão separadas de ausências originais.

A decisão evita repetir o fluxo recuperado que remove `max_bal_bc` e depois tenta preenchê-la. Imputação e seleção serão ajustadas somente com dados de treino na Fase 5.

## Amostragem determinística

A CLI usa 10.000 linhas e semente 42 por padrão. Cada linha recebe uma prioridade por hash de:

- `id`;
- posição original no arquivo;
- semente.

Somente as menores prioridades são mantidas. O resultado não depende do tamanho dos blocos, conforme teste com chunks de 7 e 13 linhas. Essa abordagem percorre o arquivo inteiro para produzir contagens globais, mas limita a memória ocupada pelos registros retornados.

`--sample-size 0` solicita todos os registros filtrados em memória e deve ser usado somente em máquinas dimensionadas para o dataset.

## Manifesto e resumo

A CLI não imprime linhas. Sua saída JSON contém:

- nome, tamanho, data de modificação, colunas e slug da fonte;
- aviso sobre a divergência Q1/Q3;
- SHA-256 quando solicitado;
- linhas antes/depois dos filtros;
- contagens de status e verificação;
- memória estimada dos blocos e resultado;
- erros de conversão;
- período mensal do arquivo bruto e intervalo de anos após os filtros;
- ausências e colunas candidatas ao limiar de 90%;
- configuração de amostragem.

O caminho absoluto é deliberadamente omitido do manifesto.

## Resultado no dataset real

A execução de 4 de agosto de 2026 confirmou:

- 2.925.493 linhas e 142 colunas no arquivo bruto;
- período bruto de junho de 2007 a setembro de 2020, confirmando Q3;
- 1.860.764 linhas após o filtro de status;
- 1.272.273 linhas após o filtro de renda verificada;
- 10.000 linhas na amostra determinística de semente 42;
- nenhuma falha de conversão e nenhuma das 51 colunas selecionadas com ausência ≥ 90% após os filtros.

O resumo separa `source_issue_month` (arquivo bruto) de `issue_year` (população depois dos dois filtros). Todas as contagens e hashes estão no manifesto versionado.

## Uso pela linha de comando

```bash
python scripts/prepare_dataset.py \
  --dataset data/raw/Loan_status_2007-2020Q3.gzip \
  --sample-size 10000 \
  --seed 42 \
  --chunk-size 100000 \
  --hash-source
```

Opções não padrão que alteram a população ou tolerância (`--include-unverified` e `--allow-conversion-errors`) ficam registradas no comando e, quando aplicável, no resumo.

## Uso pela API

```python
from tcc_reconstruction.data import DataPipelineConfig, run_data_pipeline

result = run_data_pipeline(
    DataPipelineConfig(
        dataset_path="data/raw/Loan_status_2007-2020Q3.gzip",
        sample_size=10_000,
        random_seed=42,
        include_source_hash=True,
    )
)

data = result.data
metadata = result.metadata_json()
```

O projeto é instalado em modo editável por `requirements.txt`; alterações em `src/` ficam disponíveis no ambiente sem reinstalação.

## Validação

```bash
python -m unittest discover -s tests -v
python scripts/verify_source_integrity.py
git diff --check
```

Os testes cobrem precedência de caminhos, ambiguidades, esquema incompleto, manifesto/hash, filtros, conversões, FICO, resumo, amostragem independente do chunk, modos estrito/tolerante, gzip verdadeiro, CSV com sufixo `.gzip` e saída da CLI sem linhas ou caminho absoluto.
