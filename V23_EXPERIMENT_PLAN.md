# Plano experimental v23 — catálogo material auditável

## Escopo controlado

A v23 parte integralmente da v22 e altera somente a identificação e a revisão
dos pedidos. Lentes, consolidação decisória, opções, reparo, auditoria e Termo de
Opção permanecem inalterados.

Mudanças:

- `RP01...` continua identificando pedidos do requerente;
- `CR01...` passa a identificar somente contrapedidos materiais e autônomos do
  requerido;
- defesa, improcedência, redução, recálculo e inexigibilidade ligados ao RP não
  criam CR;
- acessórios, componentes, reconhecimento e pagamento do mesmo resultado são
  consolidados;
- perícias, provas e diligências não viram pedidos;
- valor final calculado ou inferido não entra em `valor_pedido_centavos`;
- `REVISOR_CATALOGO` exige tipo, ID, fonte, evidência e correção verificáveis.
- `VALOR_INFERIDO` só é aceito quando o item realmente contém valor numérico;
  não pode reprovar um item cujo campo já seja `null`. Essa objeção impossível é
  normalizada deterministicamente, sem alterar qualquer outro tipo de falha.
- a mesma normalização se aplica quando a evidência do revisor contém literalmente
  o valor que ele chamou de inferido;
- declaração que apenas nega/extingue o RP e preliminar processual nunca geram CR;
- retenção de caução expressamente formulada como contrapedido é preservada;
- ajuste de cálculo e devolução/pagamento de saldo continuam resultados separados.

## Compatibilidade

Novos painéis aceitam apenas `RP` e `CR`. Os scripts off-chain continuam
tratando IDs como identificadores opacos e, por isso, permanecem capazes de ler
painéis históricos com `RR01...` sem conversão ou perda.

## Gate inicial de 13 casos

Corrigir: 0008, 0017, 0023, 0026, 0029, 0033 e 0035.

Preservar: 0001, 0015, 0018, 0020, 0024 e 0031.

A candidata avança se:

- corrigir pelo menos seis dos sete problemas;
- degradar no máximo um dos seis casos de preservação;
- não produzir falha estrutural do schema do revisor.

Depois desse gate, a próxima etapa é repetir os 20 sentinelas da v22. Somente
uma v23 aprovada nos dois checkpoints deve avançar para 50 casos e Studio.
`v23_cases.json` mantém os outros 37 casos depois do gate para permitir retomada
da mesma campanha congelada.

## Rechecagem dirigida v23.1

`v23_1_cases.json` inicia por 0033, 0024 e 0001, preservando para cada caso o
mesmo modelo líder observado na v23.0.2. A rechecagem usa `--case-limit 3` para
medir somente as correções de inexigibilidade defensiva, separação do saldo da
caução e retenção expressamente contraposta.

## Gate técnico v23.2.1

A v23.2.1 mantém o prompt e o validador de catálogo RP/CR idênticos à v23.1.
O gate separa três dimensões:

- disponibilidade do líder: 0013 e 0048 não podem voltar a consumir todo o
  teto de saída em raciocínio sem produzir JSON;
- coerência estrutural da auditora: 0033 deve preservar a preocupação de forma
  fail-closed sem inventar conflito com outro pedido;
- consistência dos revisores: 0017 só pode receber `PEDIDO` com falha de
  catálogo estruturada, fonte, evidência e correção.

Os controles 0048 e 0050 verificam, respectivamente, repetibilidade do
DeepSeek e preservação de sobreposição real. Após aprovação, a próxima etapa é
repetir os mesmos 20 sentinelas antes de qualquer promoção ao Studio.
