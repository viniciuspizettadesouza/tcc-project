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
| PoC 1 — aprovados Campanha 1 | cerca de 40 em amostra de 10.000 | pendente | pendente | versão/amostra e regra exata ainda não validadas | não executado |
| PoC 1 — aprovados Campanha 2 | quase 90 em amostra de 10.000 | pendente | pendente | versão/amostra e regra exata ainda não validadas | não executado |
| XGBoost — ROC AUC, todas as variáveis | 65,47% | pendente | pendente | notebook não preserva output; PDF não esclarece cálculo com probabilidade | não executado |
| XGBoost — ROC AUC de teste | 0,65 | pendente | pendente | notebook recuperado usa rótulo de classe, método incorreto para curva ROC | não executado |
| XGBoost — ROC AUC de treino | 0,66 | pendente | pendente | notebook recuperado usa rótulo de classe e treino subamostrado | não executado |
| Precisão — classe 0 | 0,88 | pendente | pendente | dataset e execução ainda indisponíveis | não executado |
| Precisão — classe 1 | 0,34 | pendente | pendente | dataset e execução ainda indisponíveis | não executado |
| Acurácia geral | 0,65 | pendente | pendente | tese chama o valor de “precisão geral” | não executado |
| Apêndice — AUC do XGBoost | 0,91 | pendente | conflito interno | contradiz 0,6547 no corpo e não há execução correspondente | conflitante |
| Exemplo de taxa — score 750, categoria B | limites 725–825; taxas 13,33%–16,08%; resultado numérico não informado | pendente | pendente | sentido da interpolação ainda ambíguo | não executado |

## Estados permitidos

- `não executado`: implementação ou dados ainda ausentes;
- `reproduzido`: resultado dentro da tolerância previamente definida;
- `divergente`: execução válida difere da tese;
- `parcial`: apenas parte do item foi reproduzida;
- `irreproduzível`: evidência insuficiente após tentativas documentadas;
- `conflitante`: fontes primárias fornecem valores incompatíveis.
