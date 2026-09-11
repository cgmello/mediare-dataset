# Backlog v23 — nomenclatura de pedidos e fontes

## Problema

A sigla `RR` possui hoje dois significados diferentes:

- `RR` como fonte: **Resposta do Requerido**;
- `RR01`, `RR02` etc. no catálogo: pedidos contrapostos formulados pelo
  requerido.

Isso dificulta a leitura do painel e do Termo pelo mediador.

## Alteração proposta

- Manter `RP01`, `RP02` etc. para **pedidos do requerente**.
- Renomear pedidos contrapostos do requerido de `RR01`, `RR02` etc. para
  `CR01`, `CR02` etc., significando **Contrapedido do Requerido**.
- Manter os identificadores de fontes sem alteração:
  - `PR`: Petição do Requerente;
  - `RR`: Resposta do Requerido;
  - `DR`: Documentos do Requerente;
  - `DD`: Documentos do Requerido.

## Regra material preservada

Um `CR` somente deve existir quando o requerido solicitar uma providência
afirmativa contra o requerente, como pagamento, devolução, declaração,
obrigação de fazer ou de não fazer. Negar responsabilidade, atribuir culpa ou
pedir improcedência continua sendo defesa registrada na fonte `RR`, mas não
gera contrapedido.

## Compatibilidade necessária

- Novas análises da v23 devem produzir `CR01...`.
- Painéis históricos das versões anteriores que já contenham `RR01...` devem
  continuar legíveis pelos getters e scripts off-chain.
- Validadores, prompts, consolidação, auditoria, referências cruzadas, Termo de
  Opção e scripts do mediador devem aceitar o histórico sem converter `RR` de
  fonte em pedido.
- A alteração é de nomenclatura e legibilidade; não deve mudar conclusões,
  valores, opções ou regras de consenso.

## Regras materiais identificadas na auditoria da v22

A auditoria manual dos 20 casos sentinela está documentada em
`V22_CATALOG_AUDIT.md`. Ela acrescenta os seguintes itens à v23:

- não transformar improcedência, negativa de responsabilidade, inexigibilidade,
  redução ou recálculo puramente defensivo em `CR`;
- tratar simples abatimento como defesa ligada ao `RP`, mas admitir `CR` quando
  houver pedido autônomo de devolução de saldo ou reconhecimento de crédito;
- consolidar principal, multa, juros e correção quando forem acessórios de uma
  única cobrança;
- não transformar componentes internos, perícias, meios de prova ou diligências
  em pedidos autônomos;
- não separar declaração/reconhecimento e pagamento quando ambos descreverem o
  mesmo resultado material;
- preencher valor numérico apenas quando o montante final estiver literalmente
  expresso, sem multiplicação ou inferência feita pelo modelo;
- exigir que `REVISOR_CATALOGO` informe tipo da falha, ID afetado, âncora da
  fonte e correção esperada;
- reservar `disagree` para falhas que alterem materialmente o conjunto
  negociável, aceitando decomposições alternativas fiéis e sem dupla contagem.

## Casos de regressão prioritários

- Corrigir: 0008, 0017, 0023, 0026, 0029, 0033 e 0035.
- Preservar: 0001, 0015, 0018, 0020, 0024 e 0031.

## Resultado implementado

A implementação e o gate estão documentados em `V23_GATE_REPORT.md`.
A v23.1 atingiu 6/7 correções e preservou 6/6 controles. O caso 0029 continua
como regressão prioritária porque um líder ainda pode calcular R$ 23.400,00 a
partir de 12 × R$ 1.950,00 apesar da proibição textual.

Próximos itens:

- os 20 sentinelas da v22 foram repetidos com o snapshot v23.1 congelado;
- a repetição técnica dos casos 0013, 0017, 0033 e 0048 foi concluída sem
  alterar o IC: 0017 e 0048 recuperaram painéis, enquanto 0013 e 0033
  permaneceram falhas técnicas;
- tratar a resposta vazia do DeepSeek em 0013 e a deriva de formato da auditora
  Mistral em 0033 como problemas de robustez separados da semântica RP/CR;
- manter 0017 como sentinela de consistência dos revisores: a fonte contém
  pedido contraposto expresso, mas a nova rodada teve 1 aprovação, 2 objeções
  e 1 erro de formato, após 3–1 anterior, sem mudança da regra material;
- registrar o caso 0050 como risco de sobreposição: `RP03` pede todos os
  valores pagos e `RP04` inclui entrada e parcelas dentro dos danos materiais;
- avaliar regra determinística para impedir valor catalogado que não esteja
  literalmente ancorado na fonte, sem depender apenas da instrução à LLM.

## Resultado dos 20 sentinelas

A análise pareada completa está em `V23_CASE_BY_CASE_ANALYSIS.html`. A v23.1
obteve 13/20 maiorias, contra 11/20 da v22, sem perder maioria em caso algum.
As objeções `REVISOR_CATALOGO` caíram de 16 para 6. Dos sete `Disagree`, quatro
foram falhas técnicas, dois foram dominados por rigor excessivo ou variação de
revisor e um foi misto. A direção do catálogo foi aprovada, mas a robustez
técnica e a sobreposição do caso 0050 permanecem no backlog.

## Resultado da repetição técnica

As quatro repetições usaram o mesmo snapshot e o mesmo modelo líder da rodada
original. Foram 33 chamadas, 346.023 tokens e US$ 0,772431658492:

| Caso | Estabilidade técnica | Leitura RP/CR |
|---|---|---|
| 0013 | falha persistente; nenhum painel | não avaliável |
| 0017 | painel recuperado; 1 aprovação, 2 objeções, 1 erro | 4 RP + 2 CR fiéis ao pedido contraposto; variação dos revisores |
| 0033 | falha persistente na auditora | rodada anterior sustenta 1 RP e nenhum falso CR |
| 0048 | painel recuperado; 4–0 | RP01 + CR01/CR02 coerentes com as pretensões expressas |

## Evolução técnica v24

A v24 resolveu os três alvos sem reabrir a semântica RP/CR da v23:

- 0013 passou a formar painel; o empate 2–2 remanescente é de mérito/revisão;
- 0017 obteve aprovação unânime 4–0 com 4 RP + 2 CR preservados;
- 0033 obteve aprovação unânime 4–0 e manteve a ressalva como reformulação;
- 0048 confirmou a recuperação do DeepSeek e terminou 4–0 em repetição limpa;
- 0050 preservou conflitos explícitos de dupla contagem e terminou 4–0.

Próximo item: repetir os 20 sentinelas com o snapshot v24 antes de qualquer
promoção ao Studio. O relatório está em `V24_TECHNICAL_GATE_REPORT.md`.
