# Instruções para a reconstrução

## Escopo e fontes

- Trate `TCC_Vinicius_P_Souza.pdf` como a fonte primária da metodologia final pretendida.
- Trate `notebooks/tcc-recovered-from-colab.ipynb` como o artefato do TCC recuperado após a perda do notebook original durante uma manutenção do Google Colab.
- Trate `notebooks/tcc-reconstructed.ipynb` como o registro histórico imutável da reconstrução concluída nas Fases 0–8.
- Nunca altere, limpe outputs, reformate, renomeie ou reexecute in-place nenhum dos dois notebooks históricos.
- Crie toda evolução metodológica em `notebooks/tcc-evolved.ipynb`; o notebook reconstruído não é mais o artefato ativo.
- Consulte `docs/reconstruction-analysis.md` antes de implementar qualquer fase.
- Execute `python scripts/verify_source_integrity.py` antes e depois de cada fase.
- Execute `python -m unittest discover -s tests -v` após alterações no pipeline.

## Proveniência

- Identifique código como recuperado, adaptado ou novo na documentação/Markdown do notebook evolutivo.
- Não atribua ao autor da tese metadados de execução pertencentes a terceiros.
- Não fabrique métricas, figuras, tabelas ou equivalência exata.
- Registre divergências entre tese, notebook recuperado e nova execução em `docs/result-comparison.md`.
- Registre resultados posteriores ao encerramento da reconstrução em `docs/evolution-results.md`, sem reclassificar a comparação histórica.

## Segurança dos dados

- Não versione dataset completo, amostras com dados potencialmente sensíveis, modelos binários, credenciais, tokens Kaggle ou arquivos temporários grandes.
- Use caminho configurável para o dataset; não introduza caminhos locais absolutos.
- Valide o esquema antes de iniciar processamento custoso.
- Prefira leitura com seleção de colunas, tipos explícitos e amostragem determinística para desenvolvimento.

## Qualidade do código e da análise

- Fixe sementes aleatórias e registre versões das dependências.
- Separe treino e teste antes de ajustar imputadores, codificadores, escaladores, seleção de atributos ou reamostragem.
- Aplique balanceamento somente ao conjunto de treino.
- Use probabilidades ou `decision_function` para ROC e ROC AUC; não use rótulos de classe.
- Mantenha uma regressão logística como baseline interpretável e XGBoost como modelo não linear; não confunda previsões de um com as do outro.
- Explique o sentido do score: maior score de crédito deve significar menor risco, ou o valor deve ser nomeado explicitamente como score de risco.
- Não use APIs obsoletas registradas na análise forense.

## Execução por fases

- Consulte `docs/reconstruction-history.md` para o protocolo e as decisões das fases concluídas.
- Consulte `docs/evolution-history.md` para as fases E0 em diante.
- Para manutenção futura, siga `docs/maintenance.md` e limite cada mudança a uma unidade revisável.
- Ao final da fase, execute os testes/checagens correspondentes e apresente o diff para revisão.
- Aguarde aprovação antes de iniciar a próxima fase e antes de criar o commit da fase.
- Preserve mudanças do usuário e não reescreva histórico.
- Quando solicitado um commit, use uma mensagem objetiva e entregue também o comando completo e copiável.
