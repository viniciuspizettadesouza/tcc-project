# Plano de continuidade e fortalecimento do projeto

## Objetivo

Melhorar automação, manutenção e facilidade de execução da reconstrução concluída, sem publicar uma versão, criar tags ou alterar metodologia e resultados.

Este plano inicia um novo escopo após o encerramento das Fases 0–8. A reconstrução validada permanece como baseline. Alterações científicas ou novos experimentos devem ser tratados separadamente e não fazem parte deste plano.

## Limites do escopo

Não estão autorizados por este plano:

- criação de tags Git;
- criação de GitHub Release;
- push para repositório remoto;
- publicação de artefatos;
- mudança de licença;
- alteração de autoria ou metadados pessoais;
- alteração do artefato recuperado;
- mudança silenciosa de métricas, populações ou decisões metodológicas.

Qualquer uma dessas ações exigirá uma solicitação futura e aprovação explícita.

## Etapa 1 — Confirmar e proteger o baseline

- confirmar que `main` está limpa e contém o commit final da reconstrução;
- executar testes, integridade das fontes e auditoria final;
- registrar o commit usado como baseline de manutenção;
- verificar que o artefato recuperado, o dataset ignorado e os resultados permanecem protegidos;
- manter novos experimentos fora do baseline validado.

## Etapa 2 — Configurar integração contínua

Criar GitHub Actions que não dependa do dataset externo:

1. checkout do repositório;
2. configuração do Python 3.12;
3. instalação de `requirements.txt`;
4. execução de `python -m unittest discover -s tests -v`;
5. execução de `python scripts/verify_source_integrity.py`;
6. execução de `python scripts/validate_final_reconstruction.py`;
7. execução de `python -m pip check`;
8. execução de `git diff --check`.

A CI não deve executar integralmente o notebook porque o dataset não é versionado. A execução completa permanece um procedimento local/Colab documentado.

Adicionar o workflow ao repositório não autoriza push nem alteração de configurações remotas.

## Etapa 3 — Padronizar comandos locais

Adicionar um `Makefile` ou mecanismo equivalente com comandos previsíveis:

```text
make install
make test
make validate
make notebook
make export
```

Regras:

- `make notebook` exige `LENDING_CLUB_DATA_PATH` e inicia um kernel novo;
- `make export` gera HTML somente como artefato local em uma pasta ignorada pelo Git;
- nenhum comando baixa dados ou acessa credenciais implicitamente;
- os comandos devem funcionar a partir da raiz do repositório;
- nenhum comando cria tag, commit, push ou release.

## Etapa 4 — Melhorar a documentação de manutenção

- documentar a finalidade dos módulos em `src/tcc_reconstruction/`;
- registrar a sequência recomendada de testes e validações;
- explicar quais verificações funcionam sem o dataset;
- explicar como executar o notebook completo localmente e no Colab;
- criar uma seção de solução de problemas para memória, caminho do dataset e kernel Jupyter;
- manter limitações e itens irreproduzíveis visíveis.

## Etapa 5 — Fortalecer verificações automatizadas

- adicionar cobertura para comandos padronizados;
- validar que o HTML local não contém caminhos absolutos ou registros individuais;
- verificar que arquivos gerados permanecem ignorados;
- testar que nenhuma alteração afeta o artefato recuperado;
- manter a auditoria de datasets, credenciais e modelos binários;
- avaliar uma ferramenta leve de lint/formatação sem reformatar o artefato recuperado.

Novas dependências somente devem ser adicionadas quando trouxerem benefício claro e após revisão.

## Etapa 6 — Preparar artefatos exclusivamente locais

- testar a exportação do notebook executado para HTML;
- armazenar a saída em diretório ignorado;
- verificar ausência de caminhos locais e dados individuais;
- registrar o comando e o hash do arquivo apenas para conferência local, se útil;
- não anexar, enviar ou publicar o artefato.

## Etapa 7 — Revisar e encerrar a manutenção

Antes de qualquer commit:

- executar todos os testes e validadores;
- confirmar a integridade das fontes protegidas;
- auditar arquivos candidatos ao Git;
- apresentar o diff completo;
- aguardar aprovação explícita;
- sugerir um comando completo de commit.

O commit local encerra este plano. Tag, push e release permanecem fora do escopo.

## Critérios de conclusão

- [ ] baseline final confirmado;
- [ ] CI localmente validada e sem dependência do dataset;
- [ ] comandos locais documentados e testados;
- [ ] documentação de manutenção atualizada;
- [ ] HTML local reproduzível, seguro e ignorado;
- [ ] notebooks e fontes protegidas intactos;
- [ ] nenhum dataset, segredo ou modelo binário versionado;
- [ ] nenhuma tag, release ou ação remota criada;
- [ ] diff aprovado;
- [ ] commit local criado somente após aprovação.

## Possíveis trabalhos posteriores, fora deste plano

Se houver interesse futuro, criar um plano separado para:

- avaliação temporal dos modelos;
- modelo pré-oferta sem `int_rate` e `sub_grade`;
- análise de fairness e estabilidade;
- novos modelos ou otimização de hiperparâmetros;
- interface demonstrativa com dados sintéticos;
- eventual publicação ou compartilhamento externo.

Nenhum desses itens deve ser iniciado implicitamente durante o fortalecimento da manutenção.

## Prompt para iniciar a futura sessão

> Fortaleça a manutenção do projeto seguindo `docs/continuation-plan.md`. Preserve o artefato recuperado e não altere metodologia ou resultados. Implemente somente automação local, CI sem dataset, comandos padronizados, documentação de manutenção e exportação HTML local ignorada. Pare para revisão antes do commit. Não crie tag, push, release nem publique qualquer artefato.
