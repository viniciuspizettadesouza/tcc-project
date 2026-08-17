# Escopo da evolução

## O que é estimado

O target é **inadimplência**: `Fully Paid = 0` e `Charged Off`/`Default = 1`.
Os modelos estimam risco de crédito; não aprendem aceite, conversão ou
preferência por campanhas.

```text
perfil ou solicitação → probabilidade de inadimplência → score/faixa → regra → oferta
```

“Recomendação” designa apenas a camada final de regras. Avaliar adesão exigiria
dados de campanha ofertada, resposta e contratação.

## Contratos de atributos

| Cenário | Atributos | Momento de uso |
|---|---:|---|
| Histórico | 43 | referência forense da reconstrução |
| Solicitação conhecida | 38 | valor, prazo, finalidade e tipo de aplicação já informados |
| Perfil puro | 34 | antes de existir uma solicitação |

São 43 atributos no histórico, 38 na solicitação conhecida e 34 no perfil puro.

Nos dois cenários pré-oferta são removidos cinco campos pós-decisão:
`int_rate`, `installment`, `sub_grade`, `initial_list_status` e `monthly_load`.
O perfil puro remove adicionalmente `loan_amnt`, `term`, `purpose` e
`application_type`.

Os demais 34 atributos são informações temporais, cadastrais ou do arquivo de
crédito consideradas disponíveis no perfil. O alvo `default` nunca entra nos
preditores. A tabela completa, com disponibilidade e justificativa individual
dos 43 atributos, é gerada no notebook por
`tcc_evolution.features.feature_availability_table()`.

Esses contratos são hipóteses analíticas da evolução, não afirmações do TCC ou
garantias operacionais. Uma implantação precisa confirmar a origem e o momento
real de disponibilidade de cada campo.

## Fora do escopo

Fairness regulatória, impacto financeiro, adesão real e validação brasileira
permanecem fora deste ciclo por falta de dados adequados.
