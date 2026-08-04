# Plano de implementação faseado

## Princípio de execução

Cada fase é uma unidade revisável. A próxima fase só começa depois de: critérios de aceite satisfeitos, revisão do diff, atualização da documentação de resultados, aprovação do responsável e commit próprio.

## Estado de execução

As **Fases 0–8 estão concluídas**. O plano abaixo permanece como registro do escopo e dos critérios usados durante a reconstrução; frases prospectivas descrevem o estado existente quando cada fase foi planejada, não o estado atual do repositório.

| Fase | Estado | Commit de encerramento |
|---:|---|---|
| 0 | concluída | `b29ff0b` |
| 1 | concluída | `9ed7362` |
| 2 | concluída | `a3890e4` |
| 3 | concluída | `c10a14d` |
| 4 | concluída | `49ec59e` |
| 5 | concluída | `7e5f911` |
| 6 | concluída | `7c94882` |
| 7 | concluída | `6b0eca9` |
| 8 | concluída | `134222c` |

O commit posterior `cc127b8` esclareceu a proveniência e o nome do artefato recuperado sem alterar os resultados da reconstrução.

## Fase 0 — Investigação forense e planejamento

Entregas:

- inventário das fontes e hashes;
- leitura integral da tese e das 93 células recuperadas;
- matriz de rastreabilidade em `docs/reconstruction-analysis.md`;
- plano de dados, comparação de resultados e regras para agentes;
- identificação de bloqueios estruturais.

Critérios de aceite:

- todas as figuras 9–29 e tabelas 3–9 estão mapeadas;
- PoC 1, PoC 2, score e interpolação possuem evidência/lacunas registradas;
- nenhuma fonte original foi modificada;
- nenhuma alegação de reprodução foi feita sem execução.

Bloqueio registrado na investigação: o `.git/` inicialmente disponível estava vazio. Situação resolvida antes da Fase 1; o repositório agora está em `main`, rastreando `origin/main`.

## Fase 1 — Fundação reprodutível

Entregas:

- confirmar o hash de `notebooks/tcc-recovered-from-colab.ipynb` sem alterar seus bytes nem criar uma segunda fonte;
- registrar SHA-256 antes e depois da cópia;
- criar `requirements.txt` ou `pyproject.toml` com versões compatíveis;
- validar `.gitignore` contra dados, modelos e credenciais;
- completar instruções locais e Colab no README;
- criar verificação automática de que o notebook recuperado permanece inalterado.

Decisões necessárias:

- se o artefato recuperado será preservado e duplicado como controle técnico de integridade, ou apenas verificado pelo hash;
- versão mínima do Python e estratégia de pinagem;
- uso de scripts auxiliares em `src/` ou funções autocontidas no notebook.

Decisões adotadas na Fase 1:

- preservar somente o artefato recuperado do TCC; usar manifesto de hash e histórico Git para integridade, sem manter duplicata no estado final;
- usar Python 3.12, fixando em `requirements.txt` as dependências diretas validadas nessa versão;
- usar um script Python independente e um manifesto JSON para verificar as fontes;
- reservar funções de análise para o notebook ou módulos futuros, conforme a complexidade das próximas fases.

Critérios de aceite:

- ambiente limpo instala dependências;
- notebook recuperado mantém SHA-256 `7c58b4b0d0a9cae0accd49f77cd46fd8fd02316961ec588394463b5e9456f330`;
- dataset/credenciais não aparecem no diff;
- README permite preparar ambiente local e Colab.

## Fase 2 — Pipeline de dados

Entregas:

- caminho de dados configurável;
- manifesto da fonte e validação de esquema;
- carregamento consciente de memória;
- conversão de `int_rate` e `issue_d`;
- filtro para `Fully Paid`, `Charged Off` e `Default`;
- filtro de `verification_status` documentado;
- limpeza, conversões e amostra determinística de desenvolvimento;
- resumo antes/depois por operação.

Critérios de aceite:

- ausência de caminhos absolutos;
- falha antecipada e legível para colunas ausentes;
- definição explícita de `fico`;
- nenhuma imputação tenta acessar coluna previamente removida;
- contagens e esquema ficam registrados sem versionar dados.

Decisões adotadas na Fase 2:

- validar o cabeçalho completo antes da leitura dos registros;
- ler somente a união de 51 colunas necessárias às fases planejadas, em blocos de 100.000 linhas;
- aplicar os filtros de status e verificação antes das conversões mais custosas;
- definir `fico` como a média de `fico_range_low` e `fico_range_high`, mantendo ausente quando faltar um limite;
- não remover nem imputar colunas nesta fase; apenas contabilizar e sinalizar ausência ≥ 90%;
- usar amostragem determinística por hash de identificador, posição da linha e semente;
- detectar compressão pela assinatura do arquivo, porque o CSV publicado usa a extensão enganosa `.gzip`;
- não exibir nem versionar linhas do dataset na CLI ou nos testes;
- registrar em manifesto apenas hashes e agregados reproduzidos: 2.925.493 × 142, período 2007-06–2020-09 e conteúdo confirmado até Q3.

## Fase 3 — Análise exploratória

Entregas, na ordem da tese:

1. distribuição de `loan_amnt` por ano;
2. correlação `loan_amnt` × `funded_amnt`;
3. correlação `fico_range_low` × `fico_range_high`;
4. correlação `total_acc` × `open_acc`;
5. razões/finalidades associadas à inadimplência, com população explicitamente filtrada;
6. mapa de empréstimos por estado;
7. distribuição de DTI;
8. renda anual antes/depois de `log1p`;
9. contas abertas antes/depois de `log1p`;
10. tabelas de dados antes/depois do processamento.

Critérios de aceite:

- títulos e ordem correspondem às Figuras 9–19;
- correlações são recalculadas, não fixadas em texto;
- população de cada gráfico é declarada;
- APIs modernas substituem `seaborn.distplot`;
- tabelas não expõem dados além do necessário.

## Fase 4 — PoC 1: recomendação baseada em conteúdo

Entregas:

- atributos `annual_inc`, `all_util`, `acc_open_past_24mths` e `grade`;
- campanhas e limiar documentados;
- reprodução dos exemplos Vinicius/Elder;
- execução sobre amostra determinística de 10.000;
- Figuras 20–22 e Tabela 7;
- comparação entre distância bruta descrita na tese e alternativa normalizada.

Critérios de aceite:

- Campanha 1: renda mínima 30.000, utilização máxima 60%, ao menos 1 conta em 24 meses, grau B–E;
- Campanha 2: renda mínima 60.000, utilização máxima 35%, ao menos 5 contas em 24 meses, grau A–C;
- limiar de distância 20 é testado conforme a tese;
- codificação de `grade`, regra de desigualdade e semente da amostra ficam explícitas;
- resultados “cerca de 40” e “quase 90” são comparados, nunca forçados.

Observação: as distâncias publicadas para Vinicius/Elder mostram uso de escalas brutas dominadas por renda. A versão fiel deve ser preservada para comparação, enquanto a versão normalizada deve ser apresentada como análise de sensibilidade/adaptação.

## Fase 5 — PoC 2: baseline e XGBoost

Entregas:

- alvo binário documentado;
- separação treino/teste estratificada e determinística;
- pipelines sem vazamento para imputação e codificação;
- `RandomUnderSampler` somente no treino;
- regressão logística como baseline real;
- XGBoost com objetivo de classificação binária;
- seleção/redução de atributos rastreável;
- importância de atributos, relatório, matriz de confusão e ROC/AUC por probabilidades;
- comparação com métricas da tese.

Critérios de aceite:

- 43 atributos e `monthly_load` são reconciliados com o Anexo A;
- `monthly_load = ((installment * 12) / annual_inc) * 100`, com regra explícita para renda zero;
- transformadores são ajustados somente no treino;
- FICO e variáveis categóricas têm semântica preservada;
- regressão logística e XGBoost têm objetos e resultados nomeados separadamente;
- métricas antigas calculadas com rótulos, se reproduzidas, aparecem apenas como comparação histórica.

## Fase 6 — Score e ofertas personalizadas

Entregas:

- probabilidade de inadimplência calibrada/interpretada;
- conversão explícita para score de risco ou score de crédito;
- categorias A–G e limites da tese;
- limites de taxa por categoria sustentados por evidência;
- interpolação linear e testes de fronteira;
- validação do exemplo de score 750;
- análises por taxa, DTI, moradia e tipo de aplicação (Figuras 26–29).

Critérios de aceite:

- maior risco não é chamado silenciosamente de melhor score;
- inversão entre categorias do PDF e do notebook é resolvida e documentada;
- taxas nos extremos e sentido da interpolação têm testes;
- conflito “campanha D/E” versus exemplo na categoria B é registrado;
- linhas fora de 175–900 recebem tratamento explícito.

## Fase 7 — Organização narrativa do notebook

Estrutura:

1. descrição do projeto;
2. notas de reprodutibilidade;
3. aquisição do dataset;
4. imports e configuração;
5. carregamento;
6. EDA;
7. limpeza e pré-processamento;
8. PoC 1;
9. PoC 2;
10. score e taxa personalizada;
11. resultados;
12. comparação com a tese;
13. limitações;
14. conclusões;
15. proveniência e notas de reconstrução.

Critérios de aceite:

- cada bloco informa se é recuperado, adaptado ou novo;
- variáveis são definidas antes do uso;
- narrativa em português preserva termos da tese;
- código reutilizável evita células monolíticas e repetição.

## Fase 8 — Validação final

Entregas:

- execução do notebook do início ao fim em ambiente limpo;
- checagem automatizada de estrutura e outputs;
- `docs/result-comparison.md` preenchido;
- README local/Colab completo;
- relatório final de limitações e itens irreproduzíveis.

Critérios de aceite:

- execução sem estado oculto;
- seeds e versões registradas;
- figuras têm títulos, eixos e dimensões legíveis;
- nenhum caminho absoluto, segredo, dataset ou binário de modelo foi versionado;
- ambas as PoCs estão presentes;
- todas as diferenças relevantes estão classificadas como reproduzidas, divergentes, parciais ou irreproduzíveis.

## Revisão consolidada das fases concluídas

Checklist aplicado às Fases 0–8 e consolidado após seus commits de encerramento:

- [x] escopo limitado à fase;
- [x] fonte recuperada inalterada;
- [x] testes/execuções anexados ao resumo;
- [x] documentação e comparação atualizadas;
- [x] `git diff --check` sem erros;
- [x] diff revisado pelo responsável;
- [x] aprovação recebida antes do commit;
- [x] um único commit de fase, sem mudanças alheias.
