# Roteiro de teste — Mediare IC v10.1

## Arquivo para deploy

Use `ic_v10_1.py`. O `ic.py` continua sendo a baseline v9 e não foi alterado.

Classe do contrato: `MediareCommitteeV101`.

Revisao atual: `10.1.2-experimental`, no mesmo arquivo e classe. Faca um novo
deploy para executar a correcao; contratos ja implantados continuam com o
codigo anterior.

### O que muda na 10.1.2

- `necessita_informacao` e `fora_de_escopo` exigem `valor_centavos: null` nas
  teses. Campo ausente ou zero nessas decisoes e erro de schema.
- `negar` continua exigindo zero; concessao monetaria exige inteiro positivo.
- `faixa_centavos` de um pedido fica `null` se qualquer lente nao o quantificou.
  `estado_valor` distingue `quantificado`, `indeterminado`, `fora_de_escopo` e
  `nao_monetario`.
- `faixa_quantificada_centavos` preserva apenas os valores conhecidos, quando
  existirem. O termo os identifica como parciais, sem apresentar uma faixa
  completa ou substituir abstencoes por zero.
- `totais_por_lente_centavos` ficam `null` para lentes com pedido monetario
  pendente/fora de escopo. A faixa total so existe quando todos os cenarios
  monetarios estiverem quantificados. Pedidos nao monetarios nao entram na soma;
  se forem os unicos pedidos, o total e "nao se aplica".
- O EP compara os estados de valor e as faixas conhecidas. `null` nunca equivale
  a `[0, 0]` ou a faixa positiva. A tolerancia de 15% para valores positivos
  permanece; as demais condicoes de consenso nao foram afrouxadas.
- Os prompts orientam avaliar responsabilidade compartilhada a partir dos
  resumos, distinguindo falta de nexo de falta de proporcao/valor. Nao ha rateio
  fixo nem instrucao de reproduzir o percentual do gabarito.

Motivacao: o painel do lider na transacao do caso 0005
`0xf88c596d1af19781887d6ae20ab0d5486af2f4a006d7172967b31c0b8661deec`
mostrou tres abstencoes transformadas em `[0, 0]`. O snapshot estava em
`COMMITTING`, com `NO_MAJORITY`; nao comprova finalizacao nem identifica os
motivos individuais dos votos. O protocolo nao grava os paineis dos validadores.

Foram executados 25 testes unitarios, incluindo respostas simuladas de LLM.
Eles verificam formato, consolidacao, documento e equivalencia; nao demonstram
melhora de merito ou consenso com modelos reais. O harness v9 nao e compativel
diretamente com esse schema novo; uma futura comparacao off-chain deve manter
abstencoes separadas das negacoes e salvar seus proprios paineis.

No reteste de `analyze_case("5")`, se houver novamente tres abstencoes, espere
faixas e totais `null`, e "valor indeterminado" no Termo de Opcao obtido por
`get_case()` apos uma transacao aceita. So um resultado financeiro efetivamente
quantificado pode ser comparado ao valor do gabarito.

### Correcoes preservadas da 10.1.1

A 10.1.1 corrigiu omissoes nos prompts (limites de texto, centavos e formatos),
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
- faixa em centavos ou `null` para valor indeterminado/nao aplicavel;
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
