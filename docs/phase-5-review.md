# Revisão da Fase 5 — PoC 2, baseline e XGBoost

Data da validação: 4 de agosto de 2026. Commit base: `49ec59e`.

## Resultado

A PoC 2 foi reconstruída e executada sobre os 1.272.273 empréstimos com status final e renda verificada. Foram treinados três objetos separados: regressão logística completa, XGBoost completo e XGBoost reduzido. A avaliação usa o teste original e desbalanceado; nenhum modelo binário foi salvo no repositório.

## Reconciliação das variáveis

O Anexo A enumera 43 itens, mas inclui `default` como item 3. Excluir o alvo deixa 42 preditores originais. Com `monthly_load`, existem 43 entradas efetivas, embora a narrativa afirme “44 variáveis”. O alvo nunca entra em `X`.

`monthly_load` segue a fórmula publicada:

```text
((installment × 12) / annual_inc) × 100
```

Renda zero recebe `-1`. `fico` permanece a média dos limites criada na Fase 2. `annual_inc` e `open_acc` recebem `log1p` como transformação fixa; categorias nominais recebem one-hot ajustado somente no treino.

## Separação e ausência de vazamento

- divisão estratificada 80/20, semente 1;
- treino: 1.017.818 registros, sendo 798.743 classe 0 e 219.075 classe 1;
- teste: 254.455 registros, sendo 199.686 classe 0 e 54.769 classe 1;
- `RandomUnderSampler` seleciona 219.075 exemplos de cada classe somente no treino;
- imputadores, categorias do one-hot e escalador da regressão são ajustados depois do undersampling e nunca veem o teste;
- o teste não é balanceado.

## Modelos e métricas de teste

| Modelo | Atributos | ROC AUC por probabilidade | AUC histórica por rótulos | Acurácia |
|---|---:|---:|---:|---:|
| Regressão logística | 43 | 0,704407 | 0,647971 | 0,637154 |
| XGBoost completo | 43 | 0,711818 | 0,654009 | 0,647109 |
| XGBoost reduzido | 12 | 0,706897 | 0,649376 | 0,642593 |

A redução rastreada na célula 63 custa apenas 0,004921 de AUC correta. No XGBoost reduzido, a precisão é 0,872802 para a classe 0 e 0,333465 para a classe 1. A matriz de confusão é:

|  | Prevê classe 0 | Prevê classe 1 |
|---|---:|---:|
| Classe 0 real | 127.293 | 72.393 |
| Classe 1 real | 18.551 | 36.218 |

## Explicação do AUC publicado

O notebook recuperado calcula ROC AUC com `model.predict`, isto é, classes. A reconstrução encontra 0,649376 pelo mesmo cálculo no modelo reduzido, praticamente os 0,65 da tese. Com probabilidades, o valor correto é 0,706897. Para o XGBoost completo, o cálculo histórico produz 0,654009, também praticamente os 65,47% publicados.

Essa proximidade explica os resultados históricos sem manter o erro metodológico. A Figura 25 e a avaliação principal usam probabilidades; a curva de treino tem AUC 0,709264 e é apresentada apenas como medida de ajuste.

## Importância e redução

A Figura 23 usa importância por ganho, explicitamente configurada e agregada das colunas one-hot para a variável fonte. As primeiras posições são `int_rate` 0,294044, `addr_state` 0,138330 e `term` 0,136008. `monthly_load` aparece em 7º, com 0,027179, e `year` em 10º, com 0,022651.

Isso diverge dos F scores 77/53/44 publicados, cujo tipo não é definido. Além disso, `int_rate` e `sub_grade` são atribuídos pela plataforma e podem ser circulares em uma recomendação feita antes da decisão de crédito.

## Verificações e limites

- regressão logística e XGBoost têm nomes e objetos distintos;
- XGBoost usa `objective="binary:logistic"` e `importance_type="gain"`;
- relatório, matriz de confusão e ROC são calculados no teste por probabilidades;
- o cálculo com rótulos aparece somente como comparação histórica;
- score, categorias e ofertas não foram implementados, pois pertencem à Fase 6;
- o AUC 0,91 do apêndice não foi reproduzido e permanece conflitante.

## Checklist de encerramento

- [x] escopo limitado à Fase 5;
- [x] fontes protegidas inalteradas;
- [x] alvo e contagem de atributos reconciliados;
- [x] split estratificado e transformadores sem vazamento;
- [x] balanceamento somente no treino;
- [x] baseline logístico e XGBoost separados;
- [x] seleção reduzida rastreável;
- [x] Figuras 23–25 e métricas executadas;
- [x] comparação com a tese atualizada;
- [ ] diff aprovado pelo responsável;
- [ ] commit criado somente após aprovação.
