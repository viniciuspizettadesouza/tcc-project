# Revisão da Fase 3 — análise exploratória

Data da validação: 4 de agosto de 2026. Commit base: `a3890e4`.

## Resultado

A análise exploratória foi reconstruída e executada do início ao fim com o dataset real. O notebook apresenta as Figuras 9–19 na ordem e com os títulos da tese, declara a população de cada análise e preserva as fontes recuperadas. A fase foi posteriormente aprovada e encerrada no commit `c10a14d`.

## Populações e renderização

- arquivo bruto: 2.925.493 registros;
- Figuras 9–15: 1.860.764 empréstimos em `Fully Paid`, `Charged Off` ou `Default`;
- Figuras 16–19: 1.272.273 desses empréstimos com renda `Verified` ou `Source Verified`;
- gráficos densos: amostra determinística de 100.000, semente 42, usada somente para renderização;
- correlações, contagens e tabelas agregadas: população completa correspondente.

A Figura 9 exclui 2020, seguindo a célula 20 recuperada e reconhecendo que o arquivo termina no terceiro trimestre. A Figura 13 corrige a população do código recuperado e inclui somente `Charged Off` e `Default`.

## Resultados observados

| Análise | Resultado reconstruído | Comparação com a tese |
|---|---:|---:|
| `loan_amnt` × `funded_amnt` | 0,999700 | 1,00 após arredondamento |
| `fico_range_low` × `fico_range_high` | 0,999999923 | 1,00 após arredondamento |
| `total_acc` × `open_acc` | 0,708775 | 0,71 após arredondamento |
| inadimplentes | 362.981 | total não publicado |
| finalidade `debt_consolidation` | 219.761 | primeiro lugar confirmado |
| finalidade `credit_card` | 69.656 | segundo lugar confirmado |
| DTI válido | 1.859.655 | total não publicado |
| DTI mediano / percentil 99 / máximo | 17,71 / 39,61 / 999 | assimetria e outliers confirmados qualitativamente |

## Decisões de segurança e escopo

- As Tabelas 3–6 não reproduzem linhas de clientes. Elas mostram o esquema das dez primeiras colunas e perfis agregados após o pipeline.
- `annual_inc_log1p` e `open_acc_log1p` são cópias analíticas; as colunas originais permanecem inalteradas.
- Os eixos da renda mostram os percentis 0,5–99,5, e o eixo do DTI termina no percentil 99, para que extremos não ocultem a distribuição central. Os extremos completos continuam nas tabelas de resumo.
- Nenhuma imputação, codificação, divisão treino/teste, reamostragem ou modelagem foi introduzida.
- O dataset, amostras de linhas e artefatos externos continuam ignorados pelo Git.

## Verificações exigidas

- integridade das fontes antes e depois da fase;
- execução integral das 26 células do notebook com o dataset real;
- validação do formato do notebook e ausência de outputs de erro;
- testes unitários do pipeline, funções de EDA e contrato do notebook;
- Ruff e `git diff --check`;
- inspeção do diff e confirmação de que o artefato recuperado não foi alterado.

## Checklist de encerramento

- [x] escopo limitado à Fase 3;
- [x] fontes protegidas inalteradas;
- [x] Figuras 9–19 na ordem da tese;
- [x] populações e amostras declaradas;
- [x] correlações recalculadas na população completa;
- [x] tabelas sem registros individuais;
- [x] documentação de comparação atualizada;
- [x] diff aprovado pelo responsável;
- [x] commit da Fase 3 criado após aprovação (`c10a14d`).
