# Comparação entre a tese e a reconstrução

Este documento é o registro oficial das diferenças entre os resultados publicados e as execuções reconstruídas. Ele deve ser atualizado ao final de cada fase que gere tabelas, figuras ou métricas.

Não preencher a coluna “resultado reconstruído” sem uma execução reproduzível. Valores observados apenas no PDF permanecem na coluna da tese.

| Item | Resultado da tese | Resultado reconstruído | Diferença | Explicação provável | Status |
|---|---|---|---|---|---|
| Figura 9 — `loan_amnt` por ano | aumento até 2013 e posterior estabilização; 2020 ausente na figura | tendência visual compatível; população completa para filtros e amostra determinística de 100.000 para renderização, excluindo 2020 | comparação apenas qualitativa | a tese não publica estatísticas anuais nem a semente; a reconstrução explicita a amostra visual | parcial |
| Figura 10 — correlação `loan_amnt` × `funded_amnt` | 1,00 | 0,999700 em 1.860.764 pares | -0,000300; igual após arredondamento a duas casas | a tese publica somente duas casas decimais | reproduzido |
| Figura 11 — correlação FICO low × high | 1,00 | 0,999999923 em 1.860.764 pares | aproximadamente -0,000000077; igual após arredondamento | raras diferenças não constantes entre os limites são ocultadas pelo arredondamento da tese | reproduzido |
| Figura 12 — correlação `total_acc` × `open_acc` | 0,71 | 0,708775 em 1.860.764 pares | -0,001225; igual após arredondamento a duas casas | diferença compatível com o arredondamento publicado | reproduzido |
| Figura 13 — finalidades de inadimplência | consolidação de dívidas em primeiro lugar e cartão de crédito em segundo | 362.981 inadimplentes; `debt_consolidation` 219.761 e `credit_card` 69.656 | hierarquia principal confirmada | o notebook recuperado contava também pagantes; a reconstrução filtra `Charged Off`/`Default` | reproduzido |
| Figuras 14–15 — estado e DTI | Califórnia, Texas e Nova York em destaque; DTI assimétrico com outliers | mapa recalculado; DTI mediano 17,71, percentil 99 39,61 e máximo 999 em 1.859.655 valores | comparação quantitativa incompleta | a tese não publica contagens estaduais nem percentis; a reconstrução limita o eixo do histograma ao percentil 99 e registra extremos | parcial |
| Figuras 16–19 — `log1p` de renda e contas abertas | redução visual da assimetria após `log(x + 1)` | gráficos antes/depois executados em amostra determinística de 100.000 da população verificada | comparação apenas qualitativa | a tese não publica estatísticas nem semente dos gráficos | parcial |
| Tabelas 3–6 — antes/depois | cinco linhas individuais em cada bloco de colunas | esquema das dez colunas originais e perfis agregados de dez colunas processadas | formato deliberadamente diferente | a reconstrução não versiona registros individuais potencialmente sensíveis e não antecipa codificação/imputação da Fase 5 | parcial |
| PoC 1 — aprovados Campanha 1 | cerca de 40 em amostra de 10.000; a barra da Figura 20 indica aproximadamente 43 | 36 com critérios declarados + distância ≤ 20; 64 usando somente distância | -7 em relação à leitura aproximada da barra; o modo somente distância excede em cerca de 21 | amostra determinística reconstruída difere da amostra não especificada; a tese não esclarece se reaplica os critérios após calcular distância | parcial |
| PoC 1 — aprovados Campanha 2 | quase 90 em amostra de 10.000; a barra da Figura 20 indica aproximadamente 89 | 10 com critérios declarados + distância ≤ 20; 88 usando somente distância | -79 no modo conforme os critérios; -1 no modo somente distância | o resultado publicado só é aproximado quando se ignora a elegibilidade máxima de 35% e se usa a referência forense de 40% na distância | divergente |
| PoC 1 — Tabela 7 Vinicius/Elder | distâncias C1: 5 e 30000,010433; C2: 30000,004017 e 5; qualificações exclusivas | valores e booleanos reproduzidos com referência forense de utilização 40 na Campanha 2 | referência estrita 35 produz 30000,006933 e 0 na C2 | a regra textual diz máximo 35%, mas os números publicados provam referência 40 no cálculo da distância | reproduzido |
| PoC 1 — distância normalizada | não publicada | com IQR e limiar 20: todos os 1.790 elegíveis da C1 e 178 da C2 qualificam | limiar bruto não é transferível à nova escala | um limiar normalizado exigiria calibração externa; nenhum valor foi inventado | parcial |
| Regressão logística — baseline completo | afirmada pela tese, mas não treinada no notebook recuperado | ROC AUC por probabilidade 0,704407; acurácia 0,637154 | não há resultado histórico executável para comparação | baseline novo, separado do XGBoost e avaliado no teste não balanceado | parcial |
| XGBoost — ROC AUC, todas as variáveis | 65,47% | 0,711818 por probabilidade; 0,654009 pelo cálculo histórico com rótulos | +0,057118 no cálculo correto; -0,000691 no histórico | o valor publicado é compatível com o uso metodologicamente incorreto de classes observado no notebook | reproduzido |
| XGBoost reduzido — ROC AUC de teste | 0,65 | 0,706897 por probabilidade; 0,649376 por rótulos | +0,056897 no cálculo correto; -0,000624 no histórico | a reconstrução usa probabilidades na avaliação principal e preserva rótulos apenas para explicar o número histórico | reproduzido |
| XGBoost reduzido — ROC AUC de treino | 0,66 | 0,709264 por probabilidade no treino original | +0,049264 | a tese usa rótulos e treino subamostrado; a reconstrução usa probabilidades e explicita que treino mede ajuste | divergente |
| Precisão — classe 0 | 0,88 | 0,872802 | -0,007198 | diferença inferior a um ponto percentual com pipeline corrigido | reproduzido |
| Precisão — classe 1 | 0,34 | 0,333465 | -0,006535 | diferença inferior a um ponto percentual com pipeline corrigido | reproduzido |
| Acurácia geral | 0,65 | 0,642593 | -0,007407 | a tese chama o valor de “precisão geral”; reconstrução registra como acurácia | reproduzido |
| Figura 23 — importância XGBoost | `year` 77, `int_rate` 53 e `monthly_load` 44 por “F score” | por ganho agregado: `int_rate` 0,294044 (1º), `monthly_load` 0,027179 (7º), `year` 0,022651 (10º) | ordenação e medida diferentes | a tese não define o tipo de importância; ganho agregado não é equivalente a contagem/F score | divergente |
| Redução de atributos XGBoost | queda descrita como pequena, sem valor | 43 → 12 atributos; AUC de teste 0,711818 → 0,706897 | -0,004921 | lista reduzida vem da célula 63, sem seleção pelo teste atual | reproduzido |
| Apêndice — AUC do XGBoost | 0,91 | máximo observado 0,711818 no teste | -0,198182 | contradiz 0,6547 no corpo e não há execução correspondente | conflitante |
| Calibração do XGBoost reduzido | não publicada | AUC 0,706847 antes/depois; Brier 0,218330 → 0,153092 com sigmoide | comparação histórica indisponível | calibração ajustada em partição exclusiva do treino e avaliada no teste intocado | parcial |
| Categorias de score no teste | categorias A–G; narrativa discute ambos os extremos | A 66.468; B 63.158; C 45.975; D 23.277; E 4.116; F 4; G 0; acima de 900: 51.457 | G ausente e F quase vazia | score de crédito explícito é `(1 − PD calibrada) × 1000`; linhas fora da faixa não são descartadas | divergente |
| Exemplo de taxa — score 750, categoria B | limites 725–825; taxas 13,33%–16,08%; resultado numérico não informado | 15,3925% a.a.; extremos 725 → 16,08% e 825 → 13,33% | valor reconstruído não comparável a número publicado ausente | direção adotada explicitamente: maior score de crédito recebe menor taxa; PDF não define o sentido | parcial |
| Campanha de taxa por categoria | texto afirma foco em D/E; única evidência numérica é o exemplo B | oferta implementada somente para B; A e C–G permanecem sem taxa | conflito interno impede implementar D/E | nenhuma faixa de taxa foi inferida sem evidência | conflitante |
| Figuras 26–29 — taxa, DTI, moradia e aplicação | análises visuais por A–G, incluindo interpretações dos extremos | figuras reexecutadas no teste com categorias da tese; G tem 0 casos e F tem 4 | conclusões sobre extremos não reproduzíveis | probabilidades calibradas e tratamento explícito fora de 175–900 alteram a composição | divergente |

## Estados permitidos

- `não executado`: implementação ou dados ainda ausentes;
- `reproduzido`: resultado dentro da tolerância previamente definida;
- `divergente`: execução válida difere da tese;
- `parcial`: apenas parte do item foi reproduzida;
- `irreproduzível`: evidência insuficiente após tentativas documentadas;
- `conflitante`: fontes primárias fornecem valores incompatíveis.
