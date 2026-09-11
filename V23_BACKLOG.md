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
