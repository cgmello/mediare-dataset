# v27 — análise dos três casos `UNDETERMINED` no Studio

Data: 2026-09-21  
Campanha: `res_studio_v27_random100`  
Amostra: 100 casos aleatórios, seed `20260920`

## Resultado executivo

A v27 concluiu 97/100 casos com consenso válido: 95 `ACCEPTED` e dois
`FINALIZED`. Os únicos `UNDETERMINED` foram `0013`, `0019` e `0144`.

Os três têm a mesma causa operacional:

- todos os líderes executaram o contrato com `SUCCESS`;
- os quatro ciclos de líder foram consumidos em cada caso;
- os votos contrários apontaram `MEDIARE_DIAG:REVISOR_CATALOGO`;
- não houve rejeição do Termo de Opção (`EP1`), crash ou erro de JSON;
- os catálogos dos líderes perderam pedidos monetários expressos antes da
  revisão.

Portanto, não são três falhas independentes nem casos sem solução. São três
manifestações de duas regras excessivamente amplas da normalização do catálogo.

## Caso `0013` — locação residencial

### O que as partes pediram

O requerente formulou, entre outros, pedidos separados de:

- três aluguéis vencidos, multa moratória de 10% e juros de 1% ao mês;
- multa contratual da cláusula 11;
- CPFL, SAAE e IPTU;
- taxa de pintura.

### O que os quatro líderes catalogaram

Os quatro painéis mantiveram rescisão, desocupação, aluguéis e pintura. Nenhum
deles manteve a multa autônoma da cláusula 11 nem os débitos de CPFL, SAAE e
IPTU. Os IDs saltam, por exemplo, de `RP03` para `RP06`, evidenciando que itens
extraídos pela LLM foram removidos pela normalização posterior.

### Diagnóstico

A regra que consolida “multa” e “encargos” com uma cobrança anterior considera
qualquer RP monetário precedente, sem confirmar que se trata da mesma obrigação.
Assim, ela confunde acessórios dos aluguéis com resultados separadamente
negociáveis. O mérito posterior — inclusive eventual rejeição por falta de prova
ou bis in idem — não autoriza apagar o pedido do catálogo.

Classificação: **defeito real e determinístico de consolidação**.

## Caso `0019` — locação comercial

### O que as partes pediram

Além de desocupação, R$ 528.915,69 de aluguéis/encargos vencidos e R$ 26.119,64
de IPTU, o requerente pediu:

- R$ 105.783,13 de honorários **contratuais**;
- aluguéis e encargos vincendos até a efetiva desocupação.

### O que os quatro líderes catalogaram

Todos mantiveram somente desocupação, débito vencido e IPTU. Todos omitiram os
honorários contratuais e a obrigação vincenda. Um líder ainda criou CRs a partir
de defesas processuais; os demais não cometeram esse excesso, mas também foram
rejeitados pelas omissões.

### Diagnóstico

Há dois problemas de especificação:

1. o marcador genérico “honorários advocatícios” remove tanto sucumbência e
   despesas judiciais — corretamente fora do catálogo — quanto uma verba
   contratual expressamente cobrada da outra parte, que pode ser negociada;
2. a consolidação de “encargos” elimina a pretensão vincenda sem incorporá-la à
   descrição do débito principal.

Classificação: **defeito real de escopo e consolidação**, agravado em uma rodada
por excesso do catalogador.

## Caso `0144` — cessão de direitos sobre imóvel

### O que as partes pediram

O requerente pediu rescisão, reintegração, indenização pelo uso, IPTU/condomínio,
multas contratuais e honorários contratuais. O requerido formulou reconvenção
para restituição de 90% dos R$ 931.000,00 pagos, ou ao menos 75%.

### O que os quatro líderes catalogaram

Os quatro catálogos foram semanticamente estáveis e mantiveram os quatro
primeiros RPs e o `CR01` de restituição. Todos omitiram as multas contratuais e
os honorários contratuais. Em 29 votos contrários observados nos três casos,
todos apontaram catálogo; neste caso houve apenas um voto favorável isolado na
primeira rodada.

### Diagnóstico

As duas omissões reproduzem exatamente as regras amplas já vistas:

- “multa” é absorvida por existir algum RP monetário anterior, mesmo com objeto
  diferente;
- “honorários advocatícios” são removidos sem distinguir verba contratual de
  providência exclusiva do processo judicial.

Classificação: **defeito real e determinístico de escopo/consolidação**.

## Correção recomendada para a próxima versão

1. Distinguir honorários contratuais expressamente cobrados da contraparte de
   honorários sucumbenciais, custas e outras providências exclusivas do juízo.
2. Consolidar multa, juros, correção e encargos somente quando houver identidade
   verificável da obrigação principal; não usar apenas a existência de qualquer
   RP monetário anterior.
3. Preservar multa civil ou contratual autônoma, tributos/consumos com objeto
   próprio e obrigação vincenda; esta última pode integrar o RP principal desde
   que a descrição preserve explicitamente o período futuro.
4. Criar regressões específicas para `0013`, `0019` e `0144`, exigindo que esses
   pedidos sobrevivam à normalização e que defesas processuais continuem sem CR.

Antes de nova promoção ao Studio, a correção deve passar pelos três casos
dirigidos e por um conjunto sentinela, para provar que não reabre duplicações de
acessórios já resolvidas nas versões anteriores.

## Limite da análise

O Studio registra o diagnóstico público do revisor (`REVISOR_CATALOGO`), mas não
o texto privado de sua justificativa. A causa acima é inferida de evidência
convergente: pedidos literais das fontes, catálogos decodificados das quatro
rodadas, IDs removidos e regras determinísticas da v27. Não foi feita chamada
adicional ao OpenRouter e, portanto, esta análise não gerou custo de API.
