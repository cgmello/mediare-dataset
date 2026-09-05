# Mediare IC v10.2 — teste de opcoes condicionais

## Deploy

Arquivo independente: `ic_v10_2.py`.
Classe: `MediareCommitteeV102`.
Versao retornada: `10.2-experimental`.

Faca um novo deploy no Studio. `ic.py` (v9) e `ic_v10_1.py`
(v10.1.4) permanecem inalterados para comparacao. O arquivo novo e autocontido:
nao importa a baseline nem exige subir outros arquivos junto com o contrato.
A dependencia do SDK e o commit fixo dos casos sao os mesmos da v10.1.4.

Chame `analyze_case("5")`. Depois de uma execucao bem-sucedida, leia:

- `get_termo_opcao()`: texto do documento diretamente, sem envelope JSON interno;
- `get_case()`: versao, status, painel completo e termo, no formato anterior.

O Studio ainda pode representar a string de retorno com escapes. Isso nao
muda o documento. As duas consultas sao metodos de leitura, nao novas
transacoes de escrita. `analyze_case` continua retornando `null` e gravando
o resultado no estado. Resultado `ERROR` nao produz um novo termo.

## Mudanca funcional

Cada pedido tem duas camadas distintas:

1. Conclusao sobre o pedido: conceder, negar, necessita informacao ou fora de
   escopo, com o valor considerado devido por cada lente. `null` nao e zero.
2. Opcao de negociacao: proposta condicional, premissa, ressalva, fontes,
   base de calculo quando aplicavel e revisao auditora.

As tres lentes passam a trabalhar sequencialmente no mesmo EP:

1. **Probatoria:** separa suporte, controversia e lacuna, mantendo sua conclusao.
2. **Jurisprudencial:** recebe a analise probatoria, pode critica-la e acrescenta
   uma opcao por pedido. Uma conclusao indeterminada nao impede uma formula
   condicional ou uma diligencia util.
3. **Auditora/refutadora:** recebe ambas as analises e revisa especificamente
   a opcao jurisprudencial, alem de apresentar sua propria conclusao do pedido.

As lentes nao sao tres execucoes independentes nesta revisao: ha dependencia
entre elas. Isso permite auditar a proposta concreta, mas pode aumentar
ancoragem e correlacao; a comparacao experimental deve observar esse efeito.

O catalogo continua extraido por LLM. Ha uma opcao por pedido nesta primeira
v10.2, nao enumeracao ilimitada de cenarios. Os limites sao 16 pedidos, comentario
ate 1200 caracteres, textos de analise/opcao ate 800 e citacoes ate 600.
Os prompts pedem concisao: os limites nao sao metas de tamanho.

## Tipos de opcao

| Tipo | Conteudo apresentado ao mediador |
|---|---|
| `faixa` | Base citada, criterio documentado e intervalo calculado pelo contrato |
| `formula` | Base citada x participacao a negociar, sem atribuir percentual |
| `nao_monetaria` | Providencia condicional compativel com pedido nao monetario |
| `diligencia` | Pergunta concreta, premissa e efeito da resposta para avancar |
| `sem_opcao` | Justificativa para nao propor, apenas com negacao ou fora de escopo |

`sem_opcao` nao pode ser usado como atalho para abandonar um pedido
indeterminado. Formula e diligencia exigem pergunta e impacto da resposta.
Pedidos fora de escopo nao recebem uma proposta financeira.

O objeto `lacuna` tem dimensao (`nenhuma`, `nexo`, `valor`, `proporcao`, `escopo`
ou `cumprimento`), pergunta e impacto. Uma conclusao `necessita_informacao`
exige dimensao diferente de `nenhuma`. A validacao confere estrutura, tamanho
e preenchimento; a qualidade e especificidade da pergunta dependem das lentes
e precisam de avaliacao humana no teste.

## Como os numeros sao controlados

Para faixa ou formula, a base deve conter:

- valor positivo em centavos;
- natureza: orcamento, pagamento, pedido, contrato ou outro;
- fonte PR, RR, DR ou DD;
- trecho literal do resumo contendo o valor em formato brasileiro com duas
  casas decimais. Exemplo: `R$ 1.234,56` corresponde a `123456` centavos.

O contrato confere se o trecho existe no bloco apontado e se o valor consta
nesse trecho. O validador tambem verifica a citacao do lider contra o caso
que ele proprio leu. Nao ha acesso aos documentos originais nem ao gabarito.

Encontrar um valor no resumo NAO comprova responsabilidade nem pertinencia:
uma alegacao pode conter uma quantia. Natureza, contexto, escopo, dupla
contagem e premissas sao examinados pela auditora, nao provados pelo parser.

A primeira v10.2 deliberadamente restringe as faixas numericas a:

- `valor_documentado`: a base integral como opcao expressamente condicional;
- `proporcao_documentada`: limites percentuais presentes em um trecho literal.

As proporcoes usam inteiros em pontos-base: 10000 = 100%; 1250 = 12,5%.
O calculo e `arredondar(base_centavos * bps / 10000)`, com meio centavo
arredondado para cima. O modelo nao fornece uma faixa calculada separada.
Limites devem ser ordenados, de 0 a 10000, com limite superior positivo.

Se faltar uma proporcao sustentada, use `proporcao_a_negociar`, com todos os
campos numericos do criterio `null`. O termo mostra `base x p / 100`, identifica
`p` como nao definido e nao apresenta uma faixa numerica. Nao ha rateio padrao,
desconto fixo, uso de 40%-60% por conveniencia ou copia do gabarito.

Os prompts vedam inserir cifras/percentuais inventados nos campos de texto.
Essa vedacao depende tambem da auditoria por LLM: o codigo nao prova o
conteudo de toda frase livre. Por isso esta e uma versao experimental.

## Aplicacao esperada ao caso 0005

Uma saida admissivel, NAO um resultado real ja obtido com a v10.2, seria:

> Base de discussao: orcamento de reparacao de R$ 64.734,88, identificado como
> orcamento e nao como divida. Formula condicional: R$ 64.734,88 x p / 100.
> A base e a participacao dependem de concordancia. A pergunta deve tratar
> da parcela de responsabilidade/reparo que as partes admitem e explicar
> como essa resposta define ou impede a quantificacao.

Os resumos nao trazem o percentual do gabarito. A versao nao promete produzir
R$ 32.367,44 nem uma faixa de 40%-60% nesse caso. A melhoria a testar e sair
da abstencao generica para um caminho concreto de composicao, sem inventar
limites. Uma formula so e util se vier com premissas e perguntas pertinentes.

## Auditoria e documento

`auditoria.resultado` pode ser `apta` ou `reformular`. `reformular` exige risco,
motivo e lacuna com pergunta/impacto. Os riscos incluem ausencia de suporte,
valor inventado, dupla contagem, escopo, polos, premissa ou outro.

Uma opcao retida fica registrada no painel para revisao, mas o termo nao
publica sua faixa como proposta validada: mostra o bloqueio, motivo e perguntas.
Nao ha chamada adicional para reescrever uma opcao rejeitada nesta revisao.
`apta` significa que a lente auditora aprovou a apresentacao condicional;
nao significa aceite das partes, verdade comprovada ou acordo concluido.

O termo comeca com resumo por pedido, seguido de opcoes, base, premissas,
ressalvas, suporte/controversia e perguntas com seus efeitos. As conclusoes
das tres lentes ficam em secao separada. Fontes favoraveis e contrarias sao
exibidas separadamente. O rotulo ambiguo `sem maioria` e substituido por uma
leitura explicita das posicoes das lentes.

Nao ha soma automatica de opcoes: elas podem se sobrepor ou ser alternativas.
`consolidado.total_negociacao_centavos` permanece `null`. Os totais legados de
valores considerados devidos continuam separados, sem tratar abstencao como zero.

## Consenso, chamadas e custo

Um unico `run_nondet_unsafe`, sem EP de redacao, confirmacao humana on-chain
ou transacao extra. O termo e montado deterministicamente depois do EP.

O lider faz normalmente quatro chamadas: catalogo e tres lentes. Um validador
reconstroi o painel e executa:

1. Validacao estrutural e recomputacao do consolidado.
2. Checagem de citacoes do lider nos resumos locais.
3. Comparacao decisoria da v10.1, incluindo distincao de `null`/zero/positivo
   e tolerancia de 15% para valores devidos positivos.
4. Comparacao da estrutura da opcao, polos, estado da auditoria, riscos,
   fontes, natureza e valor-base, criterio e percentuais, dimensoes das lacunas.
   As bases e proporcoes das opcoes sao comparadas EXATAMENTE, nao com 15%.
5. Se os paineis validos nao forem identicos, uma chamada de comparacao
   semantica das conclusoes, propostas, premissas, ressalvas e perguntas.
   Mesmos numeros com condicoes diferentes nao devem ser aceitos.

Ha ate duas tentativas por etapa, inclusive para formato da resposta semantica.
Uma divergencia semantica valida (`false`) nao gera retry. Erro ou resposta
invalida apos o limite resulta em voto contrario. Respostas booleanas como
texto (`"true"`) nao sao aceitas. A comparacao semantica usa apenas catalogo e
teses, sem repetir o consolidado derivado.

Normal: 4 chamadas por lider e 4-5 por validador; no pior caso de retries,
ate 8 e 10, respectivamente, por execucao. Novas rotacoes podem repetir trabalho.
Os textos maiores, a dependencia sequencial e a comparacao semantica podem
aumentar custo/latencia, mesmo sem nova transacao. Nao ha estimativa monetaria
validada ainda. O teto do provedor pode truncar respostas de casos com muitos
pedidos; isso causa erro de JSON, nao reparacao silenciosa.

Igualdade estrutural nao garante equivalencia semantica e a avaliacao por LLM
tambem e falivel. Catalogos ou modalidades de opcao diferentes podem causar
`UNDETERMINED`. Esta revisao nao reduz exigencias apenas para obter `Agree`.
Os paineis e motivos internos dos validadores continuam nao gravados pelo
protocolo; nao inferir causas individuais de um `Disagree` isolado.

## Validacao e comparacao experimental

Executado localmente:

```sh
python3 -B -m unittest -v test_ic_v10_1.py test_ic_v10_2.py
```

78 testes aprovados: 42 da baseline e 36 da v10.2. Cobrem schema, limites,
citacoes literais/valores, percentuais, formulas, auditoria, polos contrapostos,
perguntas, fontes, nao somar opcoes, valores indeterminados, integridade do
consolidado, equivalencia estrutural/semantica simulada e fluxo de escrita/leitura
com um unico EP simulado. Um teste usa os resumos reais do caso 0005 para
verificar a base e rejeitar uma citacao inventada de 50%, sem usar o gabarito
para gerar respostas.

Nao foram executados SDK/GenVM real, chamadas reais a modelos nem rodada
comparativa no Studio. Testes simulados NAO demonstram melhora de merito,
robustez contra prompt injection ou consenso real. Nao promover a versao com
base apenas neles.

Primeira rodada recomendada, guardando a v10.1.4 para comparacao:

| Casos | O que observar |
|---|---|
| 0005 | Responsabilidade compartilhada; utilidade da formula/perguntas sem rateio inventado |
| 0033 | Preservacao de resultado positivo conhecido, sem transformar toda concessao em abstencao |
| 0134, 0041, 0063 | Nao substituir negacao correta por proposta financeira sem fundamento |
| 0001 | Multiplos pedidos e polos; sobreposicao/dupla contagem e custo do painel |

Repita com familias diferentes de modelos quando a configuracao permitir.
O sucesso da v10.1.4 no caso 0005 teve os votos Agree identificados como GPT-5.4;
nao demonstra, sozinho, consenso entre familias diferentes.

Registre por execucao: versao, caso, hash, resultado/status, modelos, rotacoes,
tempo, custo, retorno completo de `get_case()` e `get_termo_opcao()`. Avalie
separadamente:

- conclusao adequada, negacao indevida ou concessao indevida;
- indeterminacao justificada ou evitavel;
- opcao util, opcao sem fundamento ou retida pela auditoria;
- pertinencia da base, criterio e premissas (nao apenas se o numero existe);
- especificidade das perguntas e efeito real das respostas;
- preservacao de acertos, consenso, custo e latencia em relacao a baseline.

Nao conte `SUCCESS` como acerto de merito, nem formula sem percentual como
acerto financeiro contra o gabarito. A promocao depende da avaliacao comparativa,
especialmente de utilidade sem crescimento de propostas indevidas.
