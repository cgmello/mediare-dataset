# Auditoria de catálogo da v22 — 20 casos sentinela

## Objetivo e limite

Esta auditoria compara, caso a caso, os pedidos escritos nos quatro resumos de
entrada, o catálogo produzido pela v22, as revisões dos quatro modelos e os
catálogos das execuções v20/v21. O objetivo é distinguir:

- problema real ou provável do catálogo;
- rigor excessivo ou interpretação incompatível com a regra material desejada;
- variação de modelo ou falha técnica.

Não há gabarito jurídico externo para a decomposição dos pedidos. Portanto, as
classificações abaixo são avaliações de fidelidade ao texto resumido e ao
critério operacional definido para a Mediare, não conclusões jurídicas.

## Resultado executivo

A v22 concluiu 20 casos: 18 painéis válidos, 15 saídas úteis e 11 maiorias
locais. Nos 18 painéis revisáveis ocorreram 16 votos `REVISOR_CATALOGO`,
distribuídos por 12 casos.

Dos 12 casos questionados por catálogo:

- 6 continham problema real ou provável no catálogo;
- 6 tinham catálogo defensável e a objeção foi rigor excessivo ou consequência
  de uma ambiguidade da instrução;
- além deles, o caso 0023 continha um contrapedido indevido que nenhum revisor
  classificou como problema de catálogo.

Assim, `REVISOR_CATALOGO` é um sinal útil, mas não pode ser lido como prova de
erro. Nesta amostra, metade dos casos sinalizados justificava correção material,
e houve também um falso negativo relevante.

## Comportamento dos revisores

| Revisor | Revisões | `REVISOR_CATALOGO` | Taxa |
|---|---:|---:|---:|
| Claude Sonnet 4.6 | 14 | 0 | 0,0% |
| GLM 5.3 | 14 | 1 | 7,1% |
| GPT-5.4 | 14 | 2 | 14,3% |
| DeepSeek v4 Pro | 16 | 3 | 18,8% |
| Mistral Medium 3.5 | 14 | 10 | 71,4% |

O Mistral concentrou 62,5% de todas as objeções de catálogo. Cinco de suas dez
objeções coincidem com problemas reais ou prováveis; as outras cinco recaem
sobre catálogos defensáveis. Portanto, ele não deve ser simplesmente removido:
é um revisor sensível que também gera muitos falsos positivos. A v23 deve exigir
uma justificativa verificável para a objeção.

## Análise individual

| Caso | Catálogo v22 | Diagnóstico | Classificação principal | Leitura simples |
|---|---|---|---|---|
| 0001 | 5 RP + 3 RR | Mistral: catálogo incompleto | Excesso de rigor / variação | Os cinco pedidos do requerente e os três pedidos contrapostos expressos aparecem no catálogo. A mesma estrutura ocorreu nas cinco versões; só a revisão atual do Mistral a tratou como incompleta. |
| 0007 | 3 RP | Sem objeção de catálogo | Correto | Rescisão, desocupação e danos a apurar foram separados de forma fiel. |
| 0008 | 3 RP | DeepSeek e Mistral: incompleto | Problema provável de granularidade | A multa de 10% foi separada da cobrança de aluguéis e encargos, embora apareça como acessório do mesmo pedido monetário. A v21-schema produziu a composição mais coerente: rescisão + uma cobrança consolidada. |
| 0013 | Sem painel | Líder falhou na lente probatória | Variação técnica do modelo | O DeepSeek gerou JSON inválido nas três tentativas. Não houve catálogo para julgar. |
| 0015 | 6 RP + 1 RR | GPT: incompleto | Ambiguidade refinada na v23 | Os seis pedidos de cobrança estão presentes. Revisão, exclusão de honorários, redução de multa e compensação de valores já pagos apenas reduzem o saldo cobrado; como não há crédito próprio ou devolução de saldo, a regra refinada da v23 não cria CR. |
| 0017 | 4 RP + 6 RR | Mistral: incompleto | Problema real de excesso de fragmentação | Cinco componentes internos da retenção/compensação da caução viraram pedidos separados. O correto é consolidar o dano material em um contrapedido e manter o dano moral como outro. |
| 0018 | 1 RP | DeepSeek e Mistral: incompleto | Excesso de rigor causado por ambiguidade | Extinção, improcedência, inexigibilidade e recálculo foram respostas defensivas ao único pedido de pagamento. Segundo a regra material definida, não devem gerar CR autônomo, mesmo estando sob um tópico chamado “Pedidos”. |
| 0020 | 1 RP | Mistral: incompleto | Excesso de rigor / variação | Principal, juros, correção e retornos contratuais compõem a mesma cobrança. As versões anteriores fragmentavam o pedido em quatro; a consolidação da v22 é a evolução desejada. |
| 0022 | 3 RP | Sem objeção de catálogo | Correto | Cobrança vencida, devolução do imóvel e parcelas vincendas são resultados negociáveis distintos. As respostas do requerido não pedem prestação autônoma contra o requerente. |
| 0023 | 1 RP + 1 RR | Sem objeção de catálogo | Problema real não detectado | A perícia contábil é diligência/meio de apuração do RP01, não prestação autônoma contra o requerente. Deve permanecer associada ao pedido principal, sem gerar CR. |
| 0024 | 3 RP | Mistral: incompleto | Excesso de rigor / variação | Inexigibilidade dos meses, recálculo proporcional da multa e devolução do saldo da caução estão representados. A defesa pela cobrança integral não cria CR. |
| 0026 | 4 RP + 2 RR | Mistral: incompleto | Problema real de duplicação | “Reconhecer obrigação de terceiro” e “excluir a requerida da responsabilidade” são duas formulações do mesmo resultado defensivo/declaratório e não deveriam ser dois itens autônomos. |
| 0029 | 1 RP + 2 RR | GPT e Mistral: incompleto | Problema real, com ambiguidade adicional | A consolidação das defesas foi adequada, mas o catálogo calculou R$ 23.400,00 a partir de 12 × R$ 1.950,00. Como o valor não estava literalmente expresso, o campo numérico deveria ser nulo e a fórmula ficar na descrição. |
| 0031 | 1 RP | Mistral: incompleto | Excesso de rigor / variação | Há um único pedido expresso de pagamento de R$ 2.490,00. A alegação de que a dívida não venceu é defesa. O mesmo catálogo passou sem objeção nas três v21 válidas. |
| 0033 | 1 RP + 1 RR | GLM e DeepSeek: incompleto | Problema real e variação de líder | O pedido de declarar a dívida inexigível é a própria defesa contra o RP01, não contrapedido autônomo. A v21-catalog havia produzido corretamente apenas RP01; o item voltou na v22 com outro líder. |
| 0035 | 2 RP | Mistral: incompleto | Problema real e inconsistência do modelo | Reconhecer o valor devido e determinar seu pagamento são partes do mesmo pedido de cobrança, não dois resultados independentes. O próprio Mistral liderou a mesma decomposição em dois RP na v21-schema e a rejeitou como revisor na v22. |
| 0046 | 4 RP | Sem objeção de catálogo | Correto | Rescisão, inexigibilidade, retirada da negativação e dano moral são quatro providências distintas. |
| 0047 | 3 RP | Sem objeção de catálogo | Correto | Desfazimento da venda/devolução do veículo, restituição do preço e dano moral foram identificados separadamente. |
| 0048 | Sem painel | Líder falhou no catálogo | Variação técnica/provedor | O DeepSeek retornou texto vazio nas três tentativas da etapa de catálogo. Não houve catálogo v22 para comparar. |
| 0050 | 5 RP | Sem objeção de catálogo | Correto | Resolução da venda, cancelamento do financiamento, restituição, dano material e dano moral correspondem aos cinco resultados expressos. A sexta rubrica observada em versões anteriores era fragmentação. |

## Síntese por causa

### Problemas reais ou prováveis da v22

- **0008:** acessório monetário separado do pedido principal;
- **0017:** componentes internos transformados em seis contrapedidos;
- **0023:** diligência contábil transformada em contrapedido;
- **0026:** duas formulações do mesmo resultado catalogadas separadamente;
- **0029:** valor calculado pelo modelo em vez de valor literalmente informado;
- **0033:** defesa transformada em contrapedido;
- **0035:** reconhecimento e pagamento da mesma dívida separados em dois RP.

### Objeções provavelmente rigorosas demais

- **0001, 0015, 0018, 0020, 0024 e 0031.**

O ponto comum não é aleatório: a instrução ainda permite que um revisor entenda
“pedido expresso” em sentido processual amplo, enquanto a Mediare quer catalogar
somente resultados materiais e autônomos que possam virar objeto de negociação.

### Variação técnica

- **0013:** JSON inválido gerado pelo líder;
- **0048:** resposta vazia do provedor/modelo.

Esses casos não dizem nada sobre a qualidade da regra de catálogo. Devem entrar
na trilha de robustez de geração e retry, não na avaliação semântica da v22.

## Recomendações para a v23

1. Definir `CR` como providência autônoma pedida pelo requerido contra o
   requerente. Improcedência, inexistência de responsabilidade, redução,
   inexigibilidade e recálculo defensivo permanecem vinculados ao RP.
2. Tratar compensação de forma contextual: simples abatimento reduz o RP;
   devolução de saldo ou crédito autônomo pode gerar CR.
3. Consolidar principal e acessórios no mesmo pedido quando formarem uma única
   cobrança; separar somente resultados que possam ser aceitos de forma
   independente na mediação.
4. Proibir a transformação de componentes de cálculo, meios de prova, perícias
   e diligências em RP/CR autônomos.
5. Preencher `valor_pedido_centavos` apenas quando o valor final estiver
   literalmente expresso na fonte. Valores derivados ficam como fórmula textual.
6. Substituir o diagnóstico nu `catalogo: incompleto` por uma lista estruturada
   contendo tipo (`OMISSAO`, `EXCESSO`, `DUPLICACAO`, `GRANULARIDADE` ou
   `VALOR_INFERIDO`), ID afetado, âncora da fonte e correção esperada.
7. Orientar o revisor a votar `disagree` por catálogo somente quando a falha
   alterar materialmente o que pode ser negociado. Uma decomposição alternativa,
   mas fiel e sem dupla contagem, deve ser aceita.
8. Criar testes de regressão determinísticos com os sete casos problemáticos e
   os seis falsos positivos antes de repetir chamadas pagas.

## Critério sugerido para o próximo experimento

A v23 deve passar primeiro por estes 13 casos sem chamadas de campanha ampla:

- correções esperadas: 0008, 0017, 0023, 0026, 0029, 0033 e 0035;
- preservação esperada: 0001, 0015, 0018, 0020, 0024 e 0031.

O avanço é satisfatório se corrigir pelo menos seis dos sete problemas sem
degradar mais de um dos seis catálogos de preservação. Só então vale repetir os
20 sentinelas via OpenRouter.
