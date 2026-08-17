# Resultados da evolução

Resultados posteriores à reconstrução; não pertencem ao TCC original e não
alteram `docs/result-comparison.md`. Nenhum modelo ou limiar foi escolhido pelo
teste.

## E2 — modelos pré-oferta

Divisão aleatória estratificada da reconstrução, com ajuste e calibração
sigmoide em partições distintas do treino. Métricas calculadas no teste com
probabilidades calibradas.

| Cenário | Modelo | Atributos | ROC AUC | PR-AUC | Brier |
|---|---|---:|---:|---:|---:|
| referência histórica | XGBoost reduzido | 12 | 0,706847 | 0,393454 | 0,153092 |
| solicitação conhecida | regressão logística | 38 | 0,687283 | 0,368743 | 0,156105 |
| solicitação conhecida | XGBoost | 38 | 0,696659 | 0,385919 | 0,154390 |
| perfil puro | regressão logística | 34 | 0,632656 | 0,304546 | 0,162959 |
| perfil puro | XGBoost | 34 | 0,644703 | 0,319878 | 0,161433 |

O XGBoost de solicitação conhecida fica próximo da referência histórica mesmo
sem cinco atributos pós-decisão. O perfil puro perde discriminação ao remover
também os campos da solicitação. O limiar diagnóstico 0,5 apresentou recall
muito baixo e não deve ser tratado como política operacional.

## E3 — validação temporal madura

Todos os contratos satisfazem `issue_d + term <= 2020-09`. Preprocessamento,
reamostragem e modelo usam somente treino; a sigmoide usa somente calibração.

| Auditoria | Janelas de treino / calibração / teste | Teste (n; prevalência) |
|---|---|---:|
| prazos 36 e 60 meses | 2008–2014 / 2015Q1 / 2015Q2–Q3 | 142.297; 0,221375 |
| somente 36 meses | 2008–2015 / 2016 / 2017Q1–Q3 | 131.180; 0,188764 |

| Auditoria | Cenário | Modelo | Efetivos | ROC AUC | PR-AUC | Brier |
|---|---|---|---:|---:|---:|---:|
| 36/60 | solicitação | logística | 30/38 | 0,695270 | 0,385904 | 0,158486 |
| 36/60 | solicitação | XGBoost | 30/38 | 0,699285 | 0,390930 | 0,157833 |
| 36/60 | perfil | logística | 26/34 | 0,639365 | 0,318189 | 0,165494 |
| 36/60 | perfil | XGBoost | 26/34 | 0,645304 | 0,326656 | 0,164751 |
| 36 | solicitação | logística | 38/38 | 0,645974 | 0,281289 | 0,147407 |
| 36 | solicitação | XGBoost | 38/38 | 0,651859 | 0,291121 | 0,146613 |
| 36 | perfil | logística | 34/34 | 0,630515 | 0,268433 | 0,148612 |
| 36 | perfil | XGBoost | 34/34 | 0,636912 | 0,276531 | 0,147909 |

O teste de 2015 manteve ROC AUC próximo ao aleatório. Em 2017, o XGBoost de
solicitação perdeu 0,044800 de ROC AUC e a PR-AUC caiu com a prevalência. Isso
evidencia sensibilidade temporal, não autoriza reajuste no teste nem seleção de
vencedor. Oito atributos sem qualquer observação até 2014 foram excluídos com
informação exclusiva do treino.

## E4 — bandas e PoC 1

Septis do XGBoost de solicitação foram ajustados somente na calibração de
2015Q1 e congelados para o teste de 2015Q2–Q3. As bandas são internas e não
equivalem a bureau, rating ou categorias A–G.

| Banda | Registros | Inadimplência | IC 95% de Wilson |
|---|---:|---:|---:|
| E01 | 18.558 | 0,456892 | 0,449735–0,464067 |
| E02 | 18.207 | 0,323667 | 0,316908–0,330499 |
| E03 | 19.575 | 0,258902 | 0,252813–0,265085 |
| E04 | 20.235 | 0,214826 | 0,209221–0,220538 |
| E05 | 21.440 | 0,162080 | 0,157208–0,167074 |
| E06 | 22.329 | 0,125039 | 0,120765–0,129442 |
| E07 | 21.953 | 0,065914 | 0,062707–0,069272 |

As sete bandas têm suporte e inadimplência monotônica; o PSI entre calibração
e teste é 0,005593. A–G permanece apenas como comparação histórica.

Na PoC 1, a análise P10/P25/P50/P75/P90 confirmou que as distâncias bruta e
normalizada operam em escalas incompatíveis. O limiar histórico bruto 20
qualificou 36 de 1.790 elegíveis na Campanha 1 e 10 de 178 na Campanha 2.
Nenhum percentil foi recomendado: uma nova regra exige target de adesão ou
função de negócio externa.

## Conclusão

Remover atributos indisponíveis no momento da decisão é viável, mas reduz
desempenho, especialmente no perfil puro. A validação temporal revelou mudança
de composição, e as bandas funcionam apenas como segmentação experimental.
Nada aqui demonstra prontidão para produção, impacto financeiro, fairness,
adesão comercial ou adequação regulatória.
