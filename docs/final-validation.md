# Validação final da reconstrução — Fase 8

Data da validação: 4 de agosto de 2026. Commit base: `6b0eca9`.

## Resultado

O notebook reconstruído foi executado integralmente em um kernel novo, do primeiro import à última figura, usando o dataset real validado. A execução terminou com código zero em 118,03 segundos e gravou os outputs no próprio notebook.

```text
84 células totais
45 células Markdown
39 células de código
39 células executadas em sequência (1–39)
0 outputs de erro
20 figuras PNG + 1 figura Plotly
```

O kernel novo prova que a ordem atual não depende de variáveis deixadas por uma sessão anterior. A variável `LENDING_CLUB_DATA_PATH` foi definida apenas no processo de execução; o caminho absoluto local não foi gravado no notebook.

## Ambiente validado

| Componente | Versão |
|---|---:|
| Python | 3.12.3 |
| NumPy | 2.5.1 |
| pandas | 2.3.3 |
| matplotlib | 3.11.1 |
| Plotly | 6.9.0 |
| seaborn | 0.13.2 |
| imbalanced-learn | 0.14.2 |
| scikit-learn | 1.9.0 |
| XGBoost | 3.4.0 |
| nbclient | 0.11.0 |
| nbformat | 5.10.4 |

As 14 dependências diretas de execução estão fixadas com `==` em `requirements.txt`. As sementes 42 e 1 permanecem registradas no notebook e nos módulos.

## Dataset e fontes

- dataset: `Loan_status_2007-2020Q3.gzip`, 2.925.493 × 142;
- SHA-256: `5878af2a088f8ab5214c9337289fb8b5eb6c6338fd3f417b6cdc18513dc6f`;
- população com status final: 1.860.764;
- população com status final e renda verificada: 1.272.273;
- PDF e artefato recuperado do TCC passaram na verificação de tamanho e hash.

O dataset completo continua ignorado pelo Git. A auditoria automática não encontrou dataset, credencial ou modelo binário entre arquivos rastreados ou candidatos a versionamento.

## Estrutura, outputs e legibilidade

`scripts/validate_final_reconstruction.py` verifica automaticamente:

- as 15 seções principais na ordem do plano e com declaração de tipo;
- presença das duas PoCs;
- execução sequencial completa e ausência de erros salvos;
- 20 outputs PNG e um output Plotly para as Figuras 9–29;
- títulos de todas as seções de figuras;
- dimensões explícitas, incluindo a matriz de confusão;
- eixos rotulados nas visualizações aplicáveis;
- sementes e referência às versões fixadas;
- ausência de caminhos locais absolutos e referência a credencial no notebook;
- ausência de datasets, credenciais e modelos serializados no conjunto candidato ao Git.

## Resultados confirmados na execução limpa

- PoC 1: amostra determinística de 10.000, com 36/10 aprovações pela regra completa e 64/88 pelo modo histórico somente por distância;
- regressão logística completa: AUC 0,704407;
- XGBoost completo: AUC 0,711818;
- XGBoost reduzido: AUC 0,706897;
- XGBoost reduzido calibrado: AUC 0,706847 e Brier 0,153092;
- score 750: categoria B e taxa reconstruída de 15,3925% a.a.;
- categorias calibradas: F com 4 registros, G com 0 e 51.457 scores acima de 900.

Esses resultados coincidem com `docs/result-comparison.md`; nenhum valor foi ajustado após a execução.

## Itens irreproduzíveis

### Amostra histórica da PoC 1

A tese não informa a população inicial, a ordem das linhas nem a semente da amostra de 10.000 usada nas Figuras 20–22. A reconstrução fixa semente 42 e usa uma seleção determinística, mas não pode provar igualdade com a amostra histórica.

### Execução final histórica da PoC 2

As células de XGBoost, score e Figuras 23–29 do notebook recuperado não conservam outputs. Versões de bibliotecas, defaults do modelo e estado anterior da sessão também não foram registrados. É possível explicar métricas aproximadas e reconstruir o método, mas não provar equivalência exata da execução original.

## Conflitos que permanecem visíveis

- AUC 0,91 no apêndice versus aproximadamente 0,65 no corpo da tese;
- PoC 1 descrita como distância Euclidiana no corpo e regressão logística no apêndice;
- regressão logística atribuída ao score na narrativa, enquanto o artefato usa XGBoost;
- categorias `[G…A]` da tese versus `[A…G]` no código recuperado para `PD × 1000`;
- campanha declarada para D/E, mas única faixa de taxa publicada para B;
- limite inferior 725 de B versus comportamento fechado à direita do `pd.cut`, que atribui exatamente 725 a C.

Esses pontos não são falhas pendentes da reconstrução: são inconsistências das fontes preservadas como `conflitante` ou limitações explicitamente classificadas.

## Limitações do resultado reconstruído

- a reconstrução não é validação regulatória, de justiça ou de impacto financeiro;
- não há validação temporal fora do período 2007–2020Q3;
- `int_rate` e `sub_grade` podem causar circularidade se a inferência ocorrer antes da oferta;
- undersampling altera a distribuição vista pelo classificador e exige a calibração documentada;
- as faixas A–G e a escala 0–1000 não equivalem a score de bureau;
- apenas B possui limites publicados para interpolação de taxa;
- F quase vazia e G vazia impedem conclusões robustas sobre categorias extremas;
- resultados descritivos não demonstram causalidade.

## Como repetir a validação

Os comandos completos para ambiente local e Google Colab estão no `README.md`. A verificação rápida é:

```bash
python scripts/verify_source_integrity.py
python scripts/validate_final_reconstruction.py
python -m unittest discover -s tests -v
```

A execução integral deve usar o comando `jupyter nbconvert --execute` documentado no README, que sempre inicia um kernel novo.

## Checklist de encerramento

- [x] escopo limitado à Fase 8;
- [x] fontes protegidas inalteradas;
- [x] execução integral em kernel novo;
- [x] ausência de estado oculto demonstrada;
- [x] seeds e versões registradas;
- [x] estrutura e outputs verificados automaticamente;
- [x] figuras com títulos, eixos e dimensões legíveis;
- [x] ambas as PoCs presentes;
- [x] README local/Colab atualizado;
- [x] comparação de resultados totalmente classificada;
- [x] itens irreproduzíveis e limitações registrados;
- [x] nenhum dataset, segredo ou modelo binário candidato ao Git;
- [ ] diff aprovado pelo responsável;
- [ ] commit criado somente após aprovação.
