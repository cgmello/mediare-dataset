# Plano experimental v22 híbrida

## Snapshot

- Fonte implantável: `ic_v22.py`.
- Versão implantável: `22.0.0-experimental` (variante híbrida).
- SHA-256: `66c4300440f36fb95c927e5ab464e11cbad0fe6be2e77c36c3b1061101d0a466`.
- Base técnica: v20 acrescida do schema fechado da `v21-schema`.

## Contribuições incorporadas

1. **Schema:** `catalogo=completo|incompleto` e lista fechada de falhas
   `PEDIDO|CONCLUSAO|FONTES|OPCAO`, preservando a reprovação fail-closed.
2. **Catalog:** unidade material de pedido, união somente de repetições
   materialmente idênticas, preservação de providências autônomas e criação de
   RR apenas quando o requerido pedir providência afirmativa.
3. **Options:** opção declaratória com `pagador=null` e
   `beneficiario=null`, redação como reconhecimento consensual e validação
   determinística correspondente.

## Exclusões deliberadas

- A ampliação experimental de bases monetárias provenientes de DR/DD não foi
  incorporada, porque não mostrou ganho agregado na v21-options.
- Pedidos autônomos nunca podem ser unidos apenas por compartilharem fatos,
  fundamentos ou base econômica.
- Permanecem inalteradas as barreiras da v20 para fonte literal, valor,
  percentual, dupla contagem, polos e auditoria.

## Ordem da próxima campanha OpenRouter

`v22_cases.json` continua contendo exatamente os casos 0001–0050, mas coloca
primeiro 20 sentinelas de regressão/ganho. O primeiro comando deverá usar
`--case-limit 20`; a campanha só será retomada para os 30 restantes após esse
checkpoint.

Gates para completar os 50:

- zero falha estrutural do novo schema de revisão;
- 100% das opções declaratórias com polos neutros;
- zero omissão de providência expressa na inspeção dos catálogos alterados;
- nenhuma regressão grave de validade ou utilidade nos sentinelas.

Gates da comparação completa:

- pelo menos 42/50 painéis válidos;
- pelo menos 38/50 saídas úteis;
- maioria local igual ou superior aos 20/50 da v20;
- zero falha estrutural do revisor e zero opção declaratória com polos
  artificiais.

Somente após aprovação desses gates a v22 poderá ser congelada para o Studio
nos casos 0101–0150.
