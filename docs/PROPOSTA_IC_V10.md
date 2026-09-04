# Proposta técnica — Mediare IC v10

Status: proposta para implementação e experimento. Este documento não altera o
comportamento do contrato atual.

## Decisão executiva

A v10 deve trocar o objetivo de “produzir um acordo quando o painel parece
unânime” por “produzir um Termo de Opção auditável, pronto para o mediador”.
Esse termo mostra o que passou, o que não passou, onde as lentes divergiram e
quais faixas de valor podem ser discutidas com as partes. Ele é produzido na
mesma execução on-chain, sem uma confirmação ou segunda transação.

A prioridade não é treinar os pesos de um modelo. É melhorar o programa que
envolve o modelo:

1. entrada estruturada e versionada;
2. decisão e quantificação feitas juntas, pedido por pedido;
3. validação determinística rigorosa antes da consolidação;
4. princípio de equivalência programático, com zero versus positivo como
   divergência absoluta;
5. Termo de Opção único, voltado à condução da mediação;
6. seleção experimental de modelos e prompts contra um benchmark congelado.

Essa direção responde ao principal risco medido na v9: em 26 dos 48 casos cujo
gabarito patrimonial era zero, o painel propôs algum valor. Em nove deles o
painel foi unânime, com faixa que nem tocava zero. A unanimidade também não
predisse acerto: 57,6% nos painéis unânimes contra 66,1% nos divergentes.

## Objetivos mensuráveis

A v10 só deve substituir a v9 se, em avaliação pareada e previamente definida:

- reduzir a concessão patrimonial indevida nos casos zero de 54,2% para no
  máximo 25%;
- eliminar o caminho que transforma unanimidade em Termo de Acordo e gerar,
  em seu lugar, um Termo de Opção em todos os casos;
- obter pelo menos 65% de contenção nos casos positivos;
- obter pelo menos 70% de contenção geral;
- produzir faixa útil, com largura relativa de até 30%, em pelo menos 75% dos
  casos avaliáveis;
- produzir saída válida e painel completo em pelo menos 99% das execuções;
- não aceitar como equivalentes respostas que divirjam entre zero e positivo,
  pagador ou beneficiário;
- preservar rastreabilidade entre cada conclusão, o pedido e os trechos
  resumidos citados.

As metas são gates lexicográficos. Segurança nos casos zero vem primeiro;
cobertura e largura não podem compensar falsos positivos graves numa média
única.

## O que muda em relação à v9

| Área | v9 | v10 proposta |
|---|---|---|
| Unidade de decisão | quatro rubricas agregadas | cada pedido identificado |
| Mérito e valor | juntos, mas agregados | juntos, pedido por pedido |
| Valores | `float` tolerante | centavos inteiros e validação estrita |
| Evidência | fundamentos em texto livre | IDs dos trechos resumidos do caso |
| Painel incompleto | aceita uma ou duas lentes | não consolida sem três lentes válidas |
| Lentes | estrita, ampla, jurisprudencial | probatória, jurisprudencial e auditora/refutadora |
| Consolidação | mínimo/máximo dos totais | cenários completos + divergência por pedido |
| Equivalência | LLM compara faixas sobrepostas | validador customizado compara campos decisórios |
| Zero versus positivo | exceção no prompt | trava determinística obrigatória |
| Dano moral | ignorado no EP | decidido ou marcado fora de escopo explicitamente |
| Unanimidade | pode gerar termo | apenas informação diagnóstica |
| Saída do caso | termo de acordo ou pauta | sempre um Termo de Opção completo |

## Arquitetura proposta

```text
Caso resumido, anonimizado e imutável
                  |
                  v
      3 análises independentes
  probatória | jurisprudencial | auditora
        (mérito + valor juntos)
                  |
                  v
       validação determinística
                  |
                  v
   consolidação por pedido e cenário
                  |
                  v
  princípio de equivalência customizado
                  |
                  v
       Termo de Opção pronto
  (status, comentários e faixas)
```

### 1. Entrada estruturada

O IC atual recebe quatro blocos longos de texto e pede ao modelo que descubra,
ao mesmo tempo, partes, pedidos, evidências e valores. A v10 deve receber um
caso no schema `mediare.case.v2`:

```json
{
  "schema_version": "mediare.case.v2",
  "case_id": "0134",
  "partes": [
    {"id": "A", "papel": "requerente"},
    {"id": "B", "papel": "requerido"}
  ],
  "pedidos": [
    {
      "id": "P01",
      "autor": "A",
      "contra": "B",
      "modalidade": "pagar",
      "natureza": "danos_materiais",
      "valor_pedido_centavos": 8998848,
      "descricao": "ressarcimento dos reparos dos elevadores"
    }
  ],
  "fontes_resumidas": [
    {
      "id": "REQ_DOC_01",
      "bloco": "documentos_requerente",
      "conteudo": "Laudo técnico aponta ausência de peças..."
    },
    {
      "id": "RDO_DOC_01",
      "bloco": "documentos_requerido",
      "conteudo": "Relatório registra alagamento em 25/09/2023..."
    }
  ]
}
```

Esses IDs não apontam para documentos originais. Eles identificam apenas os
blocos, itens ou trechos já resumidos e anonimizados dentro de cada arquivo de
caso. Por exemplo, `REQ_DOC_01` pode significar “primeiro item de
documentos_requerente”. O objetivo é permitir que o Termo de Opção diga de qual
trecho do próprio input saiu uma conclusão.

Os IDs de pedido e fonte resumida devem ser gravados no dataset antes da
execução. Para os 500 casos legados, a migração é um trabalho único: separar os
pedidos e numerar os trechos existentes, revisar a amostra real e salvar o
resultado. O painel não deve inventar IDs diferentes a cada execução, e não é
necessário recuperar os documentos originais.

O contrato deve rejeitar antes da chamada ao LLM:

- `case_id` fora do formato permitido;
- schema desconhecido;
- IDs duplicados ou referências inexistentes;
- valor negativo ou fora de limite configurado;
- trecho resumido ou caso acima do limite de tamanho;
- conteúdo cujo hash não corresponda ao manifest versionado.

Os textos resumidos continuam sendo dados não confiáveis. O prompt deve
declarar que qualquer instrução encontrada dentro deles é conteúdo do litígio
e não pode modificar as regras, o schema nem o papel do modelo.

### 2. Resposta de cada lente

Cada lente deve julgar e quantificar todos os pedidos na mesma chamada. O
experimento de dois estágios já mostrou que perguntar primeiro se “há
obrigação”, sem exigir um número, aumenta concessões indevidas. A v10 preserva
a disciplina de colocar mérito e valor lado a lado.

Exemplo reduzido:

```json
{
  "schema_version": "mediare.thesis.v10",
  "lente": "probatoria",
  "pedidos": [
    {
      "pedido_id": "P01",
      "decisao": "negar",
      "pagador": null,
      "beneficiario": null,
      "valor_centavos": 0,
      "dano_comprovado": true,
      "nexo_comprovado": false,
      "condicao_previa_satisfeita": true,
      "fontes_favoraveis": ["REQ_DOC_01"],
      "fontes_contrarias": ["RDO_DOC_01"],
      "motivos": ["NEXO_NAO_COMPROVADO"],
      "informacao_faltante": "laudo que relacione o dano à conduta da requerida"
    }
  ]
}
```

Regras estruturais:

- `decisao` pertence a `conceder`, `negar`, `necessita_informacao` ou
  `fora_de_escopo`;
- `conceder` exige pagador, beneficiário, valor positivo e ao menos uma fonte
  resumida do caso;
- `negar` exige valor zero e pagador/beneficiário nulos;
- `necessita_informacao` não pode carregar condenação provisória;
- todos os pedidos de entrada aparecem exatamente uma vez, sem pedidos novos;
- valores monetários são inteiros em centavos;
- enums desconhecidos, números reparados silenciosamente e campos ausentes
  invalidam a tese; não são convertidos em zero;
- obrigações de fazer e não fazer são pedidos próprios. Não são convertidas em
  dinheiro pelo modelo;
- dano moral é decidido explicitamente ou marcado `fora_de_escopo`; nunca é
  simplesmente removido da equivalência.

Quando o runtime/modelo suportar schema estruturado nativamente, o harness deve
usar JSON Schema estrito. O OpenRouter documenta `response_format` com
`json_schema` e recomenda `strict: true` e `require_parameters: true`, embora o
suporte efetivo deva ser verificado por endpoint.

### 3. Lentes redesenhadas

As lentes devem buscar erros diferentes, não representar partes diferentes:

1. **Probatória:** verifica existência do dano, nexo, legitimidade, condição
   prévia, liquidez e limite documental de cada rubrica.
2. **Jurisprudencial:** aplica presunções e padrões decisórios pertinentes, mas
   precisa nomear a presunção e a fonte resumida que permite aplicá-la.
3. **Auditora/refutadora:** começa pela hipótese de que o valor é indevido e
   procura pedido copiado sem prova, preço confundido com condenação, obrigação
   de fazer monetizada, multa condicional, honorários/custos incluídos, dupla
   contagem, polo invertido e nexo ausente.

A lente ampla da v9 não deve ser portada como está. Ela teve o pior desempenho
individual e sua instrução de conceder o valor pedido na dúvida conflita com a
meta prioritária de reduzir falsos positivos.

### 4. Validação local da tese

Antes de uma tese entrar no painel, uma função determinística deve validar:

```text
schema e versão corretos
    -> cobertura exata dos pedidos
    -> enums e referências válidos
    -> coerência decisão/valor/partes
    -> fonte resumida obrigatória para valor positivo
    -> aritmética em centavos
    -> limites de tamanho e quantidade
```

O painel deve ter três teses válidas. Se uma lente falhar após o número limitado
de tentativas, a saída é `painel_incompleto`, sem mérito consolidado. O Termo
de Opção deve registrar claramente a falha, sem apresentar uma faixa como se o
painel estivesse completo. Converter erro de parsing em decisão zero seria tão
incorreto quanto aceitar um painel parcial.

### 5. Consolidação determinística

A consolidação ocorre por pedido e preserva os três cenários completos.

Para cada pedido:

- zero versus positivo é sempre divergência material;
- pagador ou beneficiário diferentes são divergência material;
- `necessita_informacao` nunca é promovido automaticamente a `conceder`;
- uma concessão só é classificada como `suportada` se pelo menos duas lentes
  concederem, coincidirem em pagador/beneficiário e citarem fonte válida;
- qualquer divergência de mérito produz uma pergunta objetiva para o mediador;
- o intervalo monetário usa os valores completos das lentes, sem montar um
  cenário artificial pela combinação de mínimos independentes.

O consolidado deve expor:

- decisão e faixa por pedido;
- totais completos por lente;
- faixa dos totais completos;
- motivos de divergência com códigos fechados;
- trechos resumidos citados por cada lente;
- flags de segurança;
- número de teses válidas e versão do schema/prompt.

`unanime` pode continuar existindo como telemetria, mas não muda o estado do
produto e não autoriza nenhuma ação.

### 6. Princípio de equivalência

O `prompt_comparative` atual aceita dois painéis quando suas faixas apenas se
sobrepõem. Isso permite que respostas substancialmente diferentes encontrem um
ponto comum e sejam tratadas como equivalentes.

A documentação atual da GenLayer recomenda um validador customizado para a
maioria dos contratos e exige verificação independente da substância. A v10
deve usar `run_nondet_unsafe`: o validador reexecuta o painel, normaliza os dois
resultados e compara programaticamente os campos decisórios.

Ordem de comparação:

1. ambos os painéis têm três teses válidas;
2. `case_hash`, versão do schema e conjunto de pedidos coincidem exatamente;
3. para cada pedido, a classe zero/positivo coincide exatamente;
4. pagador, beneficiário e modalidade coincidem exatamente;
5. flags de condição prévia, dano e nexo coincidem;
6. valores positivos ficam dentro da tolerância configurada por pedido;
7. estado consolidado e códigos de divergência coincidem;
8. textos explicativos e ordem das fontes são ignorados.

Para valores positivos, o experimento inicial pode manter ±15% por pedido. A
tolerância não se aplica a zero versus positivo e não deve ser baseada apenas
na sobreposição de faixas. Depois da primeira rodada, a tolerância deve ser
calibrada por categoria e valor absoluto; valores pequenos precisam também de
um limite absoluto para evitar distorção percentual.

### 7. Saída única: Termo de Opção

`analyze_case` deve produzir diretamente um Termo de Opção na mesma execução
que analisa o painel. Não existe uma segunda confirmação on-chain e não há uma
operação separada para gerar minuta.

Preferencialmente, o Termo de Opção deve ser renderizado por uma função Python
determinística a partir do painel consolidado, usando seções e frases-modelo.
Os comentários curtos já vêm das teses aceitas. Isso remove a chamada adicional
de LLM que hoje redige “termo ou pauta”, reduz custo e elimina mais uma fonte de
divergência entre validadores.

O Termo de Opção deve conter:

1. identificação e resumo do conflito;
2. quadro de todos os pedidos, com status `passou`, `nao_passou`,
   `controvertido`, `necessita_informacao` ou `fora_de_escopo`;
3. comentário curto explicando por que cada pedido recebeu aquele status;
4. fontes resumidas favoráveis e contrárias, pelos IDs internos do caso;
5. faixa de valor por pedido e faixa total dos cenários completos;
6. posição de cada lente quando houver divergência;
7. pontos e perguntas que o mediador pode discutir com as duas partes;
8. flags de segurança, inclusive painel incompleto ou divergência sobre quem
   paga.

`passou` não significa condenação nem acordo celebrado. Significa apenas que o
pedido ultrapassou os critérios do comitê e pode entrar como opção na
negociação. O documento fica pronto para uso pelo mediador, mas só as partes
podem aceitar uma opção e formalizar o acordo fora desse fluxo do IC.

Estados mínimos sugeridos:

```text
vazio -> analisando -> termo_opcao_disponivel
                    -> termo_opcao_com_painel_incompleto
                    -> indeterminado
```

## Mudanças propostas por arquivo

### `ic.py`

- adicionar schemas e validação estrita;
- substituir `float` por centavos inteiros;
- rejeitar entradas e teses inválidas sem coerção silenciosa;
- substituir a lente ampla pela auditora;
- consolidar por pedido e por cenário;
- substituir `prompt_comparative` por validador customizado;
- remover a bifurcação `unanime -> termo de acordo` / `divergente -> pauta`;
- fazer `analyze_case` gerar sempre um Termo de Opção;
- incluir status, comentários, fontes e faixas por pedido no mesmo resultado;
- renderizar o documento por template determinístico, sem a atual chamada
  adicional a `prompt_non_comparative`;
- não adicionar outra operação ou transação de confirmação.

### `harness.py`

- abstrair o cliente de modelo e adicionar OpenRouter;
- enviar JSON Schema estrito quando suportado;
- registrar modelo solicitado, modelo servido, provedor, parâmetros, prompt
  hash, dataset hash, tokens, custo, latência, retries e erro;
- fixar modelo e provedor em cada experimento e desabilitar fallback;
- implementar métricas por pedido, direção do erro e categoria;
- calcular intervalos de Wilson e comparação pareada com a v9;
- permitir repetições com seeds/parâmetros registrados;
- falhar cedo quando cinco chamadas consecutivas indicarem erro de configuração.

### Dataset

- criar `casos_v2/` com catálogo estruturado de pedidos e trechos resumidos;
- criar manifest versionado com hash de cada entrada;
- manter os gabaritos fora do contexto do modelo;
- mover o teste oculto para armazenamento privado durante os experimentos;
- registrar grupos de processos e templates para impedir vazamento entre folds.

### Testes

- unitários para validação, centavos, enums, referências, consolidação e EP;
- regressões explícitas para os nove falsos consensos da v9;
- adversariais para prompt injection, documento contraditório, dupla contagem,
  polo invertido, multa condicional e obrigação não monetária;
- golden tests do Termo de Opção sem exigir igualdade de redação;
- testes on-chain somente depois que o candidato passar os gates off-chain.

## Plano experimental

### Fase 0 — congelar avaliação

- preservar os 128 casos da baseline para comparação pareada;
- separar por processo/template, nunca aleatoriamente por arquivo;
- usar 96 casos em desenvolvimento com validação cruzada estratificada;
- manter 32 casos ocultos, aproximadamente 12 zero e 20 positivos;
- não alterar o candidato depois de revelar o resultado oculto.

Como 32 casos produzem intervalos largos, a decisão deve combinar: melhora
pareada fora de fold nos 96 casos, confirmação de direção no teste oculto e
inspeção individual de qualquer erro patrimonial grave.

### Fase 1 — infraestrutura e baseline

- implementar telemetria do harness e cliente OpenRouter;
- reproduzir uma amostra da v9 para confirmar equivalência do caminho;
- validar privacidade, schema e fixação de provedor antes de rodadas grandes.

### Fase 2 — ablação de arquitetura

Testar uma mudança por vez:

1. schema por pedido sem mudar as lentes;
2. centavos e validação estrita;
3. lente auditora no lugar da ampla;
4. evidence gate;
5. consolidação por pedido;
6. EP programático.

Cada variante deve ser comparada no mesmo subconjunto e nas mesmas condições.
Variantes que piorarem o gate de casos zero são eliminadas, mesmo que elevem a
contenção geral.

### Fase 3 — busca de prompts e modelos

- gerar 20–40 candidatos de instrução em modelos baratos;
- promover no máximo cinco configurações;
- testar modelos de pelo menos três famílias/provedores;
- testar painel homogêneo e heterogêneo;
- manter temperatura, limite de tokens e roteamento registrados;
- repetir finalistas três vezes sem cache de resposta.

O modelo vencedor é o que satisfaz os gates do Mediare, não o líder de um
benchmark genérico. A lista e os preços devem ser consultados novamente no dia
do experimento, pois modelos, endpoints e custos mudam.

### Fase 4 — teste oculto e GenLayer

- congelar commit, prompts, schemas, modelos, provedores e EP;
- executar o teste oculto uma única vez;
- investigar todos os falsos positivos, sem retunar o candidato;
- rodar Direct Mode e depois 20–30 casos críticos no Studio;
- comparar estabilidade líder/validadores e taxa de `UNDETERMINED`;
- só então decidir se a v10 está pronta para substituir a v9.

## Orçamento dos US$ 500 do OpenRouter

| Uso | Limite |
|---|---:|
| Smoke tests, schema e baseline | US$ 40 |
| Busca de arquitetura e prompts | US$ 120 |
| Matriz de modelos finalistas | US$ 120 |
| Três repetições e casos adversariais | US$ 90 |
| Confirmação do candidato congelado | US$ 50 |
| Reserva para falhas e segunda iteração | US$ 80 |
| **Total** | **US$ 500** |

Devem existir chaves ou guardrails separados por fase, com limite financeiro.
Para casos reais, o roteamento deve exigir `data_collection: "deny"` e
`zdr: true`; fallbacks ficam desligados, e o endpoint precisa suportar todos os
parâmetros requeridos. A documentação do OpenRouter permite essas restrições,
mas a política jurídica/LGPD do projeto ainda deve ser aprovada antes do envio
de casos reais a qualquer provedor.

## Critérios de parada

Interromper uma variante imediatamente quando:

- aumentar a concessão indevida nos casos zero;
- aceitar zero e positivo como equivalentes;
- produzir pedido, pagador ou beneficiário inexistente;
- depender de reparação silenciosa de JSON ou número;
- gerar faixa mais larga sem ganho correspondente de cobertura;
- apresentar custo ou latência incompatível com a operação;
- falhar de forma sistemática em uma categoria ou grupo de template.

Não fazer fine-tuning de pesos nesta fase. Reavaliá-lo apenas com schema
estável, pelo menos 1.000–1.500 casos reais independentes revisados por
especialistas, teste oculto externo e disponibilidade operacional do modelo
customizado para os validadores.

## Sequência recomendada de implementação

1. PR 1: `case.v2`, validação e testes determinísticos, sem LLM.
2. PR 2: `thesis.v10`, prompts por pedido e lente auditora.
3. PR 3: consolidação por pedido, cenários e métricas no harness.
4. PR 4: cliente OpenRouter, telemetria e runner experimental.
5. PR 5: princípio de equivalência customizado e testes de segurança.
6. PR 6: saída única do Termo de Opção e estados mínimos do produto.

Os PRs 1–4 podem ser validados inteiramente off-chain. O PR 5 exige Direct
Mode e um lote crítico no Studio. O PR 6 não adiciona uma segunda transação.

## Decisões que precisam ser tomadas antes da implementação

1. Dano moral faz parte do valor orientativo ou fica explicitamente fora de
   escopo?
2. Qual é o limite máximo de valor e tamanho de texto aceito pelo produto?
3. Os 32 casos de teste podem ser movidos para um repositório privado antes do
   início dos experimentos?
4. Quem fará a revisão humana dos catálogos de pedidos e dos gabaritos reais?

## Fontes técnicas

- [Baseline v9](../RESULTADOS.md)
- [Intelligent Contract atual](../ic.py)
- [Harness atual](../harness.py)
- [GenLayer — The Equivalence Principle](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle)
- [OpenRouter — Structured Outputs](https://openrouter.ai/docs/guides/features/structured-outputs)
- [OpenRouter — Provider Routing](https://openrouter.ai/docs/guides/routing/provider-selection)
- [OpenRouter — Guardrails](https://openrouter.ai/docs/guides/features/guardrails/overview)
