# Revisão da Fase 4 — PoC 1 baseada em conteúdo

Data da validação: 4 de agosto de 2026. Commit base: `c10a14d`.

## Resultado

A PoC 1 foi reconstruída a partir da tese, pois não existe no notebook recuperado. A implementação usa os quatro atributos publicados, reproduz os exemplos sintéticos Vinicius/Elder, executa a amostra determinística real de 10.000 e gera as Figuras 20–22. Nenhuma etapa da PoC 2 ou modelagem foi iniciada.

## Regras explícitas

- grade ordinal: A=1, B=2, ..., G=7;
- fronteiras de elegibilidade inclusivas;
- Campanha 1: renda ≥ 30.000, utilização ≤ 60%, contas em 24 meses ≥ 1, grade B–E;
- Campanha 2: renda ≥ 60.000, utilização ≤ 35%, contas em 24 meses ≥ 5, grade A–C;
- qualificação principal: elegibilidade completa e distância ≤ 20;
- valores ausentes: não elegíveis e sem distância calculada;
- amostra: pipeline da Fase 2, 10.000 linhas, semente 42, renda verificada.

## Reconstrução forense da distância

Os números da Tabela 7 permitem inferir a convenção usada:

- diferença absoluta entre renda e renda mínima, inclusive quando a renda excede o mínimo;
- diferença entre utilização e a referência da campanha;
- penalidade apenas para falta de contas em relação ao mínimo;
- penalidade ordinal apenas quando a grade fica fora da faixa aceita.

A Campanha 2 usa máximo de elegibilidade 35%, mas suas distâncias publicadas só fecham com referência de utilização 40. Com essa referência, as quatro distâncias são reproduzidas:

| Perfil | Campanha 1 | Campanha 2 |
|---|---:|---:|
| Vinicius | 5,000000 | 30000,004017 |
| Elder | 30000,010433 | 5,000000 |

Com referência estrita 35, as distâncias da Campanha 2 seriam 30000,006933 e 0. A divergência permanece explícita; a implementação não altera o critério máximo de 35%.

## Execução real

Ausências na amostra: `all_util` em 4.716 linhas e `acc_open_past_24mths` em 237. Renda e grade não possuem ausências.

| Resultado | Campanha 1 | Campanha 2 |
|---|---:|---:|
| elegíveis pelos critérios | 1.790 | 178 |
| critérios + distância bruta ≤ 20 | 36 | 10 |
| somente distância bruta ≤ 20 | 64 | 88 |
| critérios + distância normalizada ≤ 20 | 1.790 | 178 |

A Campanha 1 fica próxima do “cerca de 40” quando todos os critérios são aplicados. A Campanha 2 só se aproxima do “quase 90” no modo diagnóstico que ignora a elegibilidade explícita. Por isso, o resultado principal não é forçado para reproduzir a barra publicada.

## Normalização

A análise de sensibilidade divide cada componente pelo intervalo interquartil da amostra: renda 49.000, utilização 27, contas recentes 4 e grade 2. A mediana da distância muda de 35.000,001157 para 1,108458 na Campanha 1 e de 20.400,025024 para 1,312271 na Campanha 2.

Reutilizar o limiar bruto 20 na escala normalizada aprova todos os elegíveis. Isso demonstra que o limiar depende da escala. Um novo limiar não foi escolhido porque exigiria objetivo de negócio ou validação externa ausente das fontes.

## Entregas

- funções reutilizáveis em `src/tcc_reconstruction/poc1.py`;
- testes de fronteira, codificação, exemplos, ausências e normalização;
- seção executada da Fase 4 em `notebooks/tcc-reconstructed.ipynb`;
- Figuras 20–22 e Tabela 7;
- comparação atualizada em `docs/result-comparison.md`.

## Checklist de encerramento

- [x] escopo limitado à Fase 4;
- [x] fontes protegidas inalteradas;
- [x] quatro atributos e duas campanhas documentados;
- [x] limiar 20 e operadores de fronteira testados;
- [x] exemplos Vinicius/Elder reproduzidos;
- [x] amostra real determinística de 10.000 executada;
- [x] distância bruta comparada à alternativa normalizada;
- [x] resultados publicados comparados sem serem forçados;
- [x] diff aprovado pelo responsável;
- [x] commit da Fase 4 criado após aprovação (`49ec59e`).
