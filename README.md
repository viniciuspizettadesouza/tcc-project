# Reconstrução do TCC — recomendação de campanhas de crédito

Este repositório reúne as fontes e o planejamento para reconstruir, de forma rastreável e reproduzível, o notebook associado ao TCC **“Recomendação de campanha de crédito para perfis de clientes selecionados: utilizando técnicas de aprendizado de máquina e ciência de dados”**.

A reconstrução não deve ser apresentada como uma cópia byte a byte do notebook perdido. Ela será uma nova implementação baseada nas evidências disponíveis, com diferenças e resultados não reproduzidos explicitamente documentados.

## Estado atual

| Item esperado | Estado | Observação |
|---|---|---|
| Tese | presente | [`TCC_Vinicius_P_Souza.pdf`](TCC_Vinicius_P_Souza.pdf) |
| Notebook recuperado | presente e preservado | arquivo recebido: [`notebooks/Copy of Trabalho Data Mining.ipynb`](notebooks/Copy%20of%20Trabalho%20Data%20Mining.ipynb); cópia canônica: [`notebooks/original-recovered.ipynb`](notebooks/original-recovered.ipynb) |
| Dataset Lending Club | ausente, como esperado | não deve ser versionado |
| Notebook reconstruído | ainda não criado | destino futuro: `notebooks/tcc-reconstructed.ipynb` |
| Fundação reprodutível | preparada | dependências, manifesto e verificação de integridade disponíveis; pipeline de dados ainda não implementado |

O notebook recuperado contém evidência útil para a análise exploratória e para parte da PoC 2, mas não representa sozinho o trabalho final descrito na tese. A PoC 1, a regressão logística e a interpolação de taxas de juros, por exemplo, não estão implementadas nele.

## Documentação

- [`docs/reconstruction-analysis.md`](docs/reconstruction-analysis.md): inventário forense, matriz tese–notebook, lacunas e conflitos.
- [`docs/implementation-plan.md`](docs/implementation-plan.md): execução faseada, critérios de aceite e pontos de revisão.
- [`docs/dataset-acquisition.md`](docs/dataset-acquisition.md): obtenção e tratamento seguro do dataset externo.
- [`docs/result-comparison.md`](docs/result-comparison.md): contrato para comparar resultados reconstruídos com a tese.
- [`docs/phase-1-review.md`](docs/phase-1-review.md): entregas e evidências de validação da fundação.
- [`provenance/source-manifest.json`](provenance/source-manifest.json): hashes e tamanhos esperados das fontes protegidas.
- [`AGENTS.md`](AGENTS.md): regras operacionais para futuras sessões de implementação.

## Preparação local

### Pré-requisitos

- Git;
- Python 3.12;
- suporte a ambientes virtuais (`python3-venv` em Debian/Ubuntu);
- aproximadamente 3 GB livres apenas para ambiente e artefatos de trabalho, sem contar o dataset.

Prepare um ambiente isolado a partir da raiz do repositório:

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

## Preparação no Google Colab

Em uma sessão nova do Colab, clone o repositório e instale o mesmo arquivo de dependências:

```python
!git clone https://github.com/viniciuspizettadesouza/tcc-project.git
%cd tcc-project
!python -m pip install -r requirements.txt
!python scripts/verify_source_integrity.py
```

Depois, abra o notebook desejado pelo menu do Colab. Neste momento somente o notebook recuperado está disponível; `notebooks/tcc-reconstructed.ipynb` será criado em uma fase posterior.

O dataset e as credenciais Kaggle não fazem parte do clone. Siga [`docs/dataset-acquisition.md`](docs/dataset-acquisition.md) quando a Fase 2 for autorizada.

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

As Fases 0 e 1 cobrem investigação, planejamento e fundação do ambiente. Nenhum notebook reconstruído, pipeline ou modelo foi implementado ainda.
