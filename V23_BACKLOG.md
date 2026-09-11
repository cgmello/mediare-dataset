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

- repetir os 20 sentinelas da v22 com o snapshot v23.1 congelado;
- tratar separadamente falhas de lente/auditoria e latência do DeepSeek;
- avaliar regra determinística para impedir valor catalogado que não esteja
  literalmente ancorado na fonte, sem depender apenas da instrução à LLM.
