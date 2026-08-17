# Validação final da reconstrução — Fase 8

Executada em 4 de agosto de 2026 sobre o commit `6b0eca9`; encerrada em
`134222c`.

## Resultado

O notebook reconstruído executou com o dataset real em kernel novo:

```text
85 células: 46 Markdown + 39 código
39/39 células de código executadas em sequência
0 erros
20 figuras PNG + 1 Plotly
```

O dataset validado possui 2.925.493 × 142, SHA-256
`5878af2a088f8ab5214c9337289fb8b5eb6c6338fd3f417b6cdc18513dc6f`;
1.860.764 registros têm status final e 1.272.273 também renda verificada.
Dados, credenciais e modelos binários permaneceram fora do Git. Python 3.12 e
as 14 dependências diretas estão fixados em `requirements.txt`.

## Resultados confirmados

| Resultado | Valor |
|---|---:|
| PoC 1 — regra completa C1/C2 | 36 / 10 |
| PoC 1 — somente distância C1/C2 | 64 / 88 |
| regressão logística — ROC AUC | 0,704407 |
| XGBoost completo — ROC AUC | 0,711818 |
| XGBoost reduzido — ROC AUC | 0,706897 |
| XGBoost reduzido calibrado | AUC 0,706847; Brier 0,153092 |
| score 750 | B; 15,3925% a.a. |

A auditoria confirmou as 15 seções, Figuras 9–29, Tabelas 3–9, títulos,
dimensões, eixos, sementes, caminhos portáveis e 30 comparações classificadas.

## Limites e conflitos preservados

- a amostra histórica de 10.000 e a execução final da PoC 2 não podem ser
  reproduzidas exatamente;
- AUC 0,91 no apêndice conflita com aproximadamente 0,65 no corpo;
- a PoC 1 aparece como distância no corpo e logística no apêndice;
- a narrativa atribui o score à logística, mas o recuperado usa XGBoost;
- categorias e direção do score divergem entre tese e código recuperado;
- a campanha é descrita para D/E, mas só B possui faixa de juros;
- 725 é uma fronteira ambígua nas categorias;
- não há validação regulatória, de fairness, causalidade ou impacto financeiro;
- A–G e a escala 0–1000 não equivalem a bureau.

Esses pontos são limitações das fontes, não pendências ocultas. A classificação
completa está em `docs/result-comparison.md`.

## Como repetir

```bash
python scripts/verify_source_integrity.py
python scripts/validate_final_reconstruction.py
python -m unittest discover -s tests -v
```

A execução integral usa `make reproduce-reconstructed`, que opera sobre cópia
temporária e preserva o notebook histórico.
