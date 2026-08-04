# Reconstrução do TCC — recomendação de campanhas de crédito

Este repositório reúne as fontes, a implementação e as evidências de validação da reconstrução rastreável do notebook associado ao TCC **“Recomendação de campanha de crédito para perfis de clientes selecionados: utilizando técnicas de aprendizado de máquina e ciência de dados”**.

A reconstrução não é apresentada como cópia byte a byte do notebook perdido. Ela é uma nova implementação baseada nas evidências disponíveis, com diferenças e resultados irreproduzíveis explicitamente documentados.

## Estado atual

| Item esperado | Estado | Observação |
|---|---|---|
| Tese | presente | [`TCC_Vinicius_P_Souza.pdf`](TCC_Vinicius_P_Souza.pdf) |
| Artefato do TCC recuperado do Colab | presente e preservado | [`notebooks/tcc-recovered-from-colab.ipynb`](notebooks/tcc-recovered-from-colab.ipynb); recebido originalmente como `Copy of Trabalho Data Mining.ipynb` após a perda do notebook original durante manutenção do Google Colab |
| Dataset Lending Club | validado localmente | 2.925.493 × 142; permanece ignorado pelo Git |
| Notebook reconstruído | implementado e executado | [`notebooks/tcc-reconstructed.ipynb`](notebooks/tcc-reconstructed.ipynb); duas PoCs, Figuras 9–29, Tabelas 3–9, resultados e proveniência |
| Pipeline de dados | implementado e validado | execução integral registrada em [`provenance/dataset-manifest.json`](provenance/dataset-manifest.json) |
| Comparação com a tese | preenchida | resultados classificados em [`docs/result-comparison.md`](docs/result-comparison.md) |
| Validação automatizada | disponível | testes unitários, integridade das fontes e auditoria final do notebook; Fases 0–8 concluídas |

O notebook original do TCC armazenado no Google Colab foi perdido durante uma manutenção da plataforma. O artefato posteriormente recuperado contém evidência útil para a análise exploratória e para parte da PoC 2, mas não representa sozinho todo o trabalho final descrito na tese. A PoC 1, a regressão logística e a interpolação de taxas de juros, por exemplo, não estão implementadas nele. `tcc-reconstructed.ipynb` é o novo notebook criado pelas etapas documentadas de reconstrução.

## Documentação

- [`docs/reconstruction-analysis.md`](docs/reconstruction-analysis.md): inventário forense, matriz tese–notebook, lacunas e conflitos.
- [`docs/implementation-plan.md`](docs/implementation-plan.md): execução faseada, critérios de aceite e pontos de revisão.
- [`docs/dataset-acquisition.md`](docs/dataset-acquisition.md): obtenção e tratamento seguro do dataset externo.
- [`docs/data-pipeline.md`](docs/data-pipeline.md): contrato, transformações e uso do pipeline da Fase 2.
- [`docs/result-comparison.md`](docs/result-comparison.md): contrato para comparar resultados reconstruídos com a tese.
- [`docs/phase-1-review.md`](docs/phase-1-review.md): entregas e evidências de validação da fundação.
- [`docs/phase-2-review.md`](docs/phase-2-review.md): entregas, testes e pendências do pipeline de dados.
- [`docs/phase-3-review.md`](docs/phase-3-review.md): EDA e Figuras 9–19.
- [`docs/phase-4-review.md`](docs/phase-4-review.md): PoC 1, Tabela 7 e Figuras 20–22.
- [`docs/phase-5-review.md`](docs/phase-5-review.md): regressão logística, XGBoost e Figuras 23–25.
- [`docs/phase-6-review.md`](docs/phase-6-review.md): calibração, score, taxa e Figuras 26–29.
- [`docs/phase-7-review.md`](docs/phase-7-review.md): organização narrativa do notebook.
- [`docs/final-validation.md`](docs/final-validation.md): validação integral, limitações e itens irreproduzíveis.
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

Para abrir o notebook reconstruído localmente:

```bash
python -m jupyter lab
```

Selecione `notebooks/tcc-reconstructed.ipynb`. O ambiente usa substituições mantidas para dependências antigas como `dexplot`, `jupyter-dash` e APIs removidas do scikit-learn/seaborn.

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

## Execução local completa

Com o dataset em `data/raw/`, execute primeiro todas as verificações rápidas:

```bash
python scripts/verify_source_integrity.py
python scripts/validate_final_reconstruction.py
python -m unittest discover -s tests -v
```

Para executar o notebook inteiro em um kernel novo e atualizar seus outputs:

```bash
LENDING_CLUB_DATA_PATH="$PWD/data/raw/Loan_status_2007-2020Q3.gzip" \
python -m jupyter nbconvert \
  --to notebook \
  --execute \
  --inplace notebooks/tcc-reconstructed.ipynb \
  --ExecutePreprocessor.timeout=1800
```

O caminho vem da variável de ambiente e não é gravado no notebook. A execução integral carrega até 1.272.273 registros para modelagem e pode exigir vários gigabytes de memória; feche outros processos ou use uma máquina com memória suficiente.

No Windows PowerShell, a forma equivalente é:

```powershell
$env:LENDING_CLUB_DATA_PATH = (Resolve-Path "data/raw/Loan_status_2007-2020Q3.gzip").Path
python -m jupyter nbconvert --to notebook --execute --inplace notebooks/tcc-reconstructed.ipynb --ExecutePreprocessor.timeout=1800
```

## Execução no Google Colab

Em uma sessão nova do Colab, clone o repositório e instale o mesmo arquivo de dependências:

```python
!git clone https://github.com/viniciuspizettadesouza/tcc-project.git
%cd tcc-project
!python -m pip install -r requirements.txt
!python scripts/verify_source_integrity.py
```

Configure a autenticação do Kaggle somente na sessão do Colab, conforme a documentação oficial da plataforma, e nunca adicione `kaggle.json` ao repositório. Baixe e extraia o arquivo validado:

```python
!mkdir -p data/raw
!kaggle datasets download \
  -d ethon0426/lending-club-20072020q1 \
  -p data/raw
!unzip -n data/raw/lending-club-20072020q1.zip \
  Loan_status_2007-2020Q3.gzip \
  -d data/raw
!git check-ignore data/raw/Loan_status_2007-2020Q3.gzip
```

Valide as fontes e o arquivo antes da execução:

```python
!python scripts/verify_source_integrity.py
!python scripts/prepare_dataset.py \
  --dataset data/raw/Loan_status_2007-2020Q3.gzip \
  --sample-size 10000 \
  --seed 42 \
  --hash-source
!python scripts/validate_final_reconstruction.py
```

Abra `notebooks/tcc-reconstructed.ipynb` pela interface do Colab ou execute-o em um kernel novo:

```python
import os
from pathlib import Path

os.environ["LENDING_CLUB_DATA_PATH"] = str(
    (Path.cwd() / "data/raw/Loan_status_2007-2020Q3.gzip").resolve()
)
!python -m jupyter nbconvert \
  --to notebook \
  --execute \
  --inplace notebooks/tcc-reconstructed.ipynb \
  --ExecutePreprocessor.timeout=1800
```

Uma sessão com memória ampliada pode ser necessária. O notebook não baixa dados automaticamente e não contém credenciais.

O dataset e as credenciais Kaggle não fazem parte do clone. Siga [`docs/dataset-acquisition.md`](docs/dataset-acquisition.md) para alternativas de aquisição e verificação do hash.

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

Execute também a auditoria estrutural do notebook e dos arquivos rastreados:

```bash
python scripts/validate_final_reconstruction.py
```

## Verificação das fontes

Execute antes e depois de qualquer fase:

```bash
python scripts/verify_source_integrity.py
```

A verificação compara o SHA-256 e o tamanho do artefato recuperado do Colab com o manifesto de proveniência. Alterações nas fontes protegidas fazem o comando terminar com código diferente de zero; o histórico Git fornece a trilha adicional de auditoria.

## Fontes de verdade e prioridade

1. A tese define a metodologia e os resultados finais pretendidos.
2. O notebook recuperado é evidência de implementação e de proveniência, não uma fonte automaticamente correta.
3. Execuções reproduzíveis determinam o que pode ser afirmado sobre a reconstrução.
4. Quando as fontes conflitarem, o conflito deve permanecer visível; nenhum número deve ser ajustado manualmente para coincidir com o PDF.

## Fluxo de trabalho

O trabalho deve avançar uma fase por vez. Ao final de cada fase: executar as validações previstas, revisar o diff, atualizar a comparação de resultados e solicitar aprovação. O commit da fase só deve ser criado após essa aprovação.

As Fases 0–7 reconstruíram o pipeline, a EDA, as duas PoCs, o score e a narrativa. A Fase 8 validou a execução integral e encerrou a reconstrução. Todas as Fases 0–8 estão concluídas; o histórico e os commits de encerramento estão registrados em [`docs/implementation-plan.md`](docs/implementation-plan.md). Modelos permanecem apenas em memória durante a execução; nenhum binário é versionado.
