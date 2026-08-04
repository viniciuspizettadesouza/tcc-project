# Histórico da reconstrução

## Protocolo e estado final

A reconstrução avançou em fases revisáveis. Cada fase exigiu integridade das fontes, testes proporcionais ao escopo, atualização da comparação, revisão do diff, aprovação e commit próprio. As Fases 0–8 foram concluídas em 4 de agosto de 2026.

| Fase | Escopo | Commit |
|---:|---|---|
| 0 | investigação forense e planejamento | `b29ff0b` |
| 1 | fundação reprodutível | `9ed7362` |
| 2 | pipeline de dados | `a3890e4` |
| 3 | análise exploratória | `c10a14d` |
| 4 | PoC 1 baseada em conteúdo | `49ec59e` |
| 5 | PoC 2, baseline e XGBoost | `7e5f911` |
| 6 | score e ofertas personalizadas | `7c94882` |
| 7 | organização narrativa | `6b0eca9` |
| 8 | validação integral | `134222c` |

O commit `cc127b8` esclareceu posteriormente a proveniência e o nome do artefato recuperado. O commit `84eeb04` consolidou a documentação de encerramento sem alterar resultados científicos.

## Fase 0 — investigação forense

Foram lidas as 84 páginas do PDF e as 93 células do artefato recuperado. Figuras 9–29, Tabelas 3–9, PoC 1, PoC 2, score e interpolação foram mapeados. A análise estabeleceu a tese como fonte metodológica primária, o notebook recuperado como evidência parcial e a execução reproduzível como limite do que pode ser afirmado.

O artefato recuperado não executava integralmente: a célula 35 terminava em `KeyError: 'max_bal_bc'`, a PoC 1 estava ausente, não havia regressão logística treinada e as células finais não conservavam outputs. Lacunas e conflitos permanecem detalhados em `reconstruction-analysis.md`.

## Fase 1 — fundação reprodutível

Foram estabelecidos Python 3.12, dependências diretas fixadas, instalação editável, manifesto de fontes, `.gitignore`, instruções locais/Colab e o verificador independente de integridade.

| Fonte protegida | Tamanho | SHA-256 |
|---|---:|---|
| `TCC_Vinicius_P_Souza.pdf` | 1.854.902 bytes | `abfed8559ee14018fb9204dd061aa6003d6ceb65e6cb63a9722d02e8e3182bdf` |
| notebook recuperado | 139.488 bytes | `7c58b4b0d0a9cae0accd49f77cd46fd8fd02316961ec588394463b5e9456f330` |

Uma cópia técnica temporária foi removida após se confirmar que não era fonte independente. O histórico Git e o manifesto preservam a auditoria. Instalação limpa, imports científicos, JupyterLab e `pip check` foram aprovados; autenticação Kaggle e execução remota do Colab permaneceram dependentes do usuário.

## Fase 2 — pipeline de dados

O pacote `tcc_reconstruction` passou a resolver o dataset por argumento, variável ou descoberta relativa; validar 51 colunas antes da leitura; detectar compressão pelo conteúdo; carregar em blocos; filtrar status e renda verificada; converter taxa e data; derivar FICO; e produzir amostra determinística e manifesto agregado.

Evidência do arquivo real:

- ZIP: 505.408.012 bytes; SHA-256 `2d11fedfb54381bf0708b41ca906b047349e35957ec9718d790dcff63d692941`;
- CSV: 1.773.470.505 bytes; SHA-256 `5878af2a088f8ab5214c9337289fb8b5eb6c6338fd3f417b6cdc18513dc6f`;
- bruto: 2.925.493 × 142, de 2007-06 a 2020-09;
- status finais: 1.860.764 registros;
- status finais e renda verificada: 1.272.273 registros;
- conversões inválidas e colunas selecionadas com ausência ≥ 90%: zero.

A definição nova `fico = (fico_range_low + fico_range_high) / 2` foi explicitada. Ausências são preservadas, falhas de conversão não nulas encerram por padrão e o modo completo é reservado a máquinas com memória suficiente. O contrato operacional está em `data-guide.md`.

## Fase 3 — análise exploratória

As Figuras 9–19 foram executadas na ordem da tese. Figuras 9–15 usam a população de 1.860.764 status finais; Figuras 16–19 usam 1.272.273 registros com renda verificada. Gráficos densos usam amostra determinística de 100.000 apenas para renderização; correlações e agregados usam a população completa.

Resultados característicos:

| Análise | Resultado |
|---|---:|
| `loan_amnt` × `funded_amnt` | 0,999700 |
| `fico_range_low` × `fico_range_high` | 0,999999923 |
| `total_acc` × `open_acc` | 0,708775 |
| inadimplentes | 362.981 |
| DTI mediano / p99 / máximo | 17,71 / 39,61 / 999 |

Tabelas 3–6 usam esquema e perfis agregados, não linhas de clientes. Transformações `log1p` são cópias analíticas, e os extremos permanecem nos resumos mesmo quando os eixos são limitados para legibilidade.

## Fase 4 — PoC 1

A PoC 1 foi reconstruída exclusivamente da tese com `annual_inc`, `all_util`, `acc_open_past_24mths` e `grade`. As duas campanhas usam fronteiras inclusivas, grade ordinal A=1…G=7, limiar de distância 20 e amostra de 10.000 com semente 42.

A Tabela 7 só fecha quando a Campanha 2 mantém elegibilidade máxima de 35%, mas usa 40 como referência da distância. Essa divergência foi preservada. Na execução real, a regra completa aprovou 36 perfis na Campanha 1 e 10 na Campanha 2; o diagnóstico apenas por distância produziu 64 e 88. A normalização por intervalo interquartil foi apresentada como sensibilidade, sem escolher novo limiar de negócio.

## Fase 5 — PoC 2

O Anexo A contém 42 preditores originais após excluir o alvo; `monthly_load` produz 43 entradas efetivas. A separação é estratificada 80/20 com semente 1. O treino contém 1.017.818 registros, o teste desbalanceado 254.455, e `RandomUnderSampler` atua somente no treino. Imputadores, one-hot e escalador são ajustados depois da separação.

| Modelo | Atributos | ROC AUC por probabilidade | Acurácia |
|---|---:|---:|---:|
| regressão logística | 43 | 0,704407 | 0,637154 |
| XGBoost completo | 43 | 0,711818 | 0,647109 |
| XGBoost reduzido | 12 | 0,706897 | 0,642593 |

O AUC histórico de aproximadamente 0,65 foi explicado pelo uso incorreto de rótulos em vez de probabilidades. A reconstrução mantém esse cálculo apenas como comparação. Importância usa ganho agregado por variável fonte; `int_rate` lidera com 0,294044. Circularidade potencial de `int_rate` e `sub_grade` em decisão pré-oferta permanece como limitação.

## Fase 6 — score e ofertas

O XGBoost reduzido foi calibrado por sigmoide em partição exclusiva do treino. O AUC de teste permaneceu 0,706847 e o Brier score caiu de 0,218330 para 0,153092.

`PD × 1000` é nomeado score de risco, em que maior é pior. Seu inverso `(1 − PD) × 1000` é o score de crédito usado com A–G. Scores fora de 175–900 recebem rótulo explícito; 51.457 ficaram acima de 900, F teve quatro registros e G nenhum.

A única faixa de juros publicada pertence à categoria B. A interpolação adotada dá taxa menor a score de crédito maior: 725 → 16,08%, 750 → 15,3925% e 825 → 13,33% a.a. O conflito entre campanha D/E e evidência numérica B, assim como a fronteira ambígua de 725, permanece visível.

## Fase 7 — narrativa

O notebook foi organizado em quinze seções: projeto, reprodutibilidade, aquisição, configuração, carregamento, EDA, pré-processamento, PoC 1, PoC 2, score, resultados, comparação, limitações, conclusões e proveniência. Cada seção declara origem e tipo como recuperado, adaptado ou novo.

A fase alterou somente Markdown: 39 células de código, suas fontes, contagens e outputs foram preservados; Markdown passou de 35 para 45 células. Código reutilizável permaneceu nos módulos e variáveis foram definidas antes do uso.

## Fase 8 — validação integral

O notebook foi executado em kernel novo com o dataset real: 39/39 células, zero erros, 20 figuras PNG e uma Plotly. A auditoria confirmou Figuras 9–29, Tabelas 3–9, quinze seções, dependências/sementes, ausência de caminhos locais e nenhuma inclusão de dataset, segredo ou modelo.

A comparação final contém 30 itens: 11 reproduzidos, 10 parciais, 5 divergentes, 2 conflitantes e 2 irreproduzíveis. Resultados e limitações completos permanecem em `final-validation.md` e `result-comparison.md`.

## Critérios consolidados

- fontes protegidas permaneceram intactas;
- testes e execuções foram registrados por fase;
- documentação e comparação foram atualizadas antes do encerramento;
- diffs foram revisados e aprovados;
- cada fase recebeu commit próprio;
- dados, credenciais e modelos binários permaneceram fora do Git;
- nenhuma equivalência exata foi alegada sem evidência.
