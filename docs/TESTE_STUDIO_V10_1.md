# Roteiro de teste — Mediare IC v10.1

## Arquivo para deploy

Use `ic_v10_1.py`. O `ic.py` continua sendo a baseline v9 e não foi alterado.

Classe do contrato: `MediareCommitteeV101`.

Revisao atual: `10.1.1-experimental`, no mesmo arquivo e classe. Faca um novo
deploy para executar a correcao; contratos ja implantados continuam com o
codigo anterior.

A revisao corrige omissoes nos prompts (limites de texto, centavos e formatos),
aceita objeto JSON ou texto JSON valido sem reparar valores, e informa o erro
de formato ao modelo na segunda tentativa. Continua exigindo tres lentes
validas e conserva as regras de equivalencia da v10.1.

Em caso de falha, o rollback agora identifica a etapa, o campo e as duas
tentativas, por exemplo:

```text
LLM_INVALID_PANEL:lente=probatoria:1=RP01.comentario:TEXTO_1_A_240;2=RP01.comentario:TEXTO_1_A_240
```

`catalogo` indica falha na extracao; `lente=...` identifica a analise rejeitada;
`CHAMADA_...` indica excecao ao chamar o provedor; `JSON_INVALIDO` indica texto
que nao pode ser lido como JSON. O erro nao inclui o conteudo bruto do caso ou
a mensagem do provedor. Um `Disagree` isolado ainda pode significar divergencia
entre paineis ou falha local do validador: o booleano nao distingue esses motivos.

Motivacao: transacao do caso 0005
`0x635817c7409d12e54d09de8e50494a1dd429a4d9ceb7ed6126505942362b1faa`,
encerrada como `UNDETERMINED` com tres rotacoes e `LLM_INVALID_PANEL`.
O log original nao permite identificar qual resposta/campo causou a falha;
esta revisao ainda precisa de confirmacao com modelos reais no Studio.

Depois do deploy, chame:

```text
analyze_case("0134")
```

Quando a transação finalizar, consulte `get_case()` e guarde a resposta
completa.

## Casos sugeridos para a primeira rodada

| Caso | Motivo |
|---|---|
| `0134` | falso positivo grave da v9; gabarito patrimonial zero |
| `0041` | zero reproduzido incorretamente em várias versões/modelos |
| `0063` | zero reproduzido incorretamente em várias versões/modelos |
| `0005` | ouro; culpa concorrente e rateio documentado |
| `0033` | positivo que a v9 acertou ao centavo on-chain |
| `0001` | ouro; vários pedidos principais e contrapostos |

Comece por `0134`, depois `0005`. Eles exercitam, respectivamente, negação e
responsabilidade repartida sem exigir uma rodada grande.

## O que deve aparecer

O `get_case()` retorna:

- `status = termo_opcao_disponivel`;
- `painel`, com catálogo, três teses e consolidado;
- `termo_opcao`, montado deterministicamente sem outra chamada de LLM.

Para cada pedido, confira:

- se o catálogo separou corretamente os pedidos das razões jurídicas;
- `status`: passou, não passou, controvertido, necessita informação ou fora de
  escopo;
- faixa em centavos;
- posição e comentário das três lentes;
- referências PR, RR, DR e DD;
- flags como `ZERO_VERSUS_POSITIVO`.

## Evidência a registrar

Para cada execução, guarde:

1. ID do caso;
2. hash da transação;
3. status final (`FINALIZED` ou `UNDETERMINED`);
4. modelos configurados nos cinco validadores;
5. saída completa de `get_case()`;
6. tempo e custo informados pelo Studio;
7. observação manual sobre erros no catálogo ou na decisão.

## Limitação esperada

A v10.1 extrai o catálogo de pedidos por LLM porque os casos atuais ainda não
possuem IDs estruturados. O líder e os validadores precisam concordar sobre
quantidade, ordem, parte, modalidade e natureza dos pedidos. Se isso causar
`UNDETERMINED`, o resultado é útil: indica que a próxima iteração precisa
materializar o catálogo no dataset antes de executar o contrato.

## Comparação mínima com a v9

Para `0134`, `0041` e `0063`, a pergunta principal é: a lente auditora impede
ou pelo menos transforma a concessão indevida em `controvertido`, com faixa
incluindo zero?

Para `0005` e `0033`, a pergunta é: a segurança adicional preserva os acertos
positivos e o rateio já obtidos na v9?
