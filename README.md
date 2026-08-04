# Reconstrução do TCC — recomendação de campanhas de crédito

Este repositório reúne as fontes e o planejamento para reconstruir, de forma rastreável e reproduzível, o notebook associado ao TCC **“Recomendação de campanha de crédito para perfis de clientes selecionados: utilizando técnicas de aprendizado de máquina e ciência de dados”**.

A reconstrução não deve ser apresentada como uma cópia byte a byte do notebook perdido. Ela será uma nova implementação baseada nas evidências disponíveis, com diferenças e resultados não reproduzidos explicitamente documentados.

## Estado atual

| Item esperado | Estado | Observação |
|---|---|---|
| Tese | presente | [`TCC_Vinicius_P_Souza.pdf`](TCC_Vinicius_P_Souza.pdf) |
| Notebook recuperado | presente com nome divergente | [`notebooks/Copy of Trabalho Data Mining.ipynb`](notebooks/Copy%20of%20Trabalho%20Data%20Mining.ipynb); deve permanecer imutável |
| Dataset Lending Club | ausente, como esperado | não deve ser versionado |
| Notebook reconstruído | ainda não criado | destino futuro: `notebooks/tcc-reconstructed.ipynb` |
| Repositório Git funcional | não | o diretório `.git/` está vazio e `git status` não reconhece este diretório como repositório |

O notebook recuperado contém evidência útil para a análise exploratória e para parte da PoC 2, mas não representa sozinho o trabalho final descrito na tese. A PoC 1, a regressão logística e a interpolação de taxas de juros, por exemplo, não estão implementadas nele.

## Documentação

- [`docs/reconstruction-analysis.md`](docs/reconstruction-analysis.md): inventário forense, matriz tese–notebook, lacunas e conflitos.
- [`docs/implementation-plan.md`](docs/implementation-plan.md): execução faseada, critérios de aceite e pontos de revisão.
- [`docs/dataset-acquisition.md`](docs/dataset-acquisition.md): obtenção e tratamento seguro do dataset externo.
- [`docs/result-comparison.md`](docs/result-comparison.md): contrato para comparar resultados reconstruídos com a tese.
- [`AGENTS.md`](AGENTS.md): regras operacionais para futuras sessões de implementação.

## Fontes de verdade e prioridade

1. A tese define a metodologia e os resultados finais pretendidos.
2. O notebook recuperado é evidência de implementação e de proveniência, não uma fonte automaticamente correta.
3. Execuções reproduzíveis determinam o que pode ser afirmado sobre a reconstrução.
4. Quando as fontes conflitarem, o conflito deve permanecer visível; nenhum número deve ser ajustado manualmente para coincidir com o PDF.

## Fluxo de trabalho

O trabalho deve avançar uma fase por vez. Ao final de cada fase: executar as validações previstas, revisar o diff, atualizar a comparação de resultados e solicitar aprovação. O commit da fase só deve ser criado após essa aprovação.

Esta entrega é apenas a investigação e o planejamento. Nenhum notebook reconstruído, pipeline ou modelo foi implementado ainda.
