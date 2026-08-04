# Revisão da Fase 2 — pipeline de dados

Data da validação: 4 de agosto de 2026. Commit base: `9ed7362`.

## Resultado

O pipeline foi implementado e validado com fixtures sintéticas e com o dataset real completo. O arquivo externo permanece ignorado; somente seu manifesto agregado foi adicionado. Nenhuma credencial, linha do dataset, notebook reconstruído ou modelo foi criado no repositório durante esta fase. A fase foi posteriormente aprovada e encerrada no commit `a3890e4`.

## Entregas

- pacote editável `tcc_reconstruction` com código em `src/`;
- resolução configurável do dataset;
- validação antecipada de 51 colunas;
- manifesto opcional com SHA-256;
- leitura em chunks e amostragem determinística;
- filtros de status do empréstimo e verificação de renda;
- conversões de taxa, data/ano e limites FICO;
- definição explícita de `fico`;
- resumo antes/depois, memória, ausências e erros de conversão;
- CLI que imprime somente metadados agregados;
- testes unitários sem dados reais;
- documentação de aquisição e operação atualizada.
- manifesto reproduzido do dataset real, incluindo resolução da divergência Q1/Q3.

## Critérios de aceite

| Critério | Evidência | Estado |
|---|---|---|
| caminho sem dependência absoluta | argumento, variável e descoberta relativa testados | aprovado |
| falha clara para esquema incompleto | teste lista múltiplas colunas ausentes | aprovado |
| definição de `fico` | média documentada e testada dos limites low/high | aprovado |
| evitar coluna removida antes de acesso | nenhuma remoção/imputação nesta fase; ausências apenas sinalizadas | aprovado |
| carregamento consciente de memória | 51 colunas, chunks de 100.000 e amostra de 10.000 | aprovado em fixture e dataset real |
| filtros e conversões | populações e valores antes/depois testados | aprovado em fixture e dataset real |
| amostra determinística | mesmo resultado com chunks de 7 e 13 linhas | aprovado |
| contagens do dataset real | 2.925.493 → 1.860.764 → 1.272.273 → amostra 10.000 | aprovado |
| manifesto real com hash/shape/período | 142 colunas; 2007-06–2020-09; SHA-256 registrado | aprovado |

## Validações executadas

- instalação editável pelo `requirements.txt`;
- `pip check` sem dependências quebradas;
- 12 testes `unittest` aprovados;
- testes executados transformando `ResourceWarning` e `DeprecationWarning` em erro;
- Ruff sem erros e formatação aprovada para o código novo;
- CLI `--help` aprovada;
- ausência do dataset retorna código 1 e orientação de configuração;
- gzip verdadeiro e CSV real com sufixo `.gzip` detectados e testados;
- JSON da CLI não contém linhas nem caminho absoluto do fixture;
- `git diff --cached --check` sem erros;
- integridade do PDF e dos notebooks protegidos confirmada.

## Comandos principais

```bash
python -m pip install -r requirements.txt
python -m pip check
python -m unittest discover -s tests -v
python scripts/prepare_dataset.py --help
python scripts/verify_source_integrity.py
git diff --cached --check
```

## Decisões importantes

- `fico = (fico_range_low + fico_range_high) / 2` é código novo e hipótese explícita.
- Falhas de conversão em valores não nulos encerram a execução por padrão.
- Ausências originais são preservadas e contabilizadas.
- Colunas com ausência ≥ 90% são sinalizadas, não removidas.
- O filtro de renda verificada é padrão; removê-lo exige opção explícita.
- A CLI percorre todo o arquivo para contagens globais, mas mantém somente a amostra solicitada.
- O formato é detectado pela assinatura binária; a extensão `.gzip` do dataset publicado não representa sua compressão real.

## Evidência da execução real

- ZIP: 505.408.012 bytes; SHA-256 `2d11fedfb54381bf0708b41ca906b047349e35957ec9718d790dcff63d692941`.
- CSV: 1.773.470.505 bytes; SHA-256 `5878af2a088f8ab5214c9337289fb8b5eb6c6338fd3f417b6cdc18513dc6f`.
- Shape bruto: 2.925.493 × 142, igual ao informado na tese.
- Período bruto: junho de 2007 a setembro de 2020; o conteúdo confirma Q3 apesar do slug Q1.
- Status aceitos: 1.497.783 `Fully Paid`, 362.548 `Charged Off` e 433 `Default`, totalizando 1.860.764.
- Após renda verificada: 734.249 `Source Verified` e 538.024 `Verified`, totalizando 1.272.273; 588.491 `Not Verified` foram excluídos.
- Conversões inválidas: zero; colunas selecionadas com ausência ≥ 90%: nenhuma.

## Limites e pendências

- Uma nova publicação no mesmo slug deverá ser revalidada pelos hashes, pois o Kaggle pode substituir arquivos.
- O ZIP tem múltiplos membros e precisa ser extraído antes da leitura pelo pandas.
- O modo completo acumula os registros filtrados em memória; não é recomendado para desenvolvimento.
- Imputação, codificação, split e balanceamento pertencem à Fase 5.
- Nenhuma figura ou tabela da tese foi reproduzida nesta fase.

## Checklist de encerramento

- [x] escopo limitado à Fase 2;
- [x] fontes protegidas inalteradas;
- [x] implementação e testes adicionados;
- [x] documentação atualizada;
- [x] dados, credenciais e artefatos fora do diff;
- [x] validações estáticas e dinâmicas aprovadas;
- [x] execução com o dataset real e manifesto agregado;
- [x] diff aprovado pelo responsável;
- [x] commit da Fase 2 criado após aprovação (`a3890e4`).
