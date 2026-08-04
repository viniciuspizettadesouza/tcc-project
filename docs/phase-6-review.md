# Revisão da Fase 6 — Score e ofertas personalizadas

Data da validação: 4 de agosto de 2026. Commit base: `7e5f911`.

## Resultado

A probabilidade de inadimplência do XGBoost reduzido foi calibrada com sigmoide em uma partição exclusiva de 20% do treino da Fase 5. O modelo subjacente foi reajustado nos 80% restantes; o teste original, com 254.455 registros, permaneceu intocado. Nenhum modelo binário ou registro individual foi versionado.

| Probabilidade | ROC AUC de teste | Brier score |
|---|---:|---:|
| não calibrada | 0,706847 | 0,218330 |
| calibrada por sigmoide | 0,706847 | 0,153092 |

A transformação sigmoide preserva a ordenação e, por isso, o AUC. A redução de 0,065238 no Brier score indica probabilidades mais coerentes com a frequência observada no teste, sem usar o teste no ajuste.

## Sentido do score e categorias

O valor recuperado `PD × 1000` é mantido como **score de risco**, no qual maior significa pior. O score usado com as categorias publicadas é seu inverso explícito, `(1 − PD) × 1000`, denominado **score de crédito**, no qual maior significa melhor.

| Categoria da tese | Faixa aplicada por `pd.cut`, fechada à direita | Registros no teste |
|---|---|---:|
| A | (825, 900] | 66.468 |
| B | (725, 825] | 63.158 |
| C | (600, 725] | 45.975 |
| D | (475, 600] | 23.277 |
| E | (350, 475] | 4.116 |
| F | (225, 350] | 4 |
| G | [175, 225] | 0 |
| fora abaixo | < 175 | 0 |
| fora acima | > 900 | 51.457 |

As 51.457 linhas acima de 900 são retidas com rótulo explícito. A ausência de G e os quatro casos em F impedem confirmar as afirmações da tese sobre comportamento nas categorias extremas. A escala linear é uma representação interpretável da PD calibrada, não equivalência a um score de bureau.

## Taxa e exemplo publicado

A tese diz que a campanha promocional foi criada para D/E, mas só publica evidência numérica para B: score 725–825 e taxas 13,33%–16,08%. A reconstrução não inventa taxas para as demais categorias.

A direção da interpolação não é publicada. Foi adotada a direção coerente com score de crédito: score maior recebe taxa menor.

| Score | Categoria/limite publicado | Taxa reconstruída |
|---:|---|---:|
| 725 | limite inferior de B | 16,0800% a.a. |
| 750 | B | 15,3925% a.a. |
| 825 | limite superior de B | 13,3300% a.a. |

O `pd.cut` recuperado usa intervalos fechados à direita, então 725 pertence formalmente a C e valores imediatamente acima pertencem a B. Para testar a fórmula publicada, os dois limites 725 e 825 são aceitos como extremos matemáticos da oferta. Essa ambiguidade de fronteira é preservada, não ocultada.

## Figuras 26–29

- Figuras 26 e 27: boxplots de `int_rate` e DTI por categoria, com outliers ocultos somente na renderização;
- Figura 28: proporção de `home_ownership` dentro de cada categoria;
- Figura 29: proporção de `application_type` dentro de cada categoria;
- `dexplot` foi substituído por tabelas cruzadas normalizadas e barras empilhadas mantidas pelo pandas/matplotlib;
- categorias sem observações permanecem explícitas na tabela, mesmo sem caixa ou barra desenhável.

As figuras são análises descritivas do teste e não demonstram causalidade. Como G está vazia e F tem quatro observações, não se reproduzem as conclusões publicadas sobre os dois extremos.

## Checklist de encerramento

- [x] escopo limitado à Fase 6;
- [x] fontes protegidas inalteradas;
- [x] calibração ajustada fora do teste;
- [x] sentidos de risco e crédito explicitados;
- [x] inversão PDF/notebook reconciliada;
- [x] linhas fora de 175–900 tratadas;
- [x] taxas restritas à evidência publicada;
- [x] limites, direção e score 750 testados;
- [x] conflito D/E versus B registrado;
- [x] Figuras 26–29 executadas com o dataset real;
- [x] diff aprovado pelo responsável;
- [x] commit da Fase 6 criado após aprovação (`7c94882`).
