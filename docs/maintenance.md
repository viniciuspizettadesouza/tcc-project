# Guia de manutenção

## Escopo

`notebooks/tcc-recovered-from-colab.ipynb` e
`notebooks/tcc-reconstructed.ipynb` são históricos imutáveis.
`notebooks/tcc-evolved.ipynb` é o único ponto de entrada para novas pesquisas.
Resultados novos pertencem aos documentos de evolução, nunca a
`docs/result-comparison.md`.

## Organização dos módulos

| Módulos | Responsabilidade |
|---|---|
| `src/tcc_reconstruction/__init__.py`, `src/tcc_reconstruction/schema.py`, `src/tcc_reconstruction/data.py` | API histórica, esquema, leitura validada, filtros, amostra e manifesto |
| `src/tcc_reconstruction/eda.py` | agregados e amostras seguras da EDA |
| `src/tcc_reconstruction/poc1.py` | elegibilidade e distâncias históricas |
| `src/tcc_reconstruction/poc2.py` | pipelines sem vazamento, logística e XGBoost |
| `src/tcc_reconstruction/score.py` | calibração, scores, A–G e oferta evidenciada para B |
| `src/tcc_evolution/features.py` | contratos histórico, solicitação e perfil puro |
| `src/tcc_evolution/evaluation.py`, `src/tcc_evolution/temporal.py` | métricas, calibração separada e backtests maduros |
| `src/tcc_evolution/bands.py`, `src/tcc_evolution/poc1.py` | bandas experimentais, PSI e sensibilidade sem escolha de limiar |

## Sequência recomendada

```bash
make test
make validate
```

Quando houver mudança que dependa dos dados:

```bash
python scripts/prepare_dataset.py --dataset "$LENDING_CLUB_DATA_PATH"
make notebook
make test
make validate
```

Revise `git status` e `git diff`; pare para aprovação antes de commit ou
publicação.

## Verificações sem dataset

`make test` e `make validate` cobrem hashes históricos, estrutura e execução
salva dos notebooks, dependências, segurança textual, arquivos proibidos e
whitespace. A CI não executa o dataset nem requer credenciais.

Exportações ficam em `artifacts/html/`, ignorado pelo Git:

```bash
make export
make validate-html
```

A auditoria rejeita caminhos locais, credenciais e identificadores individuais.

## Operações que exigem o dataset

`LENDING_CLUB_DATA_PATH` deve apontar para o arquivo descrito em
`docs/data-guide.md`. `make notebook` atualiza somente o evolutivo.
`make reproduce-reconstructed` executa a reconstrução em cópia temporária,
nunca in-place.

## Execução no Google Colab

Use os comandos canônicos do `README.md`. Mantenha dataset e credenciais apenas
na sessão e selecione memória ampliada para a execução integral.

## Solução de problemas

### Memória insuficiente

Use amostra determinística no desenvolvimento, feche outros kernels e não
reduza silenciosamente a população da execução final.

### Caminho do dataset

Confirme `test -f "$LENDING_CLUB_DATA_PATH"`. Sem variável, a descoberta aceita
exatamente um arquivo compatível em `data/raw/`. Nunca grave caminho absoluto
em notebook ou documentação.

### Kernel Jupyter

Ative o ambiente Python 3.12, confirme `python -m pip check` e execute todas as
células em kernel novo. O timeout integral é 1.800 segundos.

## Limitações e resultados irreproduzíveis

- a amostra histórica de 10.000 da PoC 1 não pode ser identificada exatamente;
- a execução histórica final da PoC 2 não preserva outputs suficientes;
- somente B possui faixa de juros publicada;
- não há validação externa, regulatória, de fairness ou impacto financeiro.

Detalhes: `docs/final-validation.md` e `docs/result-comparison.md`.

## Regras para alterações futuras

- verifique integridade antes e depois;
- não versione dados, credenciais, modelos binários ou HTML;
- ajuste transformadores e reamostragem somente no treino;
- não escolha modelo, corte ou limiar pelo teste;
- documente mudanças de contrato e preserve a proveniência;
- acrescente novas pesquisas ao final do notebook evolutivo.
