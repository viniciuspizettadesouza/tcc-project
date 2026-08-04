# Reconstrução do TCC — recomendação de campanhas de crédito

Este repositório reúne as fontes e o planejamento para reconstruir, de forma rastreável e reproduzível, o notebook associado ao TCC **“Recomendação de campanha de crédito para perfis de clientes selecionados: utilizando técnicas de aprendizado de máquina e ciência de dados”**.

A reconstrução não deve ser apresentada como uma cópia byte a byte do notebook perdido. Ela será uma nova implementação baseada nas evidências disponíveis, com diferenças e resultados não reproduzidos explicitamente documentados.

## Estado atual

| Item esperado | Estado | Observação |
|---|---|---|
| Tese | presente | [`TCC_Vinicius_P_Souza.pdf`](TCC_Vinicius_P_Souza.pdf) |
| Notebook recuperado | presente e preservado | arquivo recebido: [`notebooks/Copy of Trabalho Data Mining.ipynb`](notebooks/Copy%20of%20Trabalho%20Data%20Mining.ipynb); cópia canônica: [`notebooks/original-recovered.ipynb`](notebooks/original-recovered.ipynb) |
| Dataset Lending Club | validado localmente | 2.925.493 × 142; permanece ignorado pelo Git |
| Notebook reconstruído | ainda não criado | destino futuro: `notebooks/tcc-reconstructed.ipynb` |
| Pipeline de dados | implementado e validado | execução integral registrada em [`provenance/dataset-manifest.json`](provenance/dataset-manifest.json) |

O notebook recuperado contém evidência útil para a análise exploratória e para parte da PoC 2, mas não representa sozinho o trabalho final descrito na tese. A PoC 1, a regressão logística e a interpolação de taxas de juros, por exemplo, não estão implementadas nele.

## Documentação

- [`docs/reconstruction-analysis.md`](docs/reconstruction-analysis.md): inventário forense, matriz tese–notebook, lacunas e conflitos.
- [`docs/implementation-plan.md`](docs/implementation-plan.md): execução faseada, critérios de aceite e pontos de revisão.
- [`docs/dataset-acquisition.md`](docs/dataset-acquisition.md): obtenção e tratamento seguro do dataset externo.
- [`docs/data-pipeline.md`](docs/data-pipeline.md): contrato, transformações e uso do pipeline da Fase 2.
- [`docs/result-comparison.md`](docs/result-comparison.md): contrato para comparar resultados reconstruídos com a tese.
- [`docs/phase-1-review.md`](docs/phase-1-review.md): entregas e evidências de validação da fundação.
- [`docs/phase-2-review.md`](docs/phase-2-review.md): entregas, testes e pendências do pipeline de dados.
- [`provenance/source-manifest.json`](provenance/source-manifest.json): hashes e tamanhos esperados das fontes protegidas.
- [`provenance/dataset-manifest.json`](provenance/dataset-manifest.json): identificação e contagens agregadas do dataset real, sem versionar seus registros.
- [`AGENTS.md`](AGENTS.md): regras operacionais para futuras sessões de implementação.

## Instalação local do projeto

### Pré-requisitos

- Git;
- Python 3.12;
- suporte a ambientes virtuais (`python3-venv` em Debian/Ubuntu);
- conta Kaggle com acesso ao dataset;
- pelo menos 4 GB livres para o ZIP e o CSV extraído, além do ambiente Python.

Clone o repositório e entre na pasta:

```bash
git clone https://github.com/viniciuspizettadesouza/tcc-project.git
cd tcc-project
```

Crie e prepare o ambiente isolado:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/verify_source_integrity.py
```

No Windows PowerShell, ative o ambiente com `.venv\Scripts\Activate.ps1`. No encerramento da sessão, use `deactivate`.

Para inspecionar os notebooks localmente:

```bash
python -m jupyter lab
```

O ambiente instala bibliotecas modernas para a reconstrução. Dependências exclusivas do artefato antigo, como `dexplot`, `jupyter-dash` e imports Dash obsoletos, não foram mantidas porque serão substituídas durante as fases de implementação.

Confirme que a CLI do Kaggle instalada pelo projeto está disponível e configure sua autenticação fora do repositório:

```bash
kaggle --version
```

Depois, baixe e extraia o dataset. O slug termina em `q1`, mas o arquivo publicado e validado contém dados até setembro de 2020 e se chama `Loan_status_2007-2020Q3.gzip`:

```bash
mkdir -p data/raw
kaggle datasets download \
  -d ethon0426/lending-club-20072020q1 \
  -p data/raw
unzip -n data/raw/lending-club-20072020q1.zip \
  Loan_status_2007-2020Q3.gzip \
  -d data/raw
git check-ignore data/raw/Loan_status_2007-2020Q3.gzip
```

Apesar da extensão `.gzip`, o membro publicado é um CSV sem compressão adicional. Não renomeie nem recomprima o arquivo: o pipeline detecta o formato pelo conteúdo. O último comando deve imprimir o caminho, confirmando que os dados não serão versionados.

Valide o arquivo local contra o manifesto reproduzido:

```bash
python scripts/prepare_dataset.py \
  --dataset data/raw/Loan_status_2007-2020Q3.gzip \
  --sample-size 10000 \
  --seed 42 \
  --hash-source
```

O SHA-256 esperado é `5878af2a088f8ab5214c9337289fb8b5eb6c6338fd3f417b6cdc18513dc6f`. Consulte [`docs/dataset-acquisition.md`](docs/dataset-acquisition.md) para autenticação, alternativa manual e proveniência completa.

## Preparação no Google Colab

Em uma sessão nova do Colab, clone o repositório e instale o mesmo arquivo de dependências:

```python
!git clone https://github.com/viniciuspizettadesouza/tcc-project.git
%cd tcc-project
!python -m pip install -r requirements.txt
!python scripts/verify_source_integrity.py
```

Depois, abra o notebook desejado pelo menu do Colab. Neste momento somente o notebook recuperado está disponível; `notebooks/tcc-reconstructed.ipynb` será criado em uma fase posterior.

O dataset e as credenciais Kaggle não fazem parte do clone. Siga [`docs/dataset-acquisition.md`](docs/dataset-acquisition.md) para disponibilizá-los somente na sessão do Colab.

## Pipeline de dados

Com o ambiente ativado, indique o dataset explicitamente:

```bash
python scripts/prepare_dataset.py \
  --dataset data/raw/Loan_status_2007-2020Q3.gzip \
  --sample-size 10000 \
  --seed 42 \
  --hash-source
```

O caminho também pode ser definido por `LENDING_CLUB_DATA_PATH`. Sem argumento ou variável, a ferramenta aceita exatamente um arquivo suportado em `data/raw/`. A ordem de precedência é: argumento, variável de ambiente e descoberta em `data/raw/`.

A CLI percorre o arquivo em blocos, mantém apenas uma amostra determinística em memória e imprime somente manifesto, contagens e estatísticas de pré-processamento em JSON — nenhuma linha do dataset é exibida. O hash completo é opcional porque exige uma segunda leitura do arquivo de vários gigabytes.

Use `--sample-size 0` somente quando houver memória suficiente para manter todos os registros filtrados. Consulte [`docs/data-pipeline.md`](docs/data-pipeline.md) para as decisões e limitações.

Execute os testes sintéticos com:

```bash
python -m unittest discover -s tests -v
```

## Verificação das fontes

Execute antes e depois de qualquer fase:

```bash
python scripts/verify_source_integrity.py
```

A verificação compara SHA-256, tamanho e equivalência byte a byte entre o arquivo recebido e a cópia canônica. Alterações nas fontes protegidas fazem o comando terminar com código diferente de zero.

## Fontes de verdade e prioridade

1. A tese define a metodologia e os resultados finais pretendidos.
2. O notebook recuperado é evidência de implementação e de proveniência, não uma fonte automaticamente correta.
3. Execuções reproduzíveis determinam o que pode ser afirmado sobre a reconstrução.
4. Quando as fontes conflitarem, o conflito deve permanecer visível; nenhum número deve ser ajustado manualmente para coincidir com o PDF.

## Fluxo de trabalho

O trabalho deve avançar uma fase por vez. Ao final de cada fase: executar as validações previstas, revisar o diff, atualizar a comparação de resultados e solicitar aprovação. O commit da fase só deve ser criado após essa aprovação.

As Fases 0 e 1 cobrem investigação, planejamento e fundação do ambiente. A Fase 2 implementa e valida o pipeline com o dataset externo, sem versioná-lo. Nenhum notebook reconstruído ou modelo foi implementado.
