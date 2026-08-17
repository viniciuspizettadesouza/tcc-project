# TCC — recomendação de campanhas de crédito

Reconstrução rastreável do notebook associado ao TCC **“Recomendação de
campanha de crédito para perfis de clientes selecionados”**, seguida de uma
trilha evolutiva independente.

## Estado atual

| Artefato | Papel |
|---|---|
| [`TCC_Vinicius_P_Souza.pdf`](TCC_Vinicius_P_Souza.pdf) | fonte metodológica primária |
| [`notebooks/tcc-recovered-from-colab.ipynb`](notebooks/tcc-recovered-from-colab.ipynb) | artefato parcial recuperado após a perda do original |
| [`notebooks/tcc-reconstructed.ipynb`](notebooks/tcc-reconstructed.ipynb) | reconstrução histórica imutável das Fases 0–8 |
| [`notebooks/tcc-evolved.ipynb`](notebooks/tcc-evolved.ipynb) | notebook ativo, com E0–E5 concluídas |

Os dois notebooks históricos são protegidos por SHA-256 e nunca são executados
in-place. Resultados evolutivos não são atribuídos ao TCC original.

## Documentação

- [`docs/reconstruction-analysis.md`](docs/reconstruction-analysis.md): investigação forense e conflitos das fontes.
- [`docs/reconstruction-history.md`](docs/reconstruction-history.md): decisões e commits das Fases 0–8.
- [`docs/final-validation.md`](docs/final-validation.md): evidência final da reconstrução.
- [`docs/result-comparison.md`](docs/result-comparison.md): tese versus reconstrução.
- [`docs/data-guide.md`](docs/data-guide.md): aquisição e contrato do dataset.
- [`docs/maintenance.md`](docs/maintenance.md): operação e manutenção.
- [`docs/evolution-scope.md`](docs/evolution-scope.md): target e disponibilidade dos atributos.
- [`docs/evolution-results.md`](docs/evolution-results.md): resultados posteriores à reconstrução.
- [`docs/evolution-history.md`](docs/evolution-history.md): linha do tempo E0–E5.
- [`provenance/source-manifest.json`](provenance/source-manifest.json) e [`provenance/dataset-manifest.json`](provenance/dataset-manifest.json): proveniência sem dados individuais.
- [`AGENTS.md`](AGENTS.md): regras para futuras alterações.

## Instalação local do projeto

Requer Python 3.12, Git e, opcionalmente, GNU Make.

```bash
git clone https://github.com/viniciuspizettadesouza/tcc-project.git
cd tcc-project
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/verify_source_integrity.py
```

No PowerShell, ative o ambiente com `.venv\Scripts\Activate.ps1`.

## Comandos padronizados

```bash
make test          # suíte automatizada
make validate      # integridade, notebooks, dependências e diff
make notebook      # executa somente o notebook evolutivo
make export        # HTML evolutivo local e auditado
make validate-html # audita uma exportação existente
```

Os equivalentes centrais sem Make são:

```bash
python -m unittest discover -s tests -v
python scripts/verify_source_integrity.py
python scripts/validate_final_reconstruction.py
python -m scripts.validate_evolved_notebook
```

Nenhum comando padrão baixa dados, cria commit ou publica artefatos.

## Dataset

O arquivo validado é `Loan_status_2007-2020Q3.gzip` (2.925.493 × 142), SHA-256
`5878af2a088f8ab5214c9337289fb8b5eb6c6338fd3f417b6cdc18513dc6f`. Ele deve
permanecer em `data/raw/`, ignorado pelo Git. Aquisição manual, Kaggle,
validação de esquema e amostragem estão em [`docs/data-guide.md`](docs/data-guide.md).

```bash
mkdir -p data/raw
kaggle datasets download -d ethon0426/lending-club-20072020q1 -p data/raw
unzip -n data/raw/lending-club-20072020q1.zip \
  Loan_status_2007-2020Q3.gzip -d data/raw
python scripts/prepare_dataset.py \
  --dataset data/raw/Loan_status_2007-2020Q3.gzip
```

## Execução local completa

```bash
LENDING_CLUB_DATA_PATH="$PWD/data/raw/Loan_status_2007-2020Q3.gzip" \
  make notebook
make validate
```

O alvo inicia kernel novo e grava somente
`notebooks/tcc-evolved.ipynb`. A execução completa pode exigir vários
gigabytes de memória. Para auditar a reconstrução, `make
reproduce-reconstructed` usa uma cópia temporária descartável.

Sem Make, o comando de execução é:

```bash
LENDING_CLUB_DATA_PATH="$PWD/data/raw/Loan_status_2007-2020Q3.gzip" \
python -m jupyter nbconvert --to notebook --execute --inplace \
  notebooks/tcc-evolved.ipynb --ExecutePreprocessor.timeout=1800
```

## Execução no Google Colab

Clone o repositório, instale `requirements.txt`, obtenha o dataset conforme
`docs/data-guide.md` e execute:

```python
import os
from pathlib import Path

os.environ["LENDING_CLUB_DATA_PATH"] = str(
    (Path.cwd() / "data/raw/Loan_status_2007-2020Q3.gzip").resolve()
)
!python scripts/verify_source_integrity.py
!python -m jupyter nbconvert --to notebook --execute --inplace \
  notebooks/tcc-evolved.ipynb --ExecutePreprocessor.timeout=1800
!python -m scripts.validate_evolved_notebook
```

Credenciais Kaggle existem somente na sessão e nunca entram no repositório.

## Limites

A reconstrução é reproduzível, não uma cópia byte a byte da execução perdida.
A evolução melhora o momento de inferência, calibração, validação temporal e
segmentação, mas não valida impacto financeiro, fairness regulatória, adesão
comercial ou adequação ao mercado brasileiro. Consulte os documentos de
resultados para as evidências e restrições completas.
