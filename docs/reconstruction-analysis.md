# Análise forense da reconstrução

> **Nota de estado:** este documento registra a fotografia forense da Fase 0 e as decisões disponíveis antes da implementação. As Fases 0–8 foram concluídas posteriormente; o estado final está em `docs/final-validation.md`, e os resultados, em `docs/result-comparison.md`. Afirmações como “ausente”, “não existe” e “próximo passo” abaixo devem ser lidas no contexto histórico da investigação.

## 1. Escopo e conclusão

Foram inspecionadas a tese completa (84 páginas no PDF; 79 páginas numeradas de conteúdo) e todas as 93 células do notebook recuperado (31 Markdown e 62 de código).

Conclusão registrada na Fase 0: a estrutura mínima de fontes existia, mas o conteúdo então disponível **não bastava para executar o plano nem correspondia integralmente à versão final descrita na tese**. O notebook recuperado era uma evidência parcial, aparentemente associada a uma execução de 2022, e cobria:

- carregamento e filtros iniciais;
- quatro visualizações de EDA com outputs preservados;
- preparação parcial da PoC 2;
- XGBoost, avaliação, score e gráficos finais em código não executado/preservado.

Não cobre:

- PoC 1 baseada em distância Euclidiana;
- uma regressão logística efetivamente treinada;
- interpolação linear de juros;
- várias correlações, gráficos antes/depois e tabelas da tese;
- pipeline executável do início ao fim.

Naquele momento, o notebook reconstruído não deveria ser iniciado antes de resolver a fundação, o dataset e as decisões registradas neste documento. Essas condições foram atendidas nas fases posteriores.

## 2. Inventário das fontes

| Fonte | Evidência | SHA-256 | Estado |
|---|---|---|---|
| `TCC_Vinicius_P_Souza.pdf` | tese final, criada em 22/12/2024 | `abfed8559ee14018fb9204dd061aa6003d6ceb65e6cb63a9722d02e8e3182bdf` | fonte primária |
| `notebooks/tcc-recovered-from-colab.ipynb` | artefato do TCC recuperado após a perda do notebook original durante manutenção do Google Colab; 93 células | `7c58b4b0d0a9cae0accd49f77cd46fd8fd02316961ec588394463b5e9456f330` | fonte forense parcial; não modificar |
| Dataset Lending Club | URL fornecida no plano | não disponível | ausente intencionalmente |
| Google Drive ID `1eSFQZcaJeFx7rotY-j1b3ymHfApUhHOP` | notebook citado, inacessível | não disponível | apenas referência histórica |

### Divergências estruturais

- O artefato recuperado foi recebido originalmente como `Copy of Trabalho Data Mining.ipynb` e hoje usa o nome explícito `tcc-recovered-from-colab.ipynb`. A duplicata técnica criada na Fase 1 foi retirada do estado final por não constituir fonte independente; o hash e o histórico Git preservam a auditoria.
- Na Fase 0, ainda não existiam notebook reconstruído, ambiente de dependências nem pipeline; todos foram implementados posteriormente.
- O bloqueio Git observado durante a investigação foi resolvido: o projeto agora é um repositório funcional em `main`, rastreando `origin/main`.
- Antes desta análise não havia README, AGENTS, `.gitignore` nem diretório `docs/`.

## 3. Proveniência do notebook recuperado

O artefato recuperado do TCC está no formato 4.0, kernel Python 3, e contém metadados Colab. Dez células preservam `executionInfo` e outputs. Essas execuções registram o nome de usuário **Iuryck Santos**, timestamps de novembro de 2022 e ambiente Python 3.7/Colab. O metadado de proveniência superior também contém um ID de arquivo diferente do Google Drive citado na tese. A origem do artefato no processo de recuperação do TCC não transfere automaticamente a autoria desses metadados de execução.

Consequências:

- o artefato não deve ser apresentado como criação integral e exclusiva do autor da tese;
- os metadados devem ser preservados na fonte forense;
- código reaproveitado precisa ser marcado como recuperado/adaptado;
- nenhuma inferência de autoria além do que os metadados mostram é autorizada.

Todas as células têm `execution_count: null`. Apenas as células 3, 4, 7, 8, 9, 12, 15, 17, 20 e 35 possuem outputs. Da célula 36 em diante não há evidência de execução salva. A célula 35 termina em `KeyError: 'max_bal_bc'`, tornando falsa qualquer suposição de que o arquivo preservado executa do início ao fim.

## 4. Inventário lógico das células recuperadas

| Células | Conteúdo | Avaliação |
|---|---|---|
| 0–4 | título, instalação e imports | parcial; dependências antigas e imports obsoletos |
| 5–9 | leitura, filtro de status, conversão de taxa e ano | parcial; caminho absoluto e warning de cópia |
| 10–21 | EDA de finalidade, estado, DTI e montante por ano | parcial; quatro figuras com output |
| 22–27 | cabeçalho “Regressão logística, XG boosting”, filtro verificado e alvo | conflitante; regressão logística não é treinada |
| 28–41 | análise de NA, remoções, preenchimentos e seleção de 43 colunas | interrompido por erro na célula 35 |
| 42–51 | emprego, datas, codificação, `monthly_load` e `log1p` | fonte útil, mas sem execução preservada |
| 52–56 | split, imputação de DTI no treino e undersampling | parcial; não usa pipeline e codificadores já foram ajustados no conjunto completo |
| 57–62 | XGBoost com todas as variáveis e métricas | código presente, sem output; AUC usa classes |
| 63–76 | redução para 11 preditores, novo XGBoost, matriz e ROC | código presente, sem output; ROC metodologicamente incorreta |
| 77–80 | probabilidade, score e categorias | conflitante com a tese e nomes enganosos `lr_*` |
| 81–92 | boxplots e distribuições por categoria | código presente, sem outputs; usa `dexplot` |

## 5. Reconstrução esperada das duas provas de conceito

### PoC 1 — conteúdo e distância Euclidiana

Evidência exclusiva da tese (seções 4.4 e Anexo A); não existe no notebook recuperado.

| Elemento | Definição publicada |
|---|---|
| atributos | `annual_inc`, `all_util`, `acc_open_past_24mths`, `grade` |
| Campanha 1 | renda ≥ 30.000; utilização ≤ 60%; contas em 24 meses ≥ 1; grade B–E |
| Campanha 2 | renda ≥ 60.000; utilização ≤ 35%; contas em 24 meses ≥ 5; grade A–C |
| similaridade | distância Euclidiana |
| limiar | 20 |
| amostra de resultados | 10.000 perfis |
| totais publicados | cerca de 40 na Campanha 1; quase 90 na Campanha 2 |
| casos de teste | Vinicius somente Campanha 1; Elder somente Campanha 2 |

A Tabela 7 publica distâncias 5 e aproximadamente 30.000 para os exemplos. Isso demonstra que os atributos foram comparados em escala bruta, com domínio da renda, apesar de a prática recomendável ser normalização. Para preservar a evidência, a reconstrução deve:

1. reproduzir a formulação bruta e os exemplos;
2. explicitar a codificação de `grade` e os operadores das fronteiras;
3. testar a amostra determinística;
4. adicionar uma versão normalizada apenas como adaptação/análise de sensibilidade;
5. não forçar os totais publicados.

### PoC 2 — risco, XGBoost e ofertas

A tese lista 43 variáveis originais mais `monthly_load`. A lista da célula 37 corresponde substancialmente ao Anexo A. `monthly_load` é calculada como:

```text
((installment × 12) / annual_inc) × 100
```

com `-1` quando `annual_inc == 0` no notebook recuperado.

Fluxo pretendido pelas fontes:

1. filtrar renda verificada;
2. mapear `Fully Paid → 0` e `Charged Off`/`Default → 1`;
3. remover colunas com pelo menos 90% de NA;
4. preencher ausências sem vazamento;
5. codificar categorias;
6. aplicar `log1p` em `annual_inc` e `open_acc`;
7. dividir treino/teste;
8. subamostrar apenas o treino com `RandomUnderSampler(random_state=1)`;
9. comparar regressão logística e XGBoost;
10. reduzir atributos com base na importância do XGBoost;
11. avaliar por relatório, matriz de confusão e ROC/AUC;
12. converter probabilidade em score/categoria e personalizar taxa.

O notebook recuperado só materializa o XGBoost. `LogisticRegression` é importada, mas nunca instanciada ou ajustada. As variáveis `lr_preds` e `lr_preds_df` contêm, na realidade, probabilidades do objeto `model`, que é um `XGBClassifier`.

## 6. Mapeamento tese ↔ notebook recuperado

Legenda: **completo** = código e evidência suficientes; **parcial** = parte presente; **ausente** = sem célula; **conflitante** = código contradiz texto ou metodologia.

| Seção da tese | Metodologia/resultado esperado | Células | Estado | Ação proposta |
|---|---|---:|---|---|
| 4.1 | dataset 2007–2020Q3, 2.925.493 × 142 | 6 | parcial | configurar caminho, validar versão, hash, período e shape |
| 4.2 | conversão de taxa/data e filtro de status | 6–9 | parcial | encapsular, copiar após filtro e registrar contagens |
| Fig. 9 | `loan_amnt` por ano | 19–20 | completo como evidência | modernizar e recalcular |
| Fig. 10 | correlação `loan_amnt`/`funded_amnt` = 1,00 | — | ausente | implementar e comparar valor |
| Fig. 11 | correlação FICO low/high = 1,00 | — | ausente | implementar e derivar `fico` explicitamente |
| Fig. 12 | correlação `total_acc`/`open_acc` = 0,71 | — | ausente | implementar e comparar valor |
| Fig. 13 | razões de inadimplência | 11–12 | conflitante | filtrar inadimplentes; código atual conta `purpose` também de pagantes |
| Fig. 14 | empréstimos por estado | 13–15 | completo como evidência | manter mapa e registrar população |
| Fig. 15 | distribuição de DTI | 16–18 | completo como evidência | modernizar e descrever outliers |
| 4.3 | verificados, alvo, NA, transformações | 26–51 | parcial/conflitante | pipeline sem erro e sem vazamento |
| Figs. 16–17 | renda antes/depois | 49, 51 | parcial | substituir `distplot` e criar gráfico posterior |
| Figs. 18–19 | `open_acc` antes/depois | 50–51 | parcial | criar gráfico posterior e corrigir título |
| Tabelas 3–4 | 10 primeiras colunas cruas | 9 | parcial | exibir duas tabelas reproduzíveis |
| Tabelas 5–6 | 10 colunas pós-processamento | — | ausente | gerar após pipeline final |
| 4.4 / Figs. 20–22 / Tabela 7 | PoC 1 e campanhas | — | ausente | reconstruir a partir da tese |
| 4.5.1 | 43 variáveis + `monthly_load` | 37, 47 | parcial | reconciliar lista e testar fórmula |
| 4.5.2–3 | regressão logística e interpolação | 24, 78–80 | conflitante | implementar baseline e interpolação reais |
| Fig. 23 | importância XGBoost, year 77, int_rate 53, monthly_load 44 | 58–60 | parcial | executar, fixar critério de importância e comparar |
| métricas | AUC 65,47%; precisões 0,88/0,34; acurácia 0,65 | 62, 70–75 | conflitante | recalcular com probabilidades; preservar comparação histórica |
| Fig. 24 | matriz de confusão | 72 | parcial | usar API moderna e informar valores |
| Fig. 25 | ROC teste 0,65 e treino 0,66 | 73–75 | conflitante | usar `predict_proba`; separar avaliação honesta de treino/teste |
| score A–G | limites 175, 225, 350, 475, 600, 725, 825, 900 | 78–80 | conflitante | definir sentido de risco e tratar valores externos |
| Fig. 26 | taxa por categoria | 83 | parcial | executar após corrigir categorias |
| Fig. 27 | DTI por categoria | 85 | parcial | executar após corrigir categorias |
| Fig. 28 | moradia por categoria | 88 | parcial | substituir `dexplot` por ferramenta mantida |
| Fig. 29 | aplicação individual/conjunta | 91 | parcial | substituir `dexplot` por ferramenta mantida |
| Tabelas 8–9 | forças/fraquezas e melhorias | — | ausente | reproduzir como Markdown fundamentado |
| Cap. 5 | conclusões e limitações | — | ausente | redigir somente após execuções |

## 7. Inconsistências e riscos técnicos

### 7.1 Entre a tese e o próprio PDF

- O corpo informa ROC AUC 65,47%; o artigo no Apêndice A informa AUC 0,91 para XGBoost, sem execução ou explicação conciliadora.
- O corpo descreve PoC 1 por distância Euclidiana; o Apêndice A diz que a primeira PoC utilizou regressão logística.
- O corpo diz que a regressão logística gerou os scores, mas depois atribui a evolução e previsões ao XGBoost; o notebook usa apenas XGBoost.
- A conclusão afirma ajuste de hiperparâmetros, mas o notebook usa essencialmente parâmetros padrão e não contém busca/otimização.
- A metodologia do apêndice cita RMSE, mas o corpo e o notebook não mostram esse cálculo.
- A campanha de taxa é descrita como específica para categorias D/E, mas o exemplo publicado usa categoria B.

### 7.2 Categorias e sentido do score

- A tese define faixas ascendentes com rótulos `[G, F, E, D, C, B, A]`.
- A célula 80 usa os mesmos limites com `[A, B, C, D, E, F, G]`.
- A célula 79 calcula `probabilidade_de_default × 1000`. Esse é naturalmente um score de **risco**, no qual maior é pior; chamá-lo `ScoreCredito` causa ambiguidade.
- A ordenação do notebook (A para baixa probabilidade de default e G para alta) é semanticamente coerente com risco, mas contradiz os rótulos numéricos publicados na tese.
- Se forem mantidas as faixas da tese, a reconstrução deve converter probabilidade de adimplência/risco de modo explícito e validar as fronteiras.

### 7.3 Limpeza e pipeline

- A célula 30 remove colunas com NA ≥ 90%, mas o comentário diz “mais de 5%”. A tese confirma 90%.
- `max_bal_bc` é removida pelo limiar e depois acessada na célula 35, causando o erro preservado.
- Listas fixas de preenchimento e remoção podem conter colunas inexistentes e precisam de validação de esquema.
- `fico` é usado, mas não é criado a partir de `fico_range_low`/`fico_range_high`.
- `pd.get_dummies` e `LabelEncoder.fit_transform` são aplicados antes do split; isso aprende categorias no conjunto completo.
- `LabelEncoder` atribui ordem artificial a moradia, estado e tipo de aplicação.
- Apenas `X_train['dti']` recebe mediana; não há transformador compartilhado com teste/inferência.
- A transformação e seleção devem ser implementadas em pipelines ajustados somente no treino.

### 7.4 Modelagem e avaliação

- `objective="reg:logistic"` é usado onde a intenção é classificação binária; reconstruir com objetivo apropriado.
- ROC AUC e curva ROC usam `model.predict`, isto é, rótulos 0/1. O correto é usar probabilidade da classe positiva.
- A curva de treino é calculada no conjunto já subamostrado e no mesmo dado usado para ajuste, não sendo estimativa de generalização.
- A importância XGBoost precisa declarar o tipo (`weight`, `gain` etc.); o “F score” publicado não é diretamente comparável sem isso.
- `plot_confusion_matrix`, `plot_roc_curve`, `seaborn.distplot`, imports Dash antigos e `Series.iteritems` estão obsoletos/removidos em versões modernas.
- `int_rate`, `sub_grade` e outros atributos atribuídos pela plataforma podem introduzir circularidade se o objetivo for recomendar uma oferta antes da decisão de crédito. O momento de disponibilidade de cada atributo deve ser documentado.

### 7.5 Resultado e execução

- Não há outputs preservados para XGBoost, matriz, ROC, score ou gráficos das categorias.
- Não é possível provar os números do PDF a partir do notebook sem o dataset exato e uma nova execução.
- A versão Q1/Q3, a semente da amostra de 10.000 e a regra exata de qualificação da PoC 1 podem alterar resultados.

## 8. Decisões de reconstrução

| Tema | Decisão segura inicial |
|---|---|
| autoria | preservar metadados e declarar reconstrução |
| notebook fonte | imutável; validar hash em cada fase |
| dataset | registrar versão/hash/schema; nunca versionar |
| PoC 1 | versão bruta fiel + versão normalizada claramente adaptada |
| regressão logística | implementar baseline separado, pois é afirmada pela tese mas ausente no notebook |
| XGBoost | reconstruir classificação binária e manter comparação com lógica histórica |
| vazamento | usar pipelines ajustados no treino e undersampling só no treino |
| AUC | calcular com probabilidades; valores históricos ficam apenas como referência |
| score | nomear score de risco ou inverter explicitamente para score de crédito |
| juros | só implementar limites sustentados; testar o exemplo sem inventar resultado |
| números conflitantes | manter ambos e classificar como conflito até haver evidência |

## 9. Critérios de rastreabilidade no notebook novo

Cada seção reconstruída deve ter uma nota Markdown com:

- **origem:** tese, célula(s) recuperada(s) ou reconstrução nova;
- **tipo:** recuperado, adaptado ou novo;
- **mudança:** correção de API, correção metodológica ou extensão;
- **resultado esperado:** número/figura publicado, quando existir;
- **resultado observado:** preenchido somente por execução;
- **limitação:** diferença de dataset, hipótese ou item irreproduzível.

## 10. Próximo passo autorizado à época

Após revisão e commit da fundação preparada na Fase 1, o próximo passo então permitido seria exclusivamente a Fase 2 de `docs/implementation-plan.md`.

Nenhuma implementação do notebook foi realizada durante a investigação forense. As Fases 1–8, já concluídas, materializaram e validaram a reconstrução.
