# Comparação entre a tese e a reconstrução

Este documento é o registro oficial das diferenças entre os resultados publicados e as execuções reconstruídas. Ele deve ser atualizado ao final de cada fase que gere tabelas, figuras ou métricas.

Não preencher a coluna “resultado reconstruído” sem uma execução reproduzível. Valores observados apenas no PDF permanecem na coluna da tese.

| Item | Resultado da tese | Resultado reconstruído | Diferença | Explicação provável | Status |
|---|---|---|---|---|---|
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
