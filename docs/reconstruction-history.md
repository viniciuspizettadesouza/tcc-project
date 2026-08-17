# Histórico da reconstrução

As Fases 0–8 foram concluídas em 4 de agosto de 2026, com integridade, testes,
revisão e aprovação separadas.

| Fase | Commit | Entrega e decisão principal |
|---:|---|---|
| 0 | `b29ff0b` | leitura forense do PDF e das 93 células recuperadas; tese definida como fonte metodológica e execução reproduzível como limite da evidência |
| 1 | `9ed7362` | Python 3.12, dependências fixadas, manifesto, ambiente e verificação de fontes |
| 2 | `a3890e4` | pipeline validado em blocos, amostra determinística e manifesto agregado |
| 3 | `c10a14d` | Figuras 9–19 e Tabelas 3–6 sobre populações explícitas |
| 4 | `49ec59e` | PoC 1 reconstruída da tese, incluindo divergência 35/40 da Campanha 2 |
| 5 | `7e5f911` | logística e XGBoost separados, split anterior aos transformadores e undersampling somente no treino |
| 6 | `7c94882` | calibração sigmoide, direção explícita dos scores e juros somente para B |
| 7 | `6b0eca9` | narrativa com origem recuperada, adaptada ou nova |
| 8 | `134222c` | execução integral e classificação final das divergências |

`cc127b8` esclareceu a proveniência do recuperado; `84eeb04` consolidou a
documentação sem mudar resultados.

## Evidências centrais

- dataset: 2.925.493 × 142; 1.860.764 status finais e 1.272.273 também com
  renda verificada;
- PoC 1: 36/10 aprovações pela regra completa e 64/88 somente por distância;
- regressão logística: ROC AUC 0,704407;
- XGBoost completo/reduzido: 0,711818/0,706897;
- XGBoost reduzido calibrado: ROC AUC 0,706847 e Brier 0,153092;
- score 750: categoria B e taxa reconstruída de 15,3925% a.a.;
- execução final: 39/39 células, zero erros, 20 PNG e uma Plotly;
- comparação: 11 itens reproduzidos, 10 parciais, 5 divergentes, 2
  conflitantes e 2 irreproduzíveis.

## Decisões que permanecem

- `fico` é a média dos limites inferior e superior;
- AUC usa probabilidades, não rótulos;
- `PD × 1000` é score de risco; `(1 − PD) × 1000`, score de crédito;
- o limiar bruto 20 e a referência forense 40 da Campanha 2 são preservados;
- normalização da PoC 1 é sensibilidade, não nova regra;
- `int_rate` e `sub_grade` podem ser circulares antes da oferta;
- nenhuma equivalência histórica exata é alegada sem evidência.

O inventário completo está em `docs/reconstruction-analysis.md`; números e
divergências, em `docs/result-comparison.md`; validação, em
`docs/final-validation.md`.
