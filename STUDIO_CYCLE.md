# Ciclo supervisionado de testes e marcos major

`studio_runner.py` ja acessa o Studio pelo SDK, mas e um runner de lotes da v9:
nao instala revisoes nem faz upgrade. `studio_cycle.py` executa uma rodada por
versao; o Codex inspeciona o resultado, altera o codigo com justificativa e testes,
incrementa `VERSAO`, faz commit/push e executa a proxima rodada. Nao ha geracao
cega de codigo ou relaxamento automatico do consenso para obter um verde.

## Instancia e conta

O endereco usado no ultimo teste manual da v10.2,
`0xfDdf21D4BC1A85614BE2a1AA01C160489be6c1FB`, nao expoe `upgrade`.
Nao e possivel acrescentar esse metodo retroativamente nessa instancia.
O ciclo usa um novo `studio_bootstrap.py`, atualizavel somente pelo deployer.
Preserva os cinco campos de storage, na mesma ordem e com os mesmos tipos.
Nao ha migracao de storage; o construtor nao roda novamente em upgrades.
O dono da instancia pode substituir todo o codigo: recurso de testes, nao
uma governanca de producao. A chave deve continuar disponivel localmente.

A v10.2.1 tambem permite deploy direto atualizavel. Getters `get_version`,
`get_code_hash` e `can_upgrade` permitem conferir identidade e autorizacao.
Apos um upgrade o estado anterior permanece ate uma nova analise bem-sucedida:
`get_case.versao` identifica o codigo atual, enquanto `painel.versao` identifica
a analise armazenada. O runner exige que ambos coincidam com a rodada.

SDK validado: `genlayer-py==0.18.0`, Python da `.venv`. Endpoint unico permitido:
`https://studio.genlayer.com/api`, chain ID 61999. O runner nao usa faucet,
nao transfere fundos, nao cria chaves e nao expoe segredos nos logs.
A conta local existente pode ser diferente da conta aberta na interface web.

## Uso

Executar da raiz do repositorio. O argumento da chave e sempre um caminho,
nunca a chave privada na linha de comando. Nao commitar `res_*`.

```sh
.venv/bin/python studio_cycle.py inspect --key-file res_v9/conta.key
.venv/bin/python studio_cycle.py init --key-file res_v9/conta.key --out res_cycle_v10_2 --max-versions 499 --max-calls 1000 --case-id 5 --execute
.venv/bin/python studio_cycle.py run --key-file res_v9/conta.key --out res_cycle_v10_2 --source ic_v10_2.py --execute
.venv/bin/python studio_cycle.py resume --key-file res_v9/conta.key --out res_cycle_v10_2 --execute
```

Desde a politica de marcos major, use `--source ic_experimental.py` para a
candidata atual. `ic_v10_2.py` preserva a v10.2.4. O historico para relatorio
esta em [CHANGELOG.md](CHANGELOG.md); tags `ic-vM.x.y` preservam marcos no Git.
Para restaurar somente o codigo de um snapshot ja registrado:

```sh
.venv/bin/python studio_cycle.py rollback --key-file res_v9/conta.key --out res_cycle_v10_2 --version 10.2.4-experimental --reason 'Descrever a regressao observada' --execute
```

Nao executamos esse exemplo automaticamente. Rollback tambem respeita limite,
prazo, pausa e autenticacao. Nao desfaz transacoes nem restaura estado/Termo antigo.
`resume` tambem retoma um rollback interrompido, sem novo envio.

`init --contract ENDERECO` reutiliza somente uma instancia atualizavel e
autorizada para a conta local. `inspect` e somente leitura.

Cada `run` faz: valida AST/layout/metodos -> compila no Studio -> salva snapshot
imutavel e SHA-256 -> envia upgrade -> aguarda FINALIZED/SUCCESS -> confere
versao e hash on-chain -> envia analyze_case -> aguarda -> salva recibo,
estado e Termo. O upload e a instalacao do codigo acontecem no upgrade;
nao e criado um arquivo/aba no editor do navegador. O endereco fica em
`res_cycle_v10_2/cycle.json` para consultar a instancia no Studio.

O operador pode preparar a proxima revisao durante a espera, mas nunca enviar
uma nova transacao enquanto a anterior estiver pendente/incerta. Nao repetir
`init` em outra pasta para contornar uma falha. O lock protege processos que
usam a mesma pasta; nao coordena outras contas/clientes ou pastas independentes.

## Limites e retomada

- Autorizacao desta campanha: ate 1.000 envios (deploy + upgrades + analises),
  no maximo 499 revisoes e 6 horas a partir de `init`. Sao tetos, nao metas.
- O numero de chamadas internas de LLM depende de validadores, retries e
  rotacoes do protocolo; nao e igual ao numero de transacoes do runner.
- Espera minima de 15 segundos DEPOIS de observar o termino da execucao anterior.
  Polling de recibos a cada 15 segundos por padrao; sem chamadas concorrentes.
- Os limites sao persistidos e nao reiniciam em `run`/`resume`. Apos o prazo,
  consultas para esclarecer uma transacao pendente continuam permitidas,
  mas nao ha novos envios.
- Somente `FINALIZED` com recibo `execution_result=SUCCESS` e sucesso.
  `ACCEPTED`, ausencia de erro ou `MAJORITY_AGREE` sozinhos nao bastam.
- Timeout/RPC incerto interrompem envios. `resume` consulta a transacao ja
  registrada, inclusive recuperando o hash GenLayer de um recibo EVM conhecido.
  Sem hash recuperavel, exige inspecao manual: nunca reenviar por tentativa.
- Se o upgrade terminou mas um defeito de getter impede iniciar a analise,
  `skip --reason 'diagnostico' --execute` registra a revisao como nao analisada.
  Nao permite pular transacao pendente/incerta nem analise ja registrada.
- `UNDETERMINED` encerra a rodada sem sucesso; `FINALIZED/ERROR` tambem.
  Falhas de autorizacao, schema, identidade remota ou infraestrutura exigem
  diagnostico antes de continuar, nao repeticao indiscriminada.

Nao ha cobranca automatica nem estimativa monetaria inventada. O registro
inclui gas/estatisticas apenas quando o recibo os fornece. Os arquivos de
resultado contem dados do caso: permanecem locais e ignorados pelo Git.
Campos de credenciais eventualmente retornados em `node_config` sao
substituidos por `[REDACTED]` antes de salvar recibos.

## Avaliacao e criterio de parada

O runner verifica a execucao, a versao, o caso, a integridade do painel e a
consistencia dos getters. O resultado `SUCCESS_REVIEW_REQUIRED` nao certifica
correcao juridica nem qualidade do termo. A revisao deve conferir:

1. Cobertura dos pedidos, bases e citacoes apenas dos resumos, sem gabarito no IC.
2. Distincao entre valores devidos e opcoes condicionais; nada desconhecido vira zero.
3. Opcoes uteis: faixa fundamentada, formula com parametro explicitamente aberto,
   providencia nao monetaria ou pergunta concreta que destrave a mediacao.
4. Bloqueios da auditora pertinentes, sem inventar percentuais para obter consenso.
5. Rotacoes/falhas efetivamente registradas. Os paineis dos validadores nao sao
   gravados pelo protocolo: votos Disagree nao revelam a causa individual.

Parar quando houver termo operacionalmente valido e util revisado, quando o
limite terminar ou quando surgir impedimento que exija decisao do usuario.
Cada correcao deve ter revisao propria, testes de regressao e commit descritivo.
Um caso aprovado nao demonstra generalizacao: ampliar casos e uma etapa posterior.

```sh
.venv/bin/python -m unittest test_ic_v10_1 test_ic_v10_2 test_ic_experimental test_studio_cycle
```

## Registro da campanha de 06/09/2026

Instancia: `0x7AC6360E36BEA2791FA45AFA2B18b277bD3a247B`.
Conta SDK: `0x6d96d47e3370A838F4414F63Ba79D1c8b9812bCf` (conta local existente).

- Bootstrap: FINALIZED/SUCCESS, tx `0x8a72ea80f8f2afc21da4734e22a52159ceff48c794b2582af1675ab1b6614881`.
- v10.2.1: upgrade FINALIZED/SUCCESS, tx `0x298d7a601529e52c6615daf7d8b276fba809b4a5744f66079c468b9ef33774de`.
  Nao analisada: getter de hash iterava `VLA[u8]` por byte e excedeu 30s nas leituras.
- v10.2.2: substitui essa iteracao por `slot().read(data_offset(), len(code))`,
  preservando SHA-256 e layout. Nao altera prompts/merito em relacao a v10.2.1.
  Upgrade FINALIZED/SUCCESS, tx `0x146bcd7f86ab40f73e26203a25c7cc7415534f350c6b2b329ad8c2c6a1bb262e`.
  Nao analisada: SDK fixado nao possui `VLA.data_offset()` (AttributeError real).
- v10.2.3: usa offset 4 do `Root.code` indireto (prefixo u32 de tamanho),
  com leitura unica do codigo. Teste de storage sem `data_offset` e sanitizacao
  de credenciais dos recibos adicionados; 97 testes locais passaram.
  Upgrade e verificacao remota de hash funcionaram. Analise 0005, tx
  `0x05ead024baaffe8ab8f256dc2e0e0bfe7dfa7d99933e7d6f51ebbf05f7216b53`,
  terminou UNDETERMINED apos tres rotacoes, apesar de lideres com SUCCESS.
  Nenhum termo aprovado foi lido. Um lider falhou em JSON no catalogo.
  Os paineis dos **lideres** gravados mostram diferencas materiais: pedido
  declaratorio concreto versus responsabilidade abstrata, e formula condicional
  ora apta, ora rejeitada por nao fixar p. Isso nao revela motivos individuais
  de Disagree dos validadores.
- v10.2.4: delimita o objeto concreto do pedido declaratorio e o estatuto
  das alegacoes/documentos resumidos; reforca que a auditoria avalia a
  apresentacao condicional, nao exigibilidade imediata. Preserva comparador,
  limites numericos e rejeicao de base/aceitacao inventada. Parser reconhece
  apenas envelope `<think>...</think>` completo seguido de JSON (possivelmente
  cercado), sem extrair objetos de prosa nem completar respostas truncadas.
  Erros de sintaxe agora classificam o envelope sem expor texto do modelo.

A implementacao oficial de [VLA no GenVM](https://github.com/genlayerlabs/genvm/blob/main/runners/genlayer-py-std/src/genlayer/storage/core.py)
explica a diferenca entre iteracao por elemento e leitura em bloco. Os testes
de mocks nao medem latencia de storage; o teste real revelou esse defeito.
