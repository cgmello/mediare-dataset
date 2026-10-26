# Especificação do Sistema Mediare

Versão 1.0 • 29 de setembro de 2026 • Proposta para validação de produto e engenharia

## 1 Objetivo e orientação técnica

A Mediare será uma plataforma de mediação extrajudicial online que integra identificação das partes, recebimento de provas, pagamento, análise por comitê de IAs da GenLayer, revisão humana, agendamento e assinatura do acordo. Este documento estabelece o comportamento esperado e a infraestrutura necessária para implementar o ciclo completo.

Recomenda-se um backend Python com Django e Django REST Framework, organizado como monólito modular, PostgreSQL como fonte de verdade, S3 privado para documentos e filas SQS consumidas por workers Python. O frontend preservará a identidade visual existente. OpenRouter atenderá às chamadas de IA feitas pelo backend; a execução do comitê on-chain continuará sob a infraestrutura da GenLayer, por um adaptador independente.

O projeto do website deve evoluir em repositório próprio, separado dos experimentos do IC e do dataset. O contrato entre os dois projetos será um esquema de entrada e saída versionado, com fixtures sintéticas e hashes dos artefatos. A implantação do website não deve promover automaticamente uma versão experimental do IC.

As regras identificadas como RF são requisitos funcionais. RN são regras de negócio; RT, requisitos técnicos; CA, critérios de aceite; D, decisões pendentes. Uma recomendação indicada como “proposta” não é uma decisão comercial já aprovada. Os parâmetros de capacidade, retenção e operação apresentados são valores iniciais para validação.

## 2 Escopo e análise do material existente

A primeira versão usa pagamentos simulados por PIX e cartão de crédito, conforme decisão de produto. Não há cobrança real, coleta de dados bancários ou de cartão, QR Code PIX pagável nem integração com PSP nesta entrega. O fluxo de pagamento permanece implementado para validar regras e jornadas. Pagamentos reais ficam para a segunda etapa.

O escopo completo abrange portal público, área das partes, área dos mediadores, administração, processamento documental, integrações de pagamento e comunicação, comitê GenLayer, sessão de mediação e assinatura. Não inclui execução judicial do acordo, custódia do valor em disputa ou repasse automático das obrigações negociadas entre as partes. Os honorários da plataforma e o pagamento previsto no acordo são operações diferentes.

O site https://mediarev1.netlify.app/ foi consultado em 29/09/2026, juntamente com o arquivo local index.html. Há uma landing page responsiva, navegação institucional, versões PT/EN/ES, explicação do procedimento, honorários e FAQ. Os botões operacionais mostram um aviso de demonstração. No arquivo examinado não há formulários operacionais nem chamadas fetch ao backend. O layout público pode ser reaproveitado; as telas autenticadas ainda precisam ser implementadas, salvo se existirem em outros arquivos.

O conteúdo do site serve como referência de produto. Havendo divergência, esta proposta segue o rascunho de requisitos mais recente e registra a diferença abaixo.

| Tema | Site atual | Base desta especificação |
| --- | --- | --- |
| Honorários | 2% com mínimo de R$500 | R$500 somados a 2% do valor em disputa |
| Cobrança | Após o aceite do convite | Após a entrega do requerido e o congelamento |
| Frontend | Apresentação e botões demonstrativos | Áreas autenticadas e integrações ainda necessárias |
| Identidade | Cita CPF/RG e comprovante de residência | CNH, identidade ou passaporte; endereço informado obrigatório |
| IA | Fala em julgar e em decisão final humana | Parecer de apoio; acordo depende das partes |
| Privacidade | Promete sigilo e anonimização | Publicação de JSON requer avaliação específica |
| Público atendido | Pessoas e empresas | Fluxo detalhado cobre pessoas físicas; PJ exige representação |
| Análise adicional | Site permite pedir informações e voltar ao comitê | Nova rodada controlada, sem alterar o snapshot anterior |

Também existem no repositório scripts para produzir Termos de Opção e Termo Final. São componentes candidatos a reaproveitamento após revisão e adaptação; não equivalem a um serviço web pronto.

## 3 Papéis e autorização

Uma pessoa pode ter mais de um papel, mas as permissões devem ser avaliadas por caso e por ação. KYC aprovado não concede papel administrativo ou de mediador. Convites, credenciais e vínculos com casos são entidades distintas.

| Papel | Acesso permitido | Restrições |
| --- | --- | --- |
| Visitante | Site, início do cadastro e convite válido | Sem documentos ou dados privados do caso |
| Usuário em cadastro | Próprio cadastro e KYC | Não abre nem instrui casos enquanto não habilitado |
| Requerente | Próprio pedido e casos vinculados | Edita sua manifestação apenas na fase permitida |
| Requerido | Convite vinculado, defesa e casos próprios | Aceite autenticado e KYC antes da entrega |
| Mediador | Casos atribuídos, originais e termos após liberação | Não acessa casos de outros mediadores |
| Administrador | Convites, operação, parâmetros e incidentes | Documentos pessoais exigem permissão específica e auditoria |
| Worker | Recursos exigidos por sua tarefa | Credencial de serviço sem privilégios de usuário |
| Público externo | JSON expressamente liberado | Sem documentos originais ou mapa de identidades |

RT-01. Toda API verifica sessão, segundo fator quando exigido, papel, vínculo ao recurso e estado do fluxo. Um UUID conhecido nunca substitui autorização. Testes devem impedir que uma parte leia o KYC da outra ou modifique objetos de outro caso.

Proposta de visibilidade: cada parte vê sua identidade completa, suas provas e os documentos do procedimento compartilhados. Provas da outra parte poderão ser compartilhadas após adesão, conforme política de contraditório a aprovar. Documentos de KYC não integram automaticamente esse conjunto. O mediador recebe acesso amplo aos originais do caso atribuído na revisão humana; toda abertura ou download é auditado.

## 4 Cadastro autenticação e recuperação

RF-01. O cadastro por e-mail exige e-mail, senha e confirmação de senha. A confirmação é validada e descartada. O sistema armazena hash adaptativo da senha, preferencialmente Argon2id, nunca senha legível ou reversivelmente cifrada. O e-mail deve ser verificado antes de habilitar a conta. Respostas de recuperação não revelam se uma conta existe.

RF-02. O cadastro e login Google usam OpenID Connect. Além do e-mail solicitado, é tecnicamente necessário persistir o identificador estável do provedor, composto por issuer e subject, para vinculação segura. Nenhuma senha Google é armazenada. Validar assinatura, emissor, audiência, validade, nonce e fluxo de autorização. Não unir automaticamente contas apenas porque compartilham um e-mail; vinculação exige autenticação da conta existente.

RF-03. Esqueci a senha envia um link de uso único e expiração curta. Após a troca, revogar sessões anteriores e notificar o titular. Conta exclusivamente Google deve ser orientada ao provedor; criar senha local é um fluxo separado, com reautenticação. Recuperação de acesso não altera identidade civil nem dispensa o segundo fator.

RF-04. Após KYC completo, todo novo login, inclusive via Google, deve passar pelo desafio adicional escolhido entre e-mail, SMS ou WhatsApp. Antes de concluí-lo, a sessão permite apenas verificar o código, sair e recuperar acesso. Renovar uma sessão válida não deve ser tratado como login novo; expiração, inatividade e duração máxima serão configuradas.

RT-02. Proposta inicial para códigos: seis dígitos, validade de cinco minutos, uso único, até cinco tentativas, intervalo mínimo de sessenta segundos para reenvio e limites por conta, destino e IP. Armazenar digest protegido por segredo do servidor, não o código em claro. Invalidar desafios anteriores ao reenviar. Logs nunca registram códigos, links de recuperação ou tokens.

RT-03. Sessões do navegador usam cookies Secure e HttpOnly, proteção CSRF e lista explícita de origens confiáveis. Segredos não ficam no localStorage. O segundo fator por e-mail é uma opção comercial solicitada, mas sua independência é limitada quando o login Google e a caixa de e-mail são a mesma conta. Recomenda-se TOTP ou passkey para administradores e mediadores, como reforço sujeito a aprovação.

## 5 Identificação e manutenção do perfil

RF-05. O KYC possui três etapas: documento, perfil e verificação do telefone. Aceitar CNH, carteira de identidade, incluindo RG/CIN conforme o documento apresentado, ou passaporte. Solicitar frente e verso quando aplicável. Guardar tipo, país/emissor, número extraído, nome completo, arquivo de origem, data, versão do extrator e resultado da conferência. Um número isolado não é chave global confiável.

RF-06. A IA pode extrair nome e número do documento, mas não aprova identidade por si só. Primeiro executar validações locais de arquivo, legibilidade e extração; em seguida usar a chamada autorizada via backend/OpenRouter para a etapa de IA prevista. Qualquer envio de documento pessoal a fornecedor externo exige configuração de privacidade e finalidade próprias, separadas da análise do mérito. Saídas incertas, inconsistentes ou não legíveis seguem para revisão humana e reenvio.

Extrair texto de um documento não comprova autenticidade nem que o portador é seu titular. Decidir o nível de garantia exigido: conferência documental manual, fornecedor especializado, prova de vida ou outra evidência. A foto opcional do perfil não deve ser tratada como biometria verificada. A ativação comercial depende dessa decisão; o sistema não deve apresentar “identidade verificada” quando apenas houve OCR.

RF-07. O perfil exige endereço no Brasil com CEP, logradouro, número ou indicação sem número, complemento quando houver, bairro, município e UF. Foto é opcional; telefone é obrigatório porque sua confirmação conclui o KYC. Validar estrutura do endereço sem confundir consulta de CEP com comprovação de residência. Comprovante de residência não é obrigatório no rascunho e depende de decisão adicional.

RF-08. A GREEN-API envia o código WhatsApp gerado e validado pela Mediare. O status entregue da mensagem não comprova posse: somente a digitação correta do código conclui a verificação. Na indisponibilidade, manter a etapa pendente e permitir reenvio controlado; substituição desse canal para o KYC depende de regra aprovada.

RF-09. Nome completo, e-mail e identificação são imutáveis pelo autosserviço após a confirmação. Foto, endereço e telefone podem ser alterados. A troca de telefone exige reautenticação, registra o novo número como pendente e só o ativa após verificação; o número pendente nunca pode receber códigos de login. Perda do número anterior usa recuperação por canal já confiável ou revisão de identidade.

RT-04. Deve existir processo administrativo auditado para erro de OCR, mudança legal de nome e exercício de direitos de correção, com nova verificação e histórico. Isso não libera edição irrestrita. Alterar o perfil não reescreve a qualificação preservada em um snapshot ou acordo assinado. Caso sejam necessários CPF, CNPJ ou poderes de representação para assinatura, coletá-los em fluxo próprio; não inventá-los a partir de outro documento.

Estados de KYC: não iniciado, documento recebido, em processamento, revisão necessária, perfil pendente, telefone pendente, aprovado, recusado e suspenso. Cada transição guarda motivo e responsável. KYC recusado deve admitir correção ou contestação por suporte.

## 6 Upload e preservação dos originais

RF-10. A tela permite selecionar arquivos, selecionar pasta quando suportado pelo navegador e arrastar arquivos. Expandir pastas em arquivos individuais. Cada arquivo ganha uma linha com nome, tamanho, progresso, estado, mensagem de erro e lixeira. “Enviar todos” inicia os itens pendentes; falha em um item não perde os demais. Oferecer seleção múltipla como alternativa em navegadores sem suporte a pastas.

RF-11. Proposta inicial de formatos: PDF, TXT, JPEG e PNG; 25 MB por arquivo, 100 arquivos e 500 MB por caso. Limites são configuráveis e devem ser validados com amostras de uso. Áudio, vídeo, DOCX, arquivos compactados e PDFs protegidos por senha ficam fora do primeiro piloto ou exigem fluxo específico. Não executar macros ou conteúdo ativo. Validar assinatura real do arquivo, tamanho e conteúdo, não somente extensão.

RF-12. Os originais devem ser preservados de forma íntegra e cifrada desde o recebimento. A recomendação altera a ordem literal do rascunho: receber primeiro em uma área privada de quarentena e depois resumir e anonimizar. Isso permite processamento assíncrono confiável e mantém os originais necessários ao mediador. Anonimizar o único exemplar destruiria a fonte probatória; manter dados em memória até a IA terminar arriscaria perda e atrasaria o usuário.

Fluxo proposto: criar intenção de upload na API; receber o arquivo em S3 de quarentena com SSE-KMS e TLS; conferir tamanho, checksum e versão do objeto; verificar malware; registrar o original aprovado em área privada definitiva; enfileirar extração e saneamento. Arquivos infectados ou inválidos não avançam e ficam sujeitos à política de descarte. O banco armazena metadados, vínculos e derivados JSON; os binários ficam no S3.

RT-05. Uma URL pré-assinada é uma permissão temporária de acesso a um objeto, não um modo de criptografia. Buckets terão bloqueio de acesso público, políticas IAM mínimas e chaves de objetos sem nomes pessoais. Uploads podem usar autorização temporária restrita a uma chave de quarentena, tamanho e prazo. Para cumprir estritamente “somente a plataforma acessa os originais”, downloads serão transmitidos pela API após autorização. Download direto por URL assinada curta é uma alternativa explícita, pois quem possui o link consegue usá-lo enquanto válido. [F3]

RT-06. Uma URL de upload pode ser reutilizada durante sua validade. Não permitir que uma escrita posterior altere um original já conferido: registrar versionId e hash, consumir somente essa versão e promover para chave definitiva não disponível ao navegador. O processamento nunca busca “a versão mais recente” de uma chave mutável.

RF-13. Remover antes do envio apenas retira o item da tela; remover após o envio e antes do congelamento desvincula a prova da versão corrente, cancela trabalhos pendentes e agenda descarte conforme retenção. Após o congelamento, a operação é negada. Soft delete não equivale a eliminação física: expiração de versões S3 e backups deve obedecer política documentada.

## 7 Extração resumo e anonimização

RT-07. Todo processamento documental será assíncrono, inclusive o realizado localmente. A resposta do upload retorna um ID de trabalho e o frontend acompanha seus estados. Filas separam documentos, notificações e blockchain, evitando que OCR demorado impeça envio de códigos de autenticação.

É possível executar em Python local a extração de texto de PDFs, OCR por ferramenta local, normalização e detecção de padrões como e-mails, telefones e identificadores. Reconhecimento de nomes, endereços e organizações pode combinar modelo de linguagem local e regras brasileiras. Esses métodos precisam de validação em português e não asseguram anonimização completa. Resumo extrativo local é uma primeira opção; resumo semântico de narrativas complexas exige benchmark antes de decidir entre modelo local e OpenRouter.

Pipeline proposto: conferir original → extrair texto/OCR → localizar entidades e referências indiretas → substituir por marcadores consistentes dentro do caso → gerar resumo → validar JSON, fatos, números e referências → executar nova detecção de dados identificáveis → revisar exceções → liberar versão. Tabelas de valores, datas relevantes, obrigações, pedidos e contradições devem sobreviver ao resumo. Informação incerta recebe marcação explícita, sem preenchimento por adivinhação.

RF-14. Usar pseudônimos consistentes para requerente, requerido e terceiros, sem reutilizar o mesmo pseudônimo entre casos. Separar o mapa de correspondência em armazenamento privado cifrado, acessível apenas aos serviços autorizados. Documento saneado e documento resumido são artefatos diferentes: a análise jurídica não deve depender exclusivamente de um resumo que possa omitir uma ressalva importante.

RF-15. Cada derivado recebe UUIDv7, versão de esquema, idioma, referências às fontes, páginas, limitações, versão do pipeline, modelo/provedor quando usados e hash. Guardar o JSON validado em JSONB; preservar a representação canônica exata publicada como artefato imutável. Um novo processamento cria nova versão; não sobrescreve o conteúdo já analisado.

RT-08. Enviar ao OpenRouter preferencialmente texto já saneado. Documento KYC ou prova não saneada constitui uma exceção controlada, com finalidade e fornecedor autorizados, nunca fallback silencioso. Restringir provedores/modelos, desabilitar coleta para treinamento e exigir retenção zero onde contratualmente disponível. Se não houver rota compatível, a tarefa deve parar para revisão. Esses controles não impedem que o fornecedor processe os dados durante a inferência. [F4]

RT-09. Conteúdo dos arquivos é entrada não confiável. Instruções dentro de documentos não podem mudar o comportamento do worker, executar ferramentas, definir URLs de saída ou obter segredos. O extrator usa ambiente isolado, limites de memória/tempo e rede restrita. A LLM devolve esquema validado; nenhum HTML, comando ou decisão de autorização produzido por ela é executado diretamente.

CA-01. Construir corpus autorizado com documentos digitais, scans, tabelas, homônimos e referências indiretas. Medir extração de valores/datas, omissões factuais e identificação de dados pessoais. O conjunto de liberação não pode conter vazamento detectado; isso é um teste, não garantia universal. Durante o piloto, toda publicação pública terá revisão humana registrada.

## 8 Publicação dos dados e acesso do contrato

RF-16. O sistema disponibilizará JSON aprovado em GET /public/v1/cases/{snapshot_uuid}.json. Cada documento saneado terá identidade própria; o snapshot do processo reunirá manifestações e provas aprovadas. A API não publicará os originais, arquivos KYC, nomes de arquivo originais, contatos, endereços, mapa de identidades ou identificadores internos de usuários.

UUIDv7 tem 128 bits e inclui componente temporal. Sua finalidade é identificação e ordenação, não sigilo nem autorização. A URL pública pode ser copiada, indexada ou correlacionada. Desabilitar listagens e solicitar não indexação reduz descoberta casual, mas não torna o acesso privado. [F5]

RN-01. Publicação requer dois controles independentes: avaliação do risco de reidentificação e validação do uso externo de informações da mediação. A LGPD distingue dados efetivamente anonimizados de dados reversíveis ou associáveis por meios razoáveis; nomes mascarados não resolvem todos os casos. A confidencialidade da mediação também deve ser analisada, mesmo quando não restam identificadores diretos. [F1, F2]

Proposta de estados: privado, saneado, aguardando revisão, aprovado para publicação, publicado e retirado. Somente o estado publicado atende requisições públicas. Caso não seja possível liberar o conteúdo com segurança e finalidade válida, bloquear a análise pública e encaminhar para solução privada a ser avaliada com a GenLayer. Não supor que uma URL secreta ou pré-assinada entregue ao contrato permanecerá confidencial.

RN-02. O JSON publicado será imutável e terá hash SHA-256. Para manter a chamada do IC com um único UUID, esse UUID deve identificar o snapshot de análise, distinto do ID estável da mediação. O endpoint retorna sempre os mesmos bytes. Publicar nova versão exige novo UUID. A serialização e a verificação do hash precisam ser iguais no backend e no adaptador do contrato.

A retirada bloqueia futuros acessos e invalida caches controlados, mas não apaga cópias já obtidas nem registros on-chain. Incidentes de publicação interrompem novas análises, retiram o conteúdo e iniciam o processo de resposta. A escolha de conteúdo on-chain deve considerar essa irreversibilidade antes do primeiro envio.

## 9 Pedido convite e adesão

RF-17. Somente usuário habilitado pelo KYC abre um pedido. Criar um rascunho com UUIDv7, requerente, valor em disputa em BRL, provas e carta com pedidos. O editor oferece títulos, listas, negrito, itálico e parágrafos; armazena estrutura de documento validada e renderiza HTML saneado. Colagem ou importação não admite scripts ou recursos remotos ativos.

RF-18. A carta pode ser importada de PDF ou TXT. PDF digital passa por extração e PDF digitalizado por OCR. A importação gera conteúdo para revisão do usuário e preserva o arquivo de origem como anexo; não promete conservar a diagramação original. O usuário confirma o texto antes de enviar.

RF-19. O requerente informa e-mail e/ou telefone do requerido, com pelo menos um canal válido, e propõe o rateio. A tela mostra valor em disputa, honorários totais e valor devido por cada parte antes de enviar o convite. O ID interno pode ser criado no primeiro rascunho para vincular anexos; o protocolo formal é apresentado no envio.

RF-20. O convite envia mensagem pelo canal disponível, explicando a finalidade, o rateio e os próximos passos sem anexar provas ou revelar detalhes sensíveis. O link inclui ID da mediação e token aleatório próprio, de uso controlado, revogável e com prazo. Persistir digest do token. O simples conhecimento do ID não autoriza ingresso no caso.

RF-21. O requerido pode indicar interesse ou recusa na página do convite. A adesão definitiva deve ser vinculada a uma conta autenticada e à versão exata do pedido e do rateio exibidos. Em seguida conclui KYC, apresenta provas e redige contra-argumentos. Quem já tem KYC válido não repete toda a identificação, salvo regra de revisão.

RF-22. Antes do congelamento, cada parte edita apenas seus documentos e sua manifestação. O requerente pode corrigir contatos do destinatário. Depois que o convite estiver vinculado a uma pessoa, alterar o contato não troca silenciosamente a parte: exige cancelamento ou reemissão controlada. Links antigos são revogados quando necessário.

RN-03. Toda alteração material do pedido, valor em disputa ou rateio após aceite invalida esse aceite e exige reconfirmação. Alterações documentais geram novas revisões e aviso à contraparte. O requerido vê a revisão atual antes de “Iniciar mediação”. A API compara a revisão esperada e retorna conflito se houver edição concorrente.

RF-23. “Iniciar mediação” exige ambos os KYC habilitados, adesão e rateio atuais, manifestações presentes e todos os anexos em estado válido. Em uma transação, o backend bloqueia o caso, congela as revisões das duas partes, valores, condições comerciais e versões de termos aceitos, gera o snapshot e cria as obrigações de pagamento. Provas e manifestações não podem ser alteradas por endpoints alternativos.

O rótulo do botão representa o início do processamento operacional. O momento jurídico de instituição da mediação tem regra própria e deve ser refletido nos termos da plataforma. [F1]

## 10 Honorários pagamento e exceções

RN-04. Honorários = R$500,00 + 2% do valor total em disputa. Guardar a tabela de preços e a versão usada em cada caso. Usar centavos inteiros ou Decimal; nunca float binário para cálculos financeiros. Arredondar para centavos com regra única documentada.

| Valor em disputa | Parcela fixa | Parcela percentual | Honorários |
| --- | --- | --- | --- |
| R$10.000,00 | R$500,00 | R$200,00 | R$700,00 |
| R$50.000,00 | R$500,00 | R$1.000,00 | R$1.500,00 |
| R$100.000,00 | R$500,00 | R$2.000,00 | R$2.500,00 |

RN-05. O requerente escolhe pagar 0%, 10%, 20%, até 100%, com complemento para o requerido. Calcular uma cota arredondada e a outra como diferença do total para não perder centavos. Cota zero é “não devida” e nunca gera cobrança. “Ambos pagaram” significa que todas as cotas positivas foram liquidadas.

RF-24. Após congelamento, enviar a ambos aviso de pagamento pendente por e-mail e WhatsApp, conforme canais verificados. Cada parte acessa apenas sua obrigação. Na V1, o checkout será um simulador com opções PIX e cartão de crédito, identificação permanente “Simulação — nenhum valor será cobrado” e comandos de teste para aprovar, recusar ou expirar a operação. Não solicitar número de cartão, CVV, chave PIX ou transferência. O PIX terá apenas representação visual não pagável. Na etapa 2, substituir o adaptador por PSP com checkout hospedado, tokenização, webhooks, consulta e estorno. Fornecedor, parcelamento, tarifas e responsabilidade fiscal permanecem pendentes.

RT-10. O retorno do navegador não confirma pagamento. Na V1, o simulador executa a confirmação no backend por comandos autenticados restritos ao modo simulado; ele também permite testar eventos duplicados e fora de ordem. Na etapa 2, webhook autenticado e consulta de reconciliação atualizam a obrigação. Deduplicar eventos, tolerar eventos fora de ordem e impedir cobrança duplicada por clique ou retry. A soma líquida confirmada deve satisfazer cada obrigação antes de liberar análise. Eventos com valor, moeda ou referência divergentes vão para revisão.

RF-25. Quando todas as cotas positivas estiverem liquidadas (simuladas na V1) e o snapshot liberado para análise, registrar evento de caso pronto. Em falha entre commit e publicação na fila, a outbox garante reenvio. Uma única chave de execução por snapshot impede iniciar duas análises pela repetição do webhook.

RT-10A. Registrar payment_mode = simulated ou live em orçamento, obrigação, tentativa e evento. A simulação não gera receita, comprovante fiscal ou crédito financeiro. Estados simulados devem ser identificados na tela e nos avisos. Sua liberação do fluxo de análise só vale para casos explicitamente configurados no modo simulado; nunca satisfaz cotas live. Na migração, casos existentes conservam seu modo e não são cobrados retroativamente. Restringir a ativação do modo simulado no servidor e auditar comandos de teste. Chamadas reais a IA, mensagens, assinatura ou blockchain podem gerar custos mesmo com cobrança simulada; usar sandboxes/adaptadores falsos por padrão no desenvolvimento e liberar integrações reais por configuração controlada.

RF-26. Prever convite recusado/expirado, abandono de KYC, pagamento parcial, cobrança expirada, falha de provedor, desistência, estorno e chargeback. Antes do pagamento completo não há análise. Estorno ou disputa após análise gera revisão operacional e financeira, preservando o histórico. Nenhum status apaga um resultado já produzido.

A política de reembolso depende de etapa, custos incorridos e validação jurídica. A afirmação atual do site sobre impossibilidade de reembolso após análise não deve virar bloqueio técnico absoluto. Não cobrar o requerido que não aderiu; lembretes de dívida não podem ser enviados a mero convidado.

## 11 Estados e consistência do processo

O estado principal da mediação representa a etapa do serviço. KYC, documentos, pagamentos, processamento e assinatura têm estados próprios. Isso permite mostrar, por exemplo, “pagamento pendente” com um anexo em revisão sem criar dezenas de estados combinados.

| Estado principal | Condição para avançar | Próximo estado |
| --- | --- | --- |
| Rascunho | Pedido válido e convite emitido | Aguardando adesão |
| Aguardando adesão | Aceite autenticado e atual | Em instrução |
| Em instrução | KYC, documentos e revisões válidos; ação do requerido | Aguardando pagamento |
| Aguardando pagamento | Cotas positivas liquidadas e snapshot liberado | Pronto para análise |
| Pronto para análise | Execução registrada pelo worker | Em análise |
| Em análise | Resultado validado e finalizado | Revisão humana |
| Revisão humana | Mediador salva termo e propõe cinco horários | Em agendamento |
| Em agendamento | Interseção confirmada e horário reservado | Agendado |
| Agendado | Sessão iniciada pelo mediador | Em sessão |
| Em sessão | Versão final concordada | Em assinatura |
| Em assinatura | Três assinaturas válidas da mesma versão | Concluído com acordo |

Estados alternativos: convite recusado, convite expirado, cancelado, suspenso, falha técnica recuperável e encerrado sem acordo. Toda transição tem autor, data, motivo e condições verificadas no servidor. Termo final de encerramento deve existir também quando não houver acordo, conforme modelo a aprovar.

RT-11. Usar transações PostgreSQL e controle de concorrência por revisão. Congelamento, cálculo de cotas, emissão do evento e registro do snapshot devem formar uma operação consistente. Integrações externas não permanecem dentro de transações longas; usar estados intermediários, outbox e reconciliação.

RT-12. Comandos relevantes recebem chave de idempotência: convite, cobrança, congelamento, análise, remarcação e assinatura. Repetir a mesma chave e conteúdo retorna a operação existente; reutilizar a chave com conteúdo diferente resulta em conflito. Webhooks têm restrição única por provedor e ID do evento.

## 12 Integração com o comitê GenLayer

RF-27. Um worker consome processos prontos e submete transação ao Intelligent Contract. Persistir rede, endereço do contrato, versão e hash do código, UUID e hash do snapshot, ID da operação, remetente, hash da transação e tentativas. A carteira é da plataforma, com segredo protegido; usuários não precisam de carteira blockchain para mediar.

A interface proposta é analyze_case(snapshot_uuid). O contrato deriva a URL de um domínio fixo autorizado, carrega o snapshot imutável e valida seu esquema. É recomendável também fixar ou verificar o hash de entrada; isso pode exigir registro anterior ou extensão da interface. Não aceitar URLs arbitrárias fornecidas pelo usuário.

RF-28. Acompanhar submissão, execução, eventual decisão provisória e finalização conforme a rede contratada. Não tratar recibo inicial ou resultado provisório como consenso final. Salvar o retorno bruto e a representação normalizada; verificar UUID, esquema e versão esperados antes de liberar o mediador. A infraestrutura GenLayer possui processo próprio de consenso e finalização. [F7]

RT-13. Se houver timeout após envio, procurar a transação existente antes de reenviar. Persistir a transação assinada ou informações suficientes para recuperar seu hash antes da transmissão. Serializar nonces por carteira. Falta de saldo, RPC indisponível, resultado inválido ou ausência de consenso suspendem a operação com motivo e limite de tentativas. Nunca transformar falha em parecer aprovado.

O código ic_v30.py examinado em 29/09/2026 valida IDs numéricos de quatro dígitos, monta URL de dataset e armazena case_id, painel e termo_opcao em um único conjunto de campos. Portanto, não suporta diretamente UUIDv7 e histórico concorrente de várias mediações. A interface pública de análise examinada também precisa de política de autorização e proteção contra reexecução para uso em produção.

Proposta de adaptação: contrato com registros por snapshot UUID, controle do chamador, entrada imutável, resultado recuperável por UUID e execução idempotente. Alternativa a medir: uma instância por processo. Escolher após avaliar armazenamento, taxas e limitações da rede; não reutilizar a instância experimental como se fosse um banco multiusuário. O adaptador Python ficará isolado das dependências da API web.

RF-29. OpenRouter no backend e consenso on-chain são integrações diferentes. O primeiro prepara documentos e executa tarefas auxiliares. O segundo decide a validade do parecer sob o protocolo GenLayer. O runner local de múltiplas LLMs não será apresentado como consenso on-chain. A configuração de provedores OpenRouter não controla automaticamente os modelos dos validadores.

CA-02. Validar em ambiente de teste dois processos concorrentes, recuperação após reinício do worker, indisponibilidade do endpoint público, resultado provisório, finalização, ausência de consenso e tentativa duplicada. Cada resultado deve permanecer associado ao snapshot correto. A versão do IC promovida será escolhida pelo processo de validação do projeto, não por ser a de maior número.

## 13 Administração e mediadores

RF-30. O primeiro administrador é criado por procedimento de bootstrap de uso único, vinculado a identidade previamente autorizada. Deve completar o mesmo KYC e autenticação adicional antes de acessar operações administrativas. Desabilitar o bootstrap após uso. Administradores ativos podem convidar outros administradores; o convite não contorna o KYC.

RF-31. Mediadores somente entram por convite administrativo e completam cadastro, KYC e verificação de capacitação pela operação. Registrar situação ativa/inativa, disponibilidade, conflitos de interesse, atribuições e aceite das regras. KYC verifica identidade; não comprova qualificação profissional.

RF-32. Na criação formal do caso, sortear um mediador elegível, registrando candidatos elegíveis, resultado, data e regra utilizada. A atribuição inicialmente fica oculta às partes. Caso não haja mediador elegível, manter em fila de atribuição e alertar a operação; não perder o processo. Limites de carga podem filtrar os elegíveis antes do sorteio, como política proposta.

RF-33. Após consenso final e liberação para revisão, o mediador é notificado e acessa documentos originais de identificação, provas, cartas, valor em disputa e parecer de IA do caso atribuído. Impedimento, suspeição ou indisponibilidade levam a reassociação auditada. Proposta: revelar o mediador às partes antes do agendamento, com possibilidade de objeção; a seleção interna não substitui sua aceitação pelas partes. [F1]

RF-34. O painel administrativo gerencia convites, habilitação de mediadores, exceções KYC, filas com falha, pagamentos em reconciliação, casos suspensos e políticas versionadas. Ações críticas exigem motivo e reautenticação. Não permitir editar diretamente snapshots, transações pagas, pareceres originais ou acordos assinados, mesmo pelo administrador.

## 14 Revisão humana e versões do termo

RF-35. O resultado estruturado do comitê será preservado integralmente. A primeira minuta de termo derivada dele recebe v1 e referência ao resultado. Se o IC fornecer alternativas ou Termos de Opção, mostrá-los como propostas de negociação; a plataforma não deve selecionar um acordo em nome das partes.

RF-36. O mediador edita livremente a minuta em editor com formatação. Cada clique em Salvar cria nova versão imutável com autor, horário, motivo opcional e referência à versão anterior. Autosave pode preservar um rascunho de recuperação, mas não substitui as versões explícitas. Usar controle de concorrência para que duas abas não sobrescrevam silenciosamente o trabalho.

RF-37. O mediador pode aprovar para discussão, rejeitar o parecer com justificativa ou solicitar complementação. Complementação não desbloqueia o snapshot original: abre uma rodada adicional, com novos anexos, ciência das partes, nova versão de entrada e eventual análise separada. Custos e necessidade de novo aceite dessa rodada são decisões pendentes.

RF-38. “Notificar as partes para agendamento” exige termo salvo e cinco horários válidos. A notificação diz que a minuta está pronta para discussão, sem afirmar que já existe acordo. Registar qual versão foi apresentada e disponibilizada em cada etapa.

O gerador termo_mediador.py poderá apoiar a apresentação das opções; termo_acordo.py poderá apoiar a minuta final. Sua adaptação deve preservar valores definidos pelas partes, não cumulatividade, pendências e proveniência, com revisão das regras já existentes em docs/TERMO_ACORDO_FORMAL.md.

## 15 Agendamento remarcação e sessão

RF-39. O mediador propõe exatamente cinco opções futuras, distintas e reserváveis em sua agenda. Guardar início, término, fuso IANA e rodada. Persistir instantes em UTC e mostrar America/Sao_Paulo por padrão, com fuso explícito para participantes em outras localidades. Proposta inicial: sessões de sessenta minutos, duração ajustável pela operação.

RF-40. Cada parte escolhe exatamente três das mesmas cinco opções. Como 3 + 3 é maior que 5, existe ao menos uma interseção se ambas responderem validamente à mesma rodada. A garantia não vale se alguém recusar todas, não responder ou usar opções de rodadas diferentes. A API rejeita seleção de rodada expirada.

RF-41. Uma única interseção confirma o horário se a reserva ainda estiver válida. Com mais de uma, o mediador escolhe uma delas. Antes de confirmar, verificar conflitos de agenda e reservar atomicamente; liberar as demais opções. Enviar confirmação, instruções e lembretes. Prazos de resposta e de validade das opções são parâmetros pendentes.

RF-42. A parte indisponível nas cinco opções pode solicitar remarcação com justificativa e pagamento. Na V1 a taxa também é simulada. A taxa proposta é R$99 × 2^(n−1), em que n é a remarcação paga solicitada por aquela parte naquele caso: R$99, R$198, R$396 e assim por diante. Contador é individual; solicitação abandonada ou pagamento falho não o incrementa.

RF-43. Após confirmação do pagamento, o mediador abre nova rodada com cinco opções, considerando a justificativa. Invalidar escolhas anteriores e pedir nova seleção a ambos. Para solicitações simultâneas, vincular à mesma rodada de substituição e bloquear cobrança duplicada para a mesma necessidade; regra de quem paga quando ambos pedem deve ser definida antes da produção.

Proposta: remarcação por erro da plataforma ou indisponibilidade do mediador é gratuita e não incrementa o contador. Teto, isenções, contestação, ausência na sessão e desistência precisam de política aprovada. A taxa nunca elimina a possibilidade de encerrar voluntariamente a mediação.

RF-44. Na data marcada, disponibilizar uma sala privada de videoconferência para partes e mediador, com controle de entrada, link protegido e compartilhamento da minuta. Recomenda-se integração com fornecedor de vídeo, em vez de construir infraestrutura WebRTC própria. No piloto, link externo seguro pode atender o fluxo; videoconferência embutida exige escolha de fornecedor. Não gravar a sessão por padrão.

## 16 Acordo assinatura e encerramento

RF-45. Durante a sessão, o mediador apresenta e ajusta o termo com as partes. Antes de solicitar assinaturas, todas as obrigações devem estar fechadas: partes, objeto, valores ou fórmulas plenamente determinadas, prazos, forma de cumprimento e escopo da quitação. O aceite da sugestão de IA não substitui concordância sobre a redação final.

RF-46. Congelar a versão final e gerar PDF para assinatura. Criar envelope de assinatura com requerente, requerido e mediador, vinculando versão, hash do conteúdo e identidades verificadas. Cada signatário acessa sua conta, realiza autenticação adicional quando exigida e manifesta intenção de assinar a versão exibida. Imagem de assinatura colada no PDF não atende, por si, a esse requisito.

RF-47. Usar fornecedor de assinatura eletrônica/digital com trilha de evidências, integridade verificável, API, webhooks e exportação do documento e comprovante. Escolher se o produto exige certificado ICP-Brasil ou outro mecanismo adequado ao ato. Modalidade, fornecedor e requisitos de testemunhas/representação devem ser validados para os casos atendidos; não prometer validade automática de qualquer clique.

RF-48. As três assinaturas precisam corresponder à mesma revisão do conteúdo. Se o texto mudar durante a coleta, cancelar o envelope, preservar seu histórico e solicitar novas assinaturas. PDFs podem receber revisões incrementais do provedor ao incorporar assinaturas; manter o hash da minuta e o hash final, além da evidência de integridade de cada etapa.

RF-49. Após confirmação verificada de todas as assinaturas, arquivar PDF final e evidências em S3 privado, registrar conclusão e notificar os participantes. Permitir download autenticado pelas partes e mediador conforme retenção. O acordo final contém dados pessoais e não integra o endpoint público nem o blockchain.

RF-50. Se não houver consenso, assinatura for recusada ou o procedimento for encerrado, registrar termo de encerramento sem acordo e motivo adequado. O fundamento do termo final com acordo inclui o art. 20 da Lei de Mediação; requisitos de exigibilidade e assinatura devem ser conferidos no modelo aplicável. [F1, F8]

## 17 Arquitetura lógica e tecnologias

RT-14. Adotar um monólito modular para manter transações e regras de negócio em uma base coerente. API e workers podem compartilhar código de domínio e ser implantados separadamente. A divisão em microsserviços só se justifica posteriormente por escala ou isolamento mensurado.

| Camada | Proposta | Responsabilidade |
| --- | --- | --- |
| Site público | HTML/CSS existente em hospedagem estática | Apresentação, conteúdo e aquisição |
| Aplicação web | React e TypeScript, preservando componentes visuais | Fluxos autenticados, uploads, editor e painéis |
| API | Python, Django e Django REST Framework | Autenticação, autorização e regras transacionais |
| Banco | PostgreSQL gerenciado | Cadastros, casos, versões, pagamentos e auditoria |
| Arquivos | S3 privado com SSE-KMS | Quarentena, originais e documentos assinados |
| Filas | SQS e filas de falhas | Documentos, notificações e operações externas |
| Workers | Serviços Python em containers | OCR, saneamento, IA, pagamentos e GenLayer |
| IA auxiliar | OpenRouter por adaptador | Extração KYC e tarefas semânticas autorizadas |
| Comitê | Adaptador Python para GenLayer | Submissão, acompanhamento e resultado on-chain |
| Comunicação | E-mail transacional, GREEN-API e SMS | Convites, códigos e avisos |
| Pagamento | Simulador PIX/cartão na V1; PSP na etapa 2 | Obrigações, eventos e liberação do fluxo |
| Assinatura | Adaptador para fornecedor escolhido | Assinatura verificável e evidências |

A escolha de Django considera a quantidade de cadastros, permissões e operações administrativas. Django REST Framework atende a exposição de APIs. FastAPI é uma alternativa válida se a equipe já o dominar, mas exigirá compor autenticação, administração e outras peças; não há benefício demonstrado em usar os dois frameworks simultaneamente nesta fase. [F9]

Fluxo principal de dados: navegador → API → PostgreSQL; navegador → quarentena S3 mediante autorização; outbox → SQS → worker → derivados privados; liberação → snapshot público → GenLayer; resultado final → PostgreSQL → mediador; termo final → provedor de assinatura → arquivo privado. Somente a projeção aprovada para publicação atravessa a fronteira pública.

Módulos sugeridos: accounts, identity, cases, documents, billing, notifications, committee, mediation, scheduling, agreements e audit. Adaptadores externos devem oferecer operações pequenas e testáveis, sem espalhar formatos de fornecedores pelo domínio.

## 18 Infraestrutura implantação e operação

RT-15. Manter desenvolvimento local, homologação e produção isolados, com bancos, buckets, filas, chaves, carteiras e credenciais próprios. Dados reais de KYC não são copiados para homologação. Usar Docker Compose local e infraestrutura como código na nuvem. Fixar versões compatíveis em lockfiles; atualizar patches com testes de regressão.

Proposta de produção AWS: containers API e workers em ECS Fargate; balanceador HTTPS; RDS PostgreSQL em rede privada; S3, KMS, SQS, Secrets Manager e observabilidade central. Avaliar São Paulo para a camada de dados, conforme disponibilidade e orçamento. Essa escolha não garante residência brasileira de OpenRouter, Google, WhatsApp ou GenLayer; suas transferências devem ser mapeadas separadamente.

O frontend pode continuar na Netlify, usando domínio próprio para a aplicação e subdomínio de API. Se a origem permanecer em netlify.app e o backend em domínio distinto, configurar explicitamente CORS, CSRF e cookies entre sites; preferir proxy de API sob a mesma origem quando viável. API e painel privado nunca usam cache público de respostas autenticadas.

RT-16. PostgreSQL não terá endpoint aberto à internet. API e workers usam identidades IAM diferentes e acesso mínimo ao S3/KMS. Saída dos workers limita-se aos serviços necessários. Contemplar custos de balanceador, NAT ou endpoints privados e transferência de dados no orçamento. Segredos serão rotacionáveis e não entrarão em repositório, frontend ou logs.

RT-17. Cada fila tem política de retry com atraso crescente, limite e fila de falhas. Processamento é idempotente porque mensagens podem chegar mais de uma vez. Ajustar tempo de invisibilidade à tarefa e renovar quando necessário. Uma rotina reconcilia tarefas presas e eventos não publicados; a fila não é a única fonte de estado. [F6]

RT-18. CI executa análise estática, testes de domínio, integração com PostgreSQL e testes de contrato. Deploy publica imagem imutável, aplica migrações compatíveis, valida saúde e permite rollback de aplicação. Mudanças destrutivas de esquema precisam de migração em etapas. Chaves de produção não ficam disponíveis em previews de pull requests.

RT-19. Registrar métricas de idade da fila, tempo por etapa, erro de OCR/IA, tokens e custo, entrega de mensagens, liquidação, falha de assinatura e tempo de consenso. Logs estruturados usam IDs técnicos sem conteúdo de documentos, credenciais ou PII desnecessária. Alertas precisam de responsável e procedimento de resposta, incluindo indisponibilidade da GREEN-API e falta de saldo da carteira.

## 19 Modelo conceitual de dados

IDs principais serão UUIDv7 gerados no backend. Campos monetários usam centavos; datas operacionais usam UTC. Dados pessoais que exigem busca exata poderão usar índice HMAC separado do valor cifrado. Hash simples de identificador de baixa entropia não é proteção adequada contra enumeração.

| Entidade | Conteúdo principal | Relação ou invariável |
| --- | --- | --- |
| User e AuthIdentity | E-mail, hash local, vínculo Google, situação | Um usuário pode ter credenciais vinculadas |
| Profile e KYCVerification | Nome, documento, endereço, telefone e revisões | Histórico preservado; acesso restrito |
| Session e OTPChallenge | Sessões, fator, expiração e tentativas | Código de uso único |
| RoleInvitation e RoleGrant | Convite, papel, emissor e aceite | Concessão somente após habilitação |
| MediationCase e CaseParty | ID, papéis, etapa e revisão corrente | Duas partes na primeira versão |
| CaseInvitation e Acceptance | Destinatário, token, versão e aceite | Aceite vinculado às condições exibidas |
| SubmissionRevision | Carta estruturada e vínculo às provas | Imutável depois de congelada |
| Document e DocumentVersion | Tipo, objeto S3, versionId, hash e dono | Original não sobrescrito |
| ProcessingJob e DocumentDerivative | Pipeline, estado, JSON e referências | Derivado ligado à origem e à versão |
| AnalysisSnapshot e PublicationReview | Manifesto, hash, UUID público e liberação | Bytes públicos imutáveis |
| FeeQuote e PaymentObligation | Tabela, rateio, cota e moeda | Soma das cotas igual ao total |
| PaymentAttempt e ProviderEvent | Checkout, eventos e estornos | ID do evento único por provedor |
| CommitteeRun | Snapshot, contrato, transação e resultado | Uma execução lógica por chave |
| MediatorAssignment | Elegíveis, sorteio e substituições | Apenas atribuição ativa dá acesso |
| AgreementVersion | Conteúdo, autor, v1 e revisões | Versões nunca sobrescritas |
| SchedulingRound e SlotSelection | Cinco opções e três escolhas por parte | Seleções da mesma rodada |
| RescheduleRequest | Parte, contador, justificativa e cobrança | Incremento após pagamento confirmado |
| SignatureEnvelope e Signature | Revisão final, signatários e evidências | Mesmo conteúdo aceito por todos |
| Notification e DeliveryAttempt | Canal, destinatário e status | Envio separado de confirmação de entrega |
| AuditEvent e OutboxEvent | Ação, recurso e evento a publicar | Auditoria protegida e entrega recuperável |

A aplicação exige chaves estrangeiras, unicidade por caso/parte e versão, restrições de percentuais e valores não negativos. O acesso a objetos S3 depende do vínculo no banco. O nome do arquivo nunca é usado para decidir dono ou autorização.

## 20 Contratos de API propostos

Prefixo privado /api/v1. Endpoints abaixo são um contrato inicial de escopo, a detalhar em OpenAPI antes da implementação. Retornos assíncronos usam 202 com job_id; criação usa 201; conflitos de revisão usam 409; acesso negado usa 403 ou 404 conforme política contra enumeração. Erros incluem código estável, mensagem e correlation_id.

| Grupo | Operações principais | Controle específico |
| --- | --- | --- |
| Auth | POST /auth/register, /login, /google, /logout | Rate limit e validação do provedor |
| Recuperação e fator | POST /auth/password-reset, /auth/mfa/challenges, /auth/mfa/verify | Uso único e sessão limitada |
| Perfil e KYC | GET/PATCH /me; POST /kyc/documents, /kyc/submit, /me/phone/verify | Bloqueio de campos imutáveis |
| Casos | POST /cases; GET /cases/{id}; PATCH /cases/{id}/draft | Papel, vínculo e revisão |
| Convites | POST /cases/{id}/invitations; POST /invitations/{token}/accept | Token não é acesso aos documentos |
| Manifestações | POST /cases/{id}/submissions e /imports | Autoria e sanitização |
| Documentos | POST /uploads/intents, /uploads/{id}/complete | Checksum e versão do objeto |
| Provas | DELETE /cases/{id}/documents/{doc}; GET /documents/{id}/content | Editabilidade e streaming privado |
| Congelamento | POST /cases/{id}/freeze | Revisão esperada e transação |
| Pagamentos | GET /cases/{id}/payments; POST /payments/{id}/checkout | Somente a cota do pagador |
| Progresso | GET /jobs/{id}; GET /cases/{id}/timeline | Somente dados visíveis ao papel |
| Mediador | GET /mediator/cases; POST /cases/{id}/agreement-versions | Atribuição e liberação |
| Agenda | POST /cases/{id}/rounds, /rounds/{id}/selections | Cinco opções, três escolhas |
| Remarcação | POST /cases/{id}/reschedules | Rodada, contador e pagamento |
| Assinatura | POST /cases/{id}/signature-envelopes | Versão final congelada |
| Administração | POST /admin/invitations; POST /admin/cases/{id}/reassign | Papel, motivo e auditoria |
| Webhooks | POST /webhooks/{provider} | Autenticação e deduplicação |
| Público | GET /public/v1/cases/{snapshot_uuid}.json | Apenas projeção publicada |

Webhooks não dependem da sessão de navegador. Verificar assinatura criptográfica quando o fornecedor a oferecer, timestamp e replay; caso contrário, combinar credencial de callback e reconciliação autenticada conforme capacidade real do serviço. Nunca aceitar um evento financeiro ou de assinatura apenas por conter o ID correto.

## 21 Segurança privacidade e requisitos operacionais

RT-20. Inventariar dados e finalidades: cadastro, KYC, provas, comunicação, cobrança, análise e assinatura. Definir controlador, operadores, bases legais, avisos de privacidade, contratos e transferências internacionais. Consentimentos e ciência de termos, quando aplicáveis, guardam versão, data e contexto. Não usar autorização genérica como substituto da análise de finalidade.

RT-21. Retenção será definida por categoria e etapa: cadastros incompletos, KYC, convites, provas, acordos, auditoria e backups. Prever bloqueio de exclusão por obrigação de preservação, correção, exportação e eliminação verificável quando cabível. Proposta operacional: uploads órfãos expiram em 24 horas; prazos de documentos de casos exigem decisão jurídica e comercial. Não definir retenção ilimitada por padrão.

RT-22. Implementar TLS, criptografia em repouso, prevenção de XSS/CSRF, limites de upload e requisições, defesa contra enumeração e autorização por objeto. Scanner e renderizador de documentos executam com recursos limitados. O frontend exibe estados de erro sem expor detalhes internos ou dados de terceiros.

RT-23. Auditoria registra acesso a originais, alterações de papel, correções de identidade, publicação, alteração de preço, transições e operações de assinatura. Separar os eventos de domínio do log técnico. Evitar copiar conteúdo sigiloso para a trilha. Proteger o destino de auditoria contra alterações pela credencial ordinária da aplicação.

| Indicador | Meta proposta para piloto | Como verificar |
| --- | --- | --- |
| Disponibilidade da API | 99,5% mensal | Monitoramento externo de operações essenciais |
| Latência da API | p95 menor que 500 ms sem tarefas externas | Teste com carga definida |
| Carga inicial | 50 usuários simultâneos e 100 casos por mês | Ensaio e observação do piloto |
| Recuperação do banco | RPO até 24 h; RTO até 8 h | Restauração real em ambiente isolado |
| Processamento assíncrono | Progresso consultável e falhas explicadas | Testes de interrupção e retomada |
| Acessibilidade | Teclado, leitor de tela e contraste; referência WCAG AA | Auditoria dos fluxos principais |

As metas são hipóteses de dimensionamento. Para operação comercial com maior exigência, propor 99,9%, RPO de quinze minutos e RTO de quatro horas, com PITR, redundância e ensaio de recuperação antes de assumir o compromisso. Tempo de OCR, IA e consenso será medido; não prometer conclusão em minutos para todo caso.

## 22 Validações jurídicas que afetam o produto

O sistema deve apresentar IA e mediador como apoio à composição consensual, sem atribuir a eles poder de impor um acordo. A Lei de Mediação preserva voluntariedade e confidencialidade; a escolha/aceitação do mediador, impedimentos e assistência por advogado afetam o fluxo. Se uma parte comparecer assistida, a situação da outra deve ser tratada conforme a regra legal aplicável. [F1]

O convite do produto precisa ser compatibilizado com os elementos e prazos dos arts. 21 e 22, incluindo escopo, primeira reunião e efeitos da ausência de resposta. O convite preliminar digital e o convite formal podem ser etapas distintas, mas essa distinção exige definição jurídica. Não anunciar que o fluxo atual já satisfaz esses dispositivos. [F1]

Apoiar somente pessoas físicas capazes na primeira entrega é uma proposta de recorte. Empresas exigem CNPJ, representante, documentos de representação e poderes para transigir e assinar. Menores, incapazes, matérias especiais e direitos que exigem homologação precisam de triagem e encaminhamento próprios. A elegibilidade não deve ser decidida autonomamente por uma LLM.

Antes de produção, validar o regulamento de mediação, tratamento das provas compartilhadas, publicação/transferência a terceiros, retenção, honorários, remarcações, reembolsos e assinatura. Essas são dependências da definição do serviço, não afirmações de que qualquer configuração técnica assegura conformidade.

## 23 Critérios de aceite de ponta a ponta

| ID | Cenário | Resultado esperado |
| --- | --- | --- |
| CA-03 | Cadastro local e Google | Contas vinculadas corretamente; nenhum segredo em claro |
| CA-04 | KYC incompleto ou código errado | Abertura/instrução bloqueada; erro recuperável |
| CA-05 | Login de conta habilitada | APIs privadas bloqueadas até segundo fator válido |
| CA-06 | Troca de telefone | Novo número só usado após verificação |
| CA-07 | Upload múltiplo com uma falha | Itens válidos preservados e retry individual |
| CA-08 | PDF malicioso ou URL de upload reutilizada | Sem execução; original conferido não é substituído |
| CA-09 | Dado identificável em resumo | Publicação bloqueada e revisão solicitada |
| CA-10 | Convite aberto por pessoa errada | Sem acesso a provas e sem vínculo automático |
| CA-11 | Pedido alterado após aceite | Nova revisão exige reconfirmação |
| CA-12 | Edição concorrente ao congelamento | Uma revisão consistente; conflito explícito |
| CA-13 | Disputa de R$50 mil e rateio 70/30 | Total R$1.500; cotas R$1.050 e R$450 |
| CA-14 | Rateio 100/0 | Uma obrigação simulada na V1; análise liberada após confirmação |
| CA-15 | Webhook duplicado ou fora de ordem | Sem crédito duplicado nem análise repetida |
| CA-16 | Reinício após envio on-chain | Recupera a transação e o snapshot corretos |
| CA-17 | Falta de consenso ou retorno inválido | Suspensão explicada; sem termo aprovado fictício |
| CA-18 | Mediador salva duas edições | v1 preservada e versões posteriores recuperáveis |
| CA-19 | Três escolhas de cada parte entre cinco | Interseção correta para a mesma rodada |
| CA-20 | Segunda remarcação da mesma parte | R$198; contador da outra parte não muda |
| CA-21 | Alteração durante assinaturas | Envelope anterior invalidado; novos aceites |
| CA-22 | Três assinaturas completas | PDF final privado e evidências disponíveis |
| CA-23 | Acesso cruzado entre casos | API, arquivo e listagens recusam a exposição |
| CA-24 | Perda simulada do banco | Restore recupera vínculos, versões e pagamentos |
| CA-25 | PIX/cartão na V1 | Aviso de simulação e ausência de dados financeiros reais |
| CA-26 | Aprovação, recusa e expiração simuladas | Backend preserva estados e idempotência |
| CA-27 | Evento simulado em caso live | Nenhuma liquidação nem liberação do caso |

A homologação combina testes automatizados de domínio, contrato e integração com testes manuais de identidade, documentos, acessibilidade, assinatura e revisão por mediador. Usar casos sintéticos nas integrações de teste e verificar que a análise local não seja rotulada como consenso GenLayer.

## 24 Plano de implementação e custos

Recomenda-se implementar uma fatia completa com dados sintéticos antes de ampliar volume. Cada fase abaixo produz uma entrega verificável, e não apenas componentes isolados.

| Fase | Entrega | Condição de conclusão |
| --- | --- | --- |
| 0 Decisões e contratos | Escopo do piloto, políticas e prova de integração | Resolver publicação, KYC, assinatura e interface do IC |
| 1 Fundação | Repositório, CI, ambientes, API, cadastro e KYC | Usuário habilitado com isolamento e recuperação |
| 2 Instrução | Upload, pipeline, carta, convite e revisões | Caso das duas partes congelado de forma consistente |
| 3 Simulação e comitê | Cotas, simulador PIX/cartão, snapshot e worker GenLayer | Confirmação simulada libera resultado recuperável |
| 4 Mediação humana | Convites de mediadores, termo, agenda e vídeo | Sessão agendada com versões e remarcação |
| 5 Formalização | Assinaturas, PDF, encerramento e auditoria | Três signatários e recuperação dos artefatos |
| 6 Piloto assistido | V1 com revisão humana e sem cobrança real | Métricas, restore e incidentes validados |
| Etapa 2 Cobrança real | PSP, webhooks, reconciliação e estornos reais | Homologação financeira e políticas aprovadas |

O backend e o frontend podem avançar em paralelo com base em OpenAPI e simuladores, sem acoplar o cronograma à otimização contínua do IC. A integração real e os testes de contrato continuam obrigatórios antes do piloto.

Mesmo sem cobrar as partes na V1, a plataforma pode ter custos reais de infraestrutura e fornecedores. O custo mensal deve ser calculado por: infraestrutura fixa + armazenamento e transferência + OCR/LLM + execução GenLayer + mensagens + pagamento + assinaturas + vídeo + trabalho operacional. Custo por caso deve separar documentos, tokens por etapa, tentativas, chamadas on-chain, número de mensagens e revisões humanas. Honorários recebidos não são margem líquida.

Não há cotação fechada nesta proposta. Volume, tamanho dos arquivos, retenção, região, fornecedores, nível de disponibilidade e equipe ainda precisam ser definidos. Antes de contratar, medir um lote sintético representativo, consultar preços vigentes e estabelecer teto de gasto por caso e por mês, com alerta e interrupção controlada. Não executar chamadas pagas de benchmark sem orçamento autorizado.

## 25 Registro de decisões pendentes

| ID | Decisão necessária | Responsável sugerido | Marco |
| --- | --- | --- | --- |
| D-01 | Pessoas físicas apenas ou também empresas e representantes | Produto e jurídico | Antes do modelo cadastral final |
| D-02 | Garantia do KYC, revisão e eventual prova de vida | Produto e segurança | Antes de habilitar usuários reais |
| D-03 | Publicação do JSON, confidencialidade e transferências | Produto e jurídico | Antes de enviar casos reais à rede |
| D-04 | PSP, parcelamento, reembolsos e fiscal | Financeiro e produto | Etapa 2 antes da cobrança real |
| D-05 | Provedor/modalidade de assinatura e evidências | Jurídico e engenharia | Antes do acordo final |
| D-06 | Rede, contrato multi-caso, versão e custos GenLayer | Engenharia do IC | Antes da integração de produção |
| D-07 | Compartilhamento de provas e complementações | Produto e jurídico | Antes da instrução |
| D-08 | Retenção, eliminação e recuperação de identidade | Jurídico e segurança | Antes de coletar dados reais |
| D-09 | Remarcação, teto, isenções e ausência | Produto e jurídico | Antes do agendamento |
| D-10 | Fornecedores de e-mail, SMS, vídeo e modalidade GREEN-API | Engenharia e operação | Antes da homologação externa |
| D-11 | Prazos de convite, pagamento, resposta e primeira reunião | Produto e jurídico | Antes dos termos de adesão |
| D-12 | Volume, orçamento, disponibilidade e equipe | Responsável pelo projeto | Antes de contratar infraestrutura |
| D-13 | Idiomas das áreas privadas e das minutas | Produto | Antes do frontend autenticado |
| D-14 | Formatos de arquivo, limites e validação do pipeline | Engenharia e mediadores | Antes do piloto documental |

A decisão confirmada para a V1 é pagamento simulado por PIX ou cartão; cobrança real somente na etapa 2. A regra financeira adotada para a simulação é a do rascunho: R$500 + 2%. A publicação do site deve ser atualizada para refletir essa fórmula e o momento correto da cobrança, junto com linguagem precisa sobre IA, sigilo, mediador e assinatura. A especificação não promove uma nova versão do IC e não altera seus resultados experimentais.

## 26 Referências

Fontes consultadas em 29/09/2026. As referências técnicas apoiam escolhas e limitações; os detalhes específicos do produto são propostas desta especificação.

F1. Presidência da República. Lei 13.140 de 2015, especialmente arts. 1, 5, 9, 10, 17, 20, 21, 22 e 30. https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13140.htm

F2. Presidência da República. LGPD, especialmente definição de anonimização e art. 12. https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm

F3. AWS. Download and upload objects with presigned URLs. https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html

F4. OpenRouter. Provider routing e controles de retenção. https://github.com/OpenRouterTeam/docs/blob/main/guides/routing/provider-selection.mdx e https://openrouter.ai/blog/insights/zero-data-retention/

F5. IETF. RFC 9562, UUIDs, seção UUIDv7. https://www.rfc-editor.org/rfc/rfc9562.html

F6. AWS. Amazon SQS at least once delivery. https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues-at-least-once-delivery.html

F7. GenLayer. Transactions e protocolo de consenso. https://docs.genlayer.com/understand-genlayer-protocol/core-concepts/transactions

F8. Presidência da República. Código de Processo Civil, arts. 783 e 784. https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105compilada.htm

F9. Django e Django REST Framework. https://www.djangoproject.com/ e https://www.django-rest-framework.org/

F10. GREEN-API. SendMessage. https://green-api.com/en/docs/api/sending/SendMessage/

Referências do projeto: site https://mediarev1.netlify.app/; arquivo index.html fornecido; README.md; ic_v30.py, em especial analyze_case e get_case; studio_cycle.py; docs/TERMO_ACORDO_FORMAL.md. Caminhos relativos de código são relativos ao repositório mediare-dataset. O HTML fornecido está em /Users/cgmello/Documents/Projetos/Mediare/index.html.
