# Guia de manutenção

## Escopo

Este guia descreve como manter e validar a reconstrução sem alterar silenciosamente metodologia, populações ou resultados. A tese e o notebook recuperado são fontes protegidas; mudanças científicas ou novos experimentos devem usar um plano separado.

## Organização dos módulos

| Módulo | Responsabilidade | Limite de responsabilidade |
|---|---|---|
| `src/tcc_reconstruction/__init__.py` | expõe a API pública do pipeline de dados | não reúne automaticamente as APIs das fases analíticas |
| `src/tcc_reconstruction/data.py` | resolve o caminho, valida o esquema, lê em blocos, filtra, converte, amostra e produz manifestos agregados | não imputa, codifica, balanceia nem treina modelos |
| `src/tcc_reconstruction/eda.py` | calcula correlações, seleciona inadimplentes, limita amostras de gráficos, aplica `log1p` e produz perfis agregados | não prepara atributos para modelagem nem expõe linhas individuais |
| `src/tcc_reconstruction/poc1.py` | implementa elegibilidade, distância Euclidiana bruta, análise normalizada e reprodução da Tabela 7 | a análise normalizada é sensibilidade; não substitui silenciosamente a regra histórica |
| `src/tcc_reconstruction/poc2.py` | prepara alvo e atributos, cria pipelines sem vazamento e avalia regressão logística e XGBoost | transformadores e balanceamento devem continuar ajustados somente no treino |
| `src/tcc_reconstruction/score.py` | calibra probabilidades, diferencia score de risco e de crédito, categoriza A–G e interpola a oferta evidenciada | somente a categoria B possui faixa de juros publicada; taxas para outras categorias não devem ser inventadas |
| `src/tcc_reconstruction/schema.py` | mantém o contrato compartilhado de atributos da PoC 2 e sua correspondência com colunas brutas | não executa transformações nem importa bibliotecas de modelagem |

O notebook reconstruído coordena esses módulos e contém a narrativa, as visualizações e os resultados salvos. Código reutilizável deve permanecer nos módulos; células devem se concentrar na sequência analítica e na apresentação das evidências.

## Sequência recomendada

Na raiz do repositório, com o ambiente virtual ativado:

1. Execute `make test` para a suíte sintética e estrutural.
2. Execute `make validate` para integridade das fontes, auditoria do notebook, dependências e whitespace.
3. Quando uma mudança exigir dados reais, valide primeiro o arquivo com `scripts/prepare_dataset.py`.
4. Execute `make notebook` somente depois de definir `LENDING_CLUB_DATA_PATH`.
5. Repita `make test` e `make validate` após a execução.
6. Revise `git status`, `git diff` e `docs/result-comparison.md` antes de solicitar aprovação.

Os equivalentes sem GNU Make são:

```bash
python -m unittest discover -s tests -v
python scripts/verify_source_integrity.py
python scripts/validate_final_reconstruction.py
python -m pip check
git diff --check
```

## Verificações sem dataset

As seguintes verificações não leem o dataset externo e são as mesmas executadas pela CI:

- `make test`;
- `make validate`;
- validação do YAML e dos contratos do `Makefile` incluída na suíte de testes;
- inspeção dos outputs já salvos no notebook reconstruído;
- auditoria de datasets, credenciais e modelos entre arquivos candidatos ao Git.

A CI não executa `scripts/prepare_dataset.py`, `make notebook` nem `make export`. Ela não precisa de credenciais Kaggle ou de `LENDING_CLUB_DATA_PATH`.

Depois de uma exportação local, `make validate-html` audita `artifacts/html/tcc-reconstructed.html`. O validador exige que o arquivo permaneça ignorado pelo Git, rejeita caminhos absolutos, referências a credenciais e tabelas com identificadores individuais, e emite tamanho e SHA-256 para conferência local.

## Operações que exigem o dataset

A validação do arquivo real e a execução integral do notebook exigem o dataset local ignorado pelo Git. Use o comando canônico de `scripts/prepare_dataset.py` na seção **Pipeline de dados** do `README.md` antes de processamento custoso. Depois, defina `LENDING_CLUB_DATA_PATH` e execute `make notebook`, conforme **Comandos padronizados**. A execução atualiza os outputs de `notebooks/tcc-reconstructed.ipynb`; revise o diff e confirme que nenhuma alteração metodológica ou caminho local foi gravado.

## Execução no Google Colab

No Colab, clone o repositório, instale `requirements.txt`, obtenha o dataset conforme `docs/data-guide.md` e defina `LENDING_CLUB_DATA_PATH` somente no ambiente da sessão. Credenciais Kaggle também devem existir somente nessa sessão. O bloco executável canônico permanece na seção **Execução no Google Colab** do `README.md`, evitando duas cópias das mesmas instruções.

## Solução de problemas

### Memória insuficiente

- Use amostra determinística de 10.000 para desenvolvimento e validação do pipeline.
- Não use `--sample-size 0` sem memória suficiente para os registros filtrados.
- Feche outros kernels e processos antes da execução integral.
- No Colab, selecione uma sessão com memória ampliada quando disponível.
- Uma interrupção por falta de memória não autoriza reduzir silenciosamente a população da execução final; registre qualquer adaptação.

### Caminho do dataset

- Confirme com `test -f "$LENDING_CLUB_DATA_PATH"` que a variável aponta para um arquivo existente.
- Prefira `data/raw/Loan_status_2007-2020Q3.gzip`; o diretório já é ignorado pelo Git.
- A extensão `.gzip` do arquivo publicado é histórica: o pipeline detecta o formato pelo conteúdo.
- Sem variável ou argumento, a descoberta automática exige exatamente um arquivo compatível em `data/raw/`.
- Nunca grave caminho local absoluto no notebook, código ou documentação versionada.

### Kernel Jupyter

- Ative o ambiente virtual antes de iniciar Jupyter ou executar `make notebook`.
- Confirme que o kernel selecionado usa Python 3.12 e as dependências de `requirements.txt`.
- Reinicie o kernel e execute todas as células quando houver suspeita de estado oculto.
- Para execução longa, mantenha o timeout de 1.800 segundos ou registre justificativa para alterá-lo.
- Se o kernel falhar ao iniciar, execute `python -m pip check` e confirme que `ipykernel` e `jupyterlab` pertencem ao ambiente ativo.

## Limitações e resultados irreproduzíveis

As limitações continuam parte do baseline e não devem ser removidas para apresentar uma equivalência histórica inexistente:

- a amostra histórica de 10.000 da PoC 1 não pode ser identificada exatamente;
- a execução histórica final da PoC 2 não preserva outputs ou versões suficientes;
- não há validação temporal, regulatória, de fairness ou de impacto financeiro;
- `int_rate` e `sub_grade` podem introduzir circularidade em um cenário pré-oferta;
- apenas a categoria B possui evidência para interpolação de juros;
- categorias extremas têm suporte insuficiente para conclusões robustas.

Consulte `docs/final-validation.md` para limitações e itens irreproduzíveis, e `docs/result-comparison.md` para a classificação completa das diferenças em relação à tese.

## Regras para alterações futuras

- Execute integridade antes e depois de cada etapa.
- Preserve `notebooks/tcc-recovered-from-colab.ipynb` byte a byte.
- Não versione dataset, credenciais, modelos binários ou HTML exportado.
- Atualize testes e documentação quando um contrato público mudar.
- Registre divergências científicas em `docs/result-comparison.md`.
- Pare para revisão antes de commit, tag, push, release ou publicação.

## Histórico do fortalecimento

O plano de continuidade posterior à reconstrução foi executado em 4–5 de agosto de 2026 sobre o baseline científico `84eeb04`. Nenhuma metodologia, população, métrica ou output versionado foi alterado.

| Etapa | Resultado |
|---:|---|
| 1 | baseline e fontes protegidas confirmados |
| 2 | CI em Python 3.12, somente leitura e sem dataset |
| 3 | comandos locais centralizados no `Makefile` |
| 4 | módulos, sequência operacional e troubleshooting documentados |
| 5 | contratos da CI/Makefile, integridade e segurança do HTML cobertos por testes |
| 6 | HTML completo gerado e auditado somente em diretório ignorado |
| 7 | execução integral, deduplicação e revisão final concluídas |

O fortalecimento centralizou o contrato da PoC 2 em `src/tcc_reconstruction/schema.py`, substituiu laços de SHA-256 por `hashlib.file_digest`, removeu uma asserção literal repetida e consolidou comandos duplicados do README. O plano prospectivo e seus documentos intermediários foram removidos após este registro; o Git preserva o histórico integral.

Ruff 0.16.1 foi avaliado sem ser adicionado às dependências. A base anterior exigiria ajustes mecânicos sem benefício proporcional; os arquivos alterados no encerramento passaram em lint e formatação, e o notebook recuperado permaneceu fora da ferramenta.

## Artefato HTML local

`make export` incorpora offline a saída Plotly, grava `artifacts/html/tcc-reconstructed.html` e executa a auditoria de segurança. Registro da execução final:

| Campo | Valor |
|---|---|
| tamanho | 6.328.127 bytes |
| SHA-256 | `fe107c6d780ebd948a0ba3c3a8f9f185c3190c229027bac67c5fb6e3af1c0648` |
| saídas Plotly incorporadas | 1 |
| caminhos absolutos | 0 |
| tabelas com identificadores individuais | 0 |
| ignorado pelo Git | sim |

O hash identifica somente essa exportação local e pode variar com o gerador ou ambiente. O HTML não foi anexado, versionado ou publicado.

## Evidência de encerramento

- 79 testes aprovados;
- nova execução integral temporária com 39/39 células, zero erros, 20 PNG e uma Plotly;
- PDF e notebook recuperado aprovados por tamanho e SHA-256;
- 30 comparações com a tese classificadas, sem pendências;
- `pip check`, Ruff dos arquivos alterados e `git diff --check` aprovados;
- nenhum corpo de função ou bloco normalizado de seis linhas duplicado em `src/`/`scripts/`;
- nenhum parágrafo longo exatamente duplicado entre README e documentação consolidada;
- nenhum dataset, segredo, modelo binário ou HTML candidato ao Git;
- nenhuma tag, release, publicação ou ação remota criada.
