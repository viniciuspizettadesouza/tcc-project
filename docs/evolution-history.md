# Histórico da evolução

As fases E0–E5 são extensões posteriores à reconstrução. Elas não alteram os
resultados históricos nem `docs/result-comparison.md`.

| Fase | Estado | Entrega principal |
|---|---|---|
| E0 | aprovada | congelamento dos dois notebooks históricos, criação do evolutivo e separação do pacote `tcc_evolution` |
| E1 | aprovada | contratos com 43 atributos históricos, 38 de solicitação conhecida e 34 de perfil puro |
| E2 | aprovada | logística e XGBoost pré-oferta com calibração separada e métricas probabilísticas |
| E3 | aprovada | dois backtests cronológicos com maturidade até setembro de 2020 |
| E4 | aprovada | bandas internas ajustadas na calibração e sensibilidade da PoC 1 sem escolha automática de limiar |
| E5 | validada | consolidação do notebook ativo, documentação e auditoria evolutiva |

## Decisões preservadas

- target de inadimplência não é target de adesão;
- fitting, calibração e teste permanecem separados;
- resultados de teste não selecionam modelo, corte ou limiar;
- categorias A–G são somente referência histórica; `E01…E07` são internas;
- resultados novos pertencem a `docs/evolution-results.md`;
- `notebooks/tcc-evolved.ipynb` é o único ponto de entrada para novas pesquisas.

## Evidência final — 17 de agosto de 2026

- notebook E0–E5 executado em kernel novo: 43/43 células de código, zero erros;
- 63 outputs auditados sem caminhos locais, credenciais ou identificadores;
- 117 testes e `make validate` aprovados;
- `docs/result-comparison.md` permaneceu sem alterações evolutivas;
- hashes históricos preservados:
  - recuperado: `7c58b4b0d0a9cae0accd49f77cd46fd8fd02316961ec588394463b5e9456f330`;
  - reconstruído: `4b9f385dd51a798248dd6bfcbf0ad2e8815f90de7bc5fb59cd98a7431057d044`.

Fairness regulatória, impacto financeiro, adesão real e validação brasileira
continuam fora do ciclo por falta de dados adequados. Nenhum commit foi criado
automaticamente durante as fases.
