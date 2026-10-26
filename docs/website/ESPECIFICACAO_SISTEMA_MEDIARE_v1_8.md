# Especificação do Sistema Mediare

Versão 1.8 • 29 de setembro de 2026 • Proposta para validação de produto e engenharia

## 1 Objetivo e diretrizes técnicas

A Mediare será uma plataforma de mediação extrajudicial online que integra identificação das partes, recebimento de provas, pagamento, análise por comitê de IAs da GenLayer, revisão humana, agendamento e assinatura do acordo. Este documento estabelece o comportamento esperado e a infraestrutura necessária para implementar o ciclo completo.

A infraestrutura adotará AWS desde a primeira versão, provisionada por Terraform. O backend Python com Django e Django REST Framework será modular, com API e workers em containers independentes no Amazon ECS com AWS Fargate durante o piloto. O piloto não utilizará Kubernetes, Amazon EKS, Helm ou KEDA. A compatibilidade arquitetural com Kubernetes permanece como diretriz de evolução futura, sem provisionamento ou validação de cluster nesta entrega. Recomenda-se RDS PostgreSQL para dados transacionais, DynamoDB para consulta de artefatos JSON por identificador e S3 privado para originais e representações canônicas dos artefatos. Filas SQS conectarão os trabalhos assíncronos. O frontend preservará a identidade visual existente. OpenRouter atenderá às chamadas de IA feitas pelo backend; a execução do comitê on-chain continuará sob a infraestrutura da GenLayer, por um adaptador independente. PostgreSQL, DynamoDB e S3 não terão acesso direto externo aos dados. Navegadores e integrações acessam as APIs da Mediare; o consumo público do processo ocorre exclusivamente pela API de JSON por UUID, conforme RT-16 e RF-16.

O projeto do website deve evoluir em repositório próprio, separado dos experimentos do IC e do dataset. O contrato entre os dois projetos será um esquema de entrada e saída versionado, com fixtures sintéticas e hashes dos artefatos. A implantação do website não deve promover automaticamente uma versão experimental do IC.

Controle documental: MED-SYS-SPEC, revisão 1.8. Status: proposta para validação, incorporando a decisão confirmada de atender pessoas físicas e empresas na primeira versão. Esta edição mantém o suporte empresarial e propõe processamento documental híbrido, com extração local simples e IA via OpenRouter desde a V1; demais propostas permanecem sujeitas à validação indicada. Não houve execução da infraestrutura.

As regras identificadas como RF são requisitos funcionais. RN são regras de negócio; RT, requisitos técnicos; CA, critérios de aceite; D, decisões pendentes. Uma recomendação indicada como “proposta” não é uma decisão comercial já aprovada. Os parâmetros de capacidade, retenção e operação apresentados são valores iniciais para validação.

## 2 Escopo e análise do material existente

A primeira versão usa pagamentos simulados por PIX e cartão de crédito, conforme decisão de produto. Não há cobrança real, coleta de dados bancários ou de cartão, QR Code PIX pagável nem integração com PSP nesta entrega. O fluxo de pagamento permanece implementado para validar regras e jornadas. Pagamentos reais ficam para a segunda etapa.

O escopo completo abrange portal público, área das partes, área dos mediadores, administração, processamento documental, integrações de pagamento e comunicação, comitê GenLayer, sessão de mediação e assinatura. Não inclui execução judicial do acordo, custódia do valor em disputa ou repasse automático das obrigações negociadas entre as partes. Os honorários da plataforma e o pagamento previsto no acordo são operações diferentes. Pessoas físicas e empresas integram a primeira versão. Em casos empresariais, a empresa atua como requerente ou requerida por meio de representante com conta pessoal e KYC; a empresa não realiza KYC.

O site https://mediarev1.netlify.app/ foi consultado em 29/09/2026, juntamente com o arquivo local index.html. Há uma landing page responsiva, navegação institucional, versões PT/EN/ES, explicação do procedimento, honorários e FAQ. Os botões operacionais mostram um aviso de demonstração. No arquivo examinado não há formulários operacionais nem chamadas fetch ao backend. O layout público pode ser reaproveitado; as telas autenticadas ainda precisam ser implementadas, salvo se existirem em outros arquivos.

O conteúdo do site constitui referência de produto. Em caso de divergência, prevalecem os requisitos e esclarecimentos fornecidos pelo responsável pelo projeto. As diferenças identificadas estão registradas a seguir.

| Tema | Site atual | Base desta especificação |
| --- | --- | --- |
| Honorários | 2% com mínimo de R$500 | R$500 somados a 2% do valor em disputa |
| Cobrança | Após o aceite do convite | Após a entrega do requerido e o congelamento |
| Frontend | Apresentação e botões demonstrativos | Áreas autenticadas e integrações ainda necessárias |
| Identidade | Cita CPF/RG e comprovante de residência | CNH, identidade ou passaporte; endereço informado obrigatório |
| IA | Fala em julgar e em decisão final humana | Parecer de apoio; acordo depende das partes |
| Privacidade | Promete sigilo e anonimização | Publicação de JSON requer avaliação específica |
| Público atendido | Pessoas e empresas | Pessoas físicas e empresas na V1; conta e KYC do representante, empresa identificada como parte |
| Análise adicional | Site permite pedir informações e voltar ao comitê | Nova rodada controlada, sem alterar o snapshot anterior |

Também existem no repositório scripts para produzir Termos de Opção e Termo Final. São componentes candidatos a reaproveitamento após revisão e adaptação; não equivalem a um serviço web pronto.

## 3 Papéis e autorização

Uma pessoa pode ter mais de um papel, mas as permissões devem ser avaliadas por caso e por ação. KYC aprovado não concede papel administrativo ou de mediador. Convites, credenciais e vínculos com casos são entidades distintas. A identidade que se autentica é sempre uma pessoa física. Quando atua em nome de empresa, a autorização considera também o vínculo de representação e a parte empresarial vinculada ao caso; ser representante não concede papel administrativo ou de mediador.

| Papel | Acesso permitido | Restrições |
| --- | --- | --- |
| Visitante | Site, início do cadastro e convite válido | Sem documentos ou dados privados do caso |
| Usuário em cadastro | Próprio cadastro e KYC | Não abre nem instrui casos enquanto não habilitado |
| Requerente | Próprio pedido e casos vinculados | Edita sua manifestação apenas na fase permitida |
| Requerido | Convite vinculado, defesa e casos próprios | Aceite autenticado e KYC da pessoa atuante antes da entrega |
| Representante de empresa | Atuação em nome da empresa nos casos autorizados | Conta e KYC pessoais; vínculo ativo com a empresa e autorização por caso |
| Empresa | Parte requerente ou requerida, com cadastro próprio | Não possui credenciais de login nem realiza KYC |
| Mediador | Casos atribuídos, originais e termos após liberação | Não acessa casos de outros mediadores |
| Administrador | Convites, operação, parâmetros e incidentes | Documentos pessoais exigem permissão específica e auditoria |
| Worker | Recursos exigidos por sua tarefa | Credencial de serviço sem privilégios de usuário |
| Público externo | JSON expressamente liberado | Sem documentos originais ou mapa de identidades |

RT-01. Toda API verifica sessão, segundo fator quando exigido, papel, vínculo ao recurso e estado do fluxo. Um UUID conhecido nunca substitui autorização. Testes devem impedir que uma parte leia o KYC da outra ou modifique objetos de outro caso. Em casos empresariais, verificar a relação entre usuário, empresa, poderes registrados e caso. CNPJ conhecido, domínio do e-mail ou inclusão do nome de uma empresa no perfil não concedem acesso aos processos dela.

Proposta de visibilidade: cada parte vê sua identidade completa, suas provas e os documentos do procedimento compartilhados. Provas da outra parte poderão ser compartilhadas após adesão, conforme política de contraditório a aprovar. Documentos de KYC não integram automaticamente esse conjunto. O mediador recebe acesso amplo aos originais do caso atribuído na revisão humana; toda abertura ou download é auditado.

## 4 Cadastro, autenticação e recuperação de acesso

RF-01. O cadastro por e-mail exige e-mail, senha e confirmação de senha. A confirmação é validada e descartada. O sistema armazena hash adaptativo da senha, preferencialmente Argon2id, nunca senha legível ou reversivelmente cifrada. O e-mail deve ser verificado antes de habilitar a conta. Respostas de recuperação não revelam se uma conta existe. A conta é sempre de pessoa física, inclusive quando criada para representar uma empresa. A opção “Empresa” pertence ao cadastro dessa pessoa e abre o formulário empresarial; não cria uma conta de login compartilhada pela empresa.

RF-02. O cadastro e login Google usam OpenID Connect. Além do e-mail solicitado, é tecnicamente necessário persistir o identificador estável do provedor, composto por issuer e subject, para vinculação segura. Nenhuma senha Google é armazenada. Validar assinatura, emissor, audiência, validade, nonce e fluxo de autorização. A coincidência de e-mail não autoriza a união automática de contas; vinculação exige autenticação da conta existente.

RF-03. A funcionalidade de recuperação de senha envia um link de uso único e expiração curta. Após a troca, revogar sessões anteriores e notificar o titular. Conta exclusivamente Google deve ser orientada ao provedor; criar senha local é um fluxo separado, com reautenticação. Recuperação de acesso não altera identidade civil nem dispensa o segundo fator.

RF-04. Após KYC completo, todo novo login, inclusive via Google, deve passar pelo desafio adicional escolhido entre e-mail, SMS ou WhatsApp. Antes de concluí-lo, a sessão permite apenas verificar o código, sair e recuperar acesso. Renovar uma sessão válida não deve ser tratado como login novo; expiração, inatividade e duração máxima serão configuradas.

RT-02. Proposta inicial para códigos: seis dígitos, validade de cinco minutos, uso único, até cinco tentativas, intervalo mínimo de sessenta segundos para reenvio e limites por conta, destino e IP. Armazenar digest protegido por segredo do servidor, não o código em claro. Invalidar desafios anteriores ao reenviar. Logs nunca registram códigos, links de recuperação ou tokens.

RT-03. Sessões do navegador usam cookies Secure e HttpOnly, proteção CSRF e lista explícita de origens confiáveis. Segredos não ficam no localStorage. O segundo fator por e-mail é uma opção comercial solicitada, mas sua independência é limitada quando o login Google e a caixa de e-mail são a mesma conta. Recomenda-se TOTP ou passkey para administradores e mediadores, como reforço sujeito a aprovação.

## 5 Identificação e manutenção do perfil

RF-05. O KYC possui três etapas: documento, perfil e verificação do telefone. Aceitar CNH, carteira de identidade, incluindo RG/CIN conforme o documento apresentado, ou passaporte. Solicitar frente e verso quando aplicável. Guardar tipo, país/emissor, número extraído, nome completo, arquivo de origem, data, versão do extrator e resultado da conferência. Um número isolado não é chave global confiável. Em atuação empresarial, essas três etapas são exigidas somente do representante. A empresa não recebe solicitação de documento de identidade, foto, biometria ou etapa de KYC.

RF-06. A IA pode extrair nome e número do documento; a aprovação de identidade depende dos controles de verificação definidos. Primeiro executar validações locais de arquivo, legibilidade e extração; em seguida usar a chamada autorizada via backend/OpenRouter para a etapa de IA prevista. Qualquer envio de documento pessoal a fornecedor externo exige configuração de privacidade e finalidade próprias, separadas da análise do mérito. Saídas incertas, inconsistentes ou não legíveis seguem para revisão humana e reenvio.

Extrair texto de um documento não comprova autenticidade nem que o portador é seu titular. Decidir o nível de garantia exigido: conferência documental manual, fornecedor especializado, prova de vida ou outra evidência. A foto opcional do perfil não deve ser tratada como biometria verificada. A ativação comercial depende dessa decisão; o sistema não deve apresentar “identidade verificada” quando apenas houve OCR.

RF-07. O perfil exige endereço no Brasil com CEP, logradouro, número ou indicação sem número, complemento quando houver, bairro, município e UF. Foto é opcional; telefone é obrigatório porque sua confirmação conclui o KYC. Validar estrutura do endereço sem confundir consulta de CEP com comprovação de residência. Comprovante de residência não é obrigatório no rascunho e depende de decisão adicional.

RF-08. A GREEN-API envia o código WhatsApp gerado e validado pela Mediare. O status de entrega da mensagem não comprova a posse do telefone: somente a digitação correta do código conclui a verificação. Na indisponibilidade, manter a etapa pendente e permitir reenvio controlado; substituição desse canal para o KYC depende de regra aprovada.

RF-09. Nome completo, e-mail e identificação são imutáveis pelo autosserviço após a confirmação. Foto, endereço e telefone podem ser alterados. A troca de telefone exige reautenticação, registra o novo número como pendente e só o ativa após verificação; o número pendente nunca pode receber códigos de login. Perda do número anterior usa recuperação por canal já confiável ou revisão de identidade.

RT-04. Deve existir processo administrativo auditado para erro de OCR, mudança legal de nome e exercício de direitos de correção, com nova verificação e histórico. Esse procedimento não concede permissão de edição irrestrita. Alterar o perfil não reescreve a qualificação preservada em um snapshot ou acordo assinado. Caso sejam necessários CPF ou documentos de poderes de representação para assinatura, coletá-los em fluxo próprio; não inferir esses dados a partir de documentos que não os comprovem. O CNPJ é coletado no cadastro empresarial previsto na seção 5A.

Estados de KYC: não iniciado, documento recebido, em processamento, revisão necessária, perfil pendente, telefone pendente, aprovado, recusado e suspenso. Cada transição guarda motivo e responsável. KYC recusado deve admitir correção ou contestação por suporte.

### 5A Cadastro empresarial e representação

RF-51. Disponibilizar a opção “Empresa” na área de cadastro e edição do perfil da pessoa física. Ao selecioná-la, abrir formulário adicional com nome fantasia, razão social (nome empresarial, correspondente ao “nome social” solicitado para a empresa), CNPJ e endereço completo da empresa no Brasil. O endereço contém CEP, logradouro, número ou indicação sem número, complemento quando houver, bairro, município e UF. Os dados empresariais são separados do nome, documento e endereço pessoal do representante. Proposta de validação: razão social, CNPJ e endereço são obrigatórios; permitir informar que a empresa não possui nome fantasia, usando a razão social na apresentação.

RF-52. O representante mantém seu próprio cadastro, login, recuperação de acesso, KYC completo e segundo fator. A empresa não faz KYC e não possui senha, sessão ou segundo fator próprios. A habilitação para atuar em nome dela depende do KYC válido do representante, do cadastro empresarial completo e de vínculo de representação ativo para o caso. Validar estrutura e unicidade do CNPJ é controle cadastral, não KYC empresarial. Registrar CNPJ como texto, preservando a representação e aplicando normalização e validação compatíveis com o padrão vigente.

RF-53. Vincular explicitamente usuário e empresa em um registro de representação, com estado, escopo de atuação, data e histórico. No primeiro cadastro, associar a empresa ao representante autenticado. Se o CNPJ já existir, não duplicar a empresa nem conceder acesso automaticamente: encaminhar o vínculo por fluxo controlado de convite ou análise administrativa. Registrar a declaração de poderes para atuar e assinar em nome da empresa. O procedimento e as evidências para validar esses poderes serão definidos em D-18, separadamente do KYC da pessoa física e sem instituir KYC da empresa.

RF-54. Antes de criar um pedido ou aderir a um convite, a interface deve indicar explicitamente se o usuário atua em nome próprio ou de uma empresa vinculada. Quando a escolha for empresa, ela será a parte requerente ou requerida; o usuário será o representante responsável pelas ações. Não inferir a parte somente pela última empresa acessada. A estrutura de dados admite múltiplos vínculos; a habilitação de representantes adicionais exige controle explícito de acesso. Cada caso registra o representante responsável de cada parte empresarial.

RF-55. Em telas, convites, e-mails, mensagens WhatsApp, avisos de pagamento, agendamento e documentos do procedimento, identificar a parte empresarial pela empresa. Nome fantasia pode ser usado na apresentação, acompanhado da razão social quando necessário para identificação inequívoca; na ausência de nome fantasia, usar a razão social. O nome do representante não substitui o da empresa como parte. Entregar mensagens aos canais autorizados do representante responsável, mantendo na auditoria destinatário, usuário atuante e empresa representada. Mensagens de acesso e segurança continuam vinculadas à conta pessoal; quando contextualizadas por uma empresa, devem identificá-la sem tratar a empresa como titular das credenciais.

RF-56. O representante autorizado pode atualizar endereço empresarial e nome fantasia por fluxo auditado. Alterações de razão social ou CNPJ exigem correção cadastral controlada, com histórico; mudar o CNPJ para trocar a parte de um caso não é permitido. Dados empresariais e vínculo de representação são preservados em versões privadas do caso. Atualizar o cadastro não reescreve convites já aceitos, snapshots congelados ou acordos assinados. A substituição de representante exige vínculo ativo, KYC do substituto, motivo, comunicação às partes e revalidação dos poderes; assinaturas pendentes seguem o tratamento da seção 16.

RF-57. Para uma parte empresarial, o Termo de Acordo identifica a empresa por razão social, nome fantasia quando existente, CNPJ e endereço, e identifica a pessoa física que assina na qualidade de representante. O representante se autentica e assina com sua própria identidade em nome da empresa, sem assumir no sistema a posição de parte em nome próprio. O envelope e a trilha de evidências devem relacionar empresa, representante, versão dos dados e poderes de representação registrados. O mediador continua assinando em sua função própria.

## 6 Upload e preservação dos originais

RF-10. A tela permite selecionar arquivos, selecionar pasta quando suportado pelo navegador e arrastar arquivos. Expandir pastas em arquivos individuais. Cada arquivo ganha uma linha com nome, tamanho, progresso, estado, mensagem de erro e lixeira. “Enviar todos” inicia os itens pendentes; a falha de um item preserva os demais. Oferecer seleção múltipla como alternativa em navegadores sem suporte a pastas.

RF-11. Proposta inicial de formatos: PDF, TXT, JPEG e PNG; 25 MB por arquivo, 100 arquivos e 500 MB por caso. Limites são configuráveis e devem ser validados com amostras de uso. Áudio, vídeo, DOCX, arquivos compactados e PDFs protegidos por senha ficam fora do primeiro piloto ou exigem fluxo específico. Não executar macros ou conteúdo ativo. Validar assinatura real do arquivo, tamanho e conteúdo, não somente extensão.

RF-12. Os originais devem ser preservados de forma íntegra e cifrada desde o recebimento. A recomendação altera a ordem literal do rascunho: receber primeiro em uma área privada de quarentena e depois resumir e anonimizar. Isso permite processamento assíncrono confiável e mantém os originais necessários ao mediador. A preservação do original garante a disponibilidade da fonte probatória. O armazenamento durável anterior ao processamento evita depender da memória do processo e da conclusão síncrona da chamada de IA.

Fluxo proposto: criar intenção de upload na API; transmitir o arquivo do navegador para o backend por HTTPS autenticado; o backend grava em S3 de quarentena por endpoint VPC, com SSE-KMS e TLS; conferir tamanho, checksum e versão do objeto; verificar malware; registrar o original aprovado em área privada definitiva; enfileirar extração e saneamento. Arquivos infectados ou inválidos não avançam e ficam sujeitos à política de descarte. PostgreSQL armazena metadados e vínculos; DynamoDB mantém a projeção consultável dos derivados JSON; S3 preserva binários e bytes canônicos. As responsabilidades de cada armazenamento estão definidas na seção 19.

RT-05. Todo upload e download de documentos passa pela API autenticada da Mediare. O backend verifica usuário, vínculo, estado e limites, e realiza o acesso interno ao S3 com sua identidade IAM. Não fornecer ao navegador ou a terceiros URLs pré-assinadas do S3, credenciais AWS, nomes de bucket ou chaves de objeto. Buckets terão bloqueio de acesso público, IAM mínimo, criptografia e políticas que restrinjam operações de dados aos endpoints VPC autorizados. Transferir arquivos por streaming ou partes controladas pela API, com memória limitada, limites de tamanho/concorrência, timeout e recuperação de falhas; não exigir manter o arquivo inteiro em memória. A intenção de upload retorna somente IDs e endereços da API da plataforma. [F20]

RT-06. Vincular a intenção de upload ao usuário, caso, tamanho permitido, prazo e estado. A conclusão é validada pelo backend após a gravação durável; repetir a operação não pode sobrescrever um original conferido. Registrar versionId e hash, consumir somente essa versão e promover para chave definitiva controlada pelo serviço interno. O processamento nunca busca “a versão mais recente” de uma chave mutável. URLs da API não autorizam acesso direto ao S3 nem permitem escolher livremente bucket ou chave.

RF-13. Remover antes do envio apenas retira o item da tela; remover após o envio e antes do congelamento desvincula a prova da versão corrente, cancela trabalhos pendentes e agenda descarte conforme retenção. Após o congelamento, a operação é negada. Soft delete não equivale a eliminação física: expiração de versões S3 e backups deve obedecer política documentada.

## 7 Extração, resumo e anonimização

RT-07. Todo processamento documental será assíncrono, inclusive o realizado localmente. A resposta do upload retorna um ID de trabalho e o frontend acompanha seus estados. Filas separam documentos, notificações e blockchain, evitando que OCR demorado impeça envio de códigos de autenticação.

Diretriz técnica proposta para a V1: adotar processamento híbrido, com IA via OpenRouter prevista desde o início para resumo semântico, estruturação de informações e apoio à anonimização. Manter em Python a leitura de TXT, a extração da camada textual de PDFs e os controles determinísticos. “Local” significa execução dentro do worker da Mediare na AWS, sem envio ao provedor nessa etapa; não significa processamento no computador do usuário. Modelos de linguagem hospedados pela própria Mediare e uma infraestrutura própria de OCR não serão pré-requisitos da primeira entrega.

A extração local de texto é tecnicamente viável: bibliotecas como PyMuPDF recuperam texto já incorporado ao PDF. Porém, a ordem dos blocos pode divergir da leitura visual. PDFs digitalizados e fotos exigem reconhecimento de imagem; OCR local com Tesseract também é possível, mas é uma etapa distinta da extração da camada textual. Essas capacidades não equivalem à compreensão, ao resumo ou à anonimização do conteúdo. [F16]

| Etapa ou tipo de entrada | Caminho proposto para a V1 | Critério de qualidade |
| --- | --- | --- |
| TXT e PDF com texto utilizável | Extração local no worker Python | Cobertura das páginas, legibilidade e ordem verificadas |
| Scan, foto ou página sem texto utilizável | OCR ou modelo multimodal via OpenRouter, em rota autorizada | Texto e elementos visuais recuperados com referência à página |
| Tabela ou layout complexo | Avaliar extração e usar rota visual quando a estrutura não for preservada | Relações entre linhas, colunas e valores conferidas |
| Resumo e estruturação dos fatos | LLM via OpenRouter sobre conteúdo preparado | Pedidos, valores, datas, ressalvas e fontes preservados |
| Tratamento de identificadores | Regras locais + apoio semântico de LLM + validação | Pseudônimos consistentes e referências indiretas revisadas |
| Liberação pública | Validação automática e revisão humana conforme configuração administrativa | Revisão humana ligada por padrão no piloto; dispensa não elimina os demais controles |

A recomendação de usar IA desde a V1 é uma escolha de arquitetura, não resultado de benchmark já executado. Não se presume que toda LLM leia documentos melhor que um extrator ou OCR dedicado. O modelo, o mecanismo de leitura e seus limiares de qualidade serão selecionados com amostras representativas, conforme D-19.

Pipeline proposto: conferir original → avaliar texto e conteúdo visual por página → extrair localmente ou usar leitura externa autorizada → aplicar mascaramento inicial → usar IA para estruturar, resumir e localizar referências identificáveis → consolidar pseudônimos → validar JSON, fatos, números e fontes → executar nova detecção de identificadores → aplicar política vigente de revisão humana → liberar versão. Tabelas de valores, datas relevantes, obrigações, pedidos e contradições devem sobreviver ao resumo. Informações incertas devem receber marcação explícita, sem complementação factual não sustentada pelas fontes.

RF-14. Usar pseudônimos consistentes para requerente, requerido e terceiros, sem reutilizar o mesmo pseudônimo entre casos. Separar o mapa de correspondência em armazenamento privado cifrado, acessível apenas aos serviços autorizados. Documento saneado e documento resumido são artefatos diferentes: a análise jurídica não deve depender exclusivamente de um resumo que possa omitir uma ressalva importante. Em casos empresariais, a versão destinada ao endpoint público também remove ou substitui razão social, nome fantasia, CNPJ, endereço e referências ao representante que permitam identificar as partes. A identificação nominal da empresa nas comunicações privadas não altera a política de anonimização dos artefatos públicos.

RF-15. Cada derivado recebe UUIDv7, versão de esquema, idioma, referências às fontes, páginas, limitações, versão do pipeline, modelo/provedor quando usados e hash. Guardar o JSON validado na camada de artefatos DynamoDB/S3 descrita na seção 19; preservar a representação canônica exata publicada como artefato imutável. PostgreSQL mantém os vínculos, a revisão aprovada e as decisões de acesso. Um novo processamento cria nova versão; não sobrescreve o conteúdo já analisado.

RT-08. Antes de chamadas semânticas ao OpenRouter, aplicar mascaramento local dos identificadores detectáveis. Esse pré-processamento não comprova anonimização: dados residuais ainda podem identificar pessoas ou empresas. Enviar KYC, imagens, PDFs originais ou conteúdo parcialmente saneado somente em rota externa autorizada para essa categoria e finalidade, conforme a decisão D-03. Restringir modelos e provedores, desabilitar coleta para treinamento e configurar retenção zero nos endpoints compatíveis. As mesmas condições devem ser verificadas para componentes de OCR e parsing intermediários; a configuração da LLM final não comprova, por si só, a política de todo o caminho. Ausência de rota compatível mantém a tarefa pendente para revisão ou reenvio, sem encaminhamento silencioso a outro fornecedor. Retenção zero não impede o processamento durante a inferência. [F4, F19]

RT-09. Conteúdo dos arquivos é entrada não confiável. Instruções dentro de documentos não podem mudar o comportamento do worker, executar ferramentas, definir URLs de saída ou obter segredos. O extrator usa ambiente isolado, limites de memória/tempo e rede restrita. A LLM devolve esquema validado; nenhum HTML, comando ou decisão de autorização produzido por ela é executado diretamente.

RT-41. A escolha da rota de leitura deve ocorrer por página e por componente relevante. Verificar presença e qualidade da camada textual, páginas sem cobertura, caracteres inválidos, tabelas e imagens com evidências. Um PDF com texto selecionável pode conter fotos, carimbos ou anexos digitalizados que também precisam de análise. Não aprovar a extração somente por contagem de caracteres. Imagens cuja interpretação seja necessária devem chegar a um modelo compatível ou à revisão humana, mesmo quando houver texto na mesma página.

RT-42. Usar adaptadores separados para leitura documental e processamento semântico. No OpenRouter, configurar explicitamente o mecanismo de PDF compatível com a rota aprovada; não depender de seleção automática de parser ou provedor. Documentos privados serão transmitidos pelo backend no corpo da requisição, sem tornar o bucket público. A documentação prevê suporte nativo de PDF ou extração por parser, com custos e limites próprios, inclusive de imagens encaminhadas ao modelo. Testar a cobertura visual, os limites de arquivo e o custo total da rota selecionada. [F17]

RT-43. Solicitar saída estruturada com JSON Schema nos endpoints compatíveis e validar novamente no backend. A conformidade do JSON não comprova exatidão factual. Separar transcrição, conteúdo saneado e resumo em artefatos versionados; manter página/bloco de origem para fatos relevantes, registrar incertezas e conferir valores, datas e tabelas. Não permitir que a LLM complete texto ilegível com conteúdo presumido. No mapa de identidades, pseudônimos já atribuídos pelo backend não podem ser redefinidos em outra etapa. [F18]

RT-44. Para documentos extensos, dividir o processamento em unidades com origem rastreável, preservando contexto entre páginas e relações de tabelas; consolidar somente após confirmar a cobertura integral. Persistir modelo, provedor, parser, versão do prompt, esquema, hash de entrada, páginas processadas, custo e tentativas. Reutilizar resultados concluídos da mesma versão para evitar reprocessamento desnecessário; expirar dados intermediários conforme retenção. Configurar limites de páginas, tokens, concorrência, timeout, custo por documento e tentativas. Saída truncada, página ausente, divergência factual ou falha persistente impede liberação automática. OCR local pode ser incorporado posteriormente como alternativa de custo e privacidade após avaliação, sem alterar a interface do pipeline.

CA-01. Construir corpus autorizado com documentos digitais, scans, tabelas, homônimos e referências indiretas. Medir extração de valores/datas, omissões factuais e identificação de dados pessoais. O conjunto de liberação não pode conter vazamento detectado; isso é um teste, não garantia universal. No piloto, a configuração require_human_publication_review inicia ligada. Enquanto ligada, toda publicação pública exige revisão humana registrada da versão exata do artefato; o administrador do site pode desligá-la ou religá-la conforme RF-58. Com a configuração desligada, a liberação pode ocorrer automaticamente após os demais controles, registrando que não houve revisão humana e qual política foi aplicada. Comparar as rotas local e externa em um conjunto de validação separado das amostras usadas para ajustar prompts; medir também cobertura visual, latência e custo por documento. Nenhuma chamada paga foi executada para fundamentar esta especificação.

## 8 Publicação dos dados e acesso do contrato

RF-16. O sistema disponibilizará JSON aprovado em GET /public/v1/cases/{snapshot_uuid}.json. Cada documento saneado terá identidade própria; o snapshot do processo reunirá manifestações e provas aprovadas. A API pública não disponibilizará os originais, arquivos KYC, nomes de arquivo originais, contatos, endereços, mapa de identidades ou identificadores internos de usuários. O endpoint é público e não exige login: dado o UUID público do processo para análise, devolve no corpo HTTP o JSON saneado e liberado, no mesmo modelo de consumo por identificador usado pelo dataset. A API consulta internamente o estado de publicação e recupera o artefato canônico pelos serviços privados. Resposta de sucesso usa 200 e Content-Type application/json; UUID desconhecido, não publicado ou retirado retorna 404 sem revelar dados internos. Não retornar redirecionamento, URL de S3, tabela DynamoDB, chave de objeto ou credencial. O UUID corresponde ao snapshot imutável de análise, conforme RN-02, preservando os mesmos bytes enquanto publicado; o ID operacional interno da mediação continua separado. A rota aplica limites de requisição compatíveis com o consumo pelo comitê e não disponibiliza listagem pública de processos.

UUIDv7 tem 128 bits e inclui componente temporal. Sua finalidade é identificação e ordenação, não sigilo nem autorização. A URL pública pode ser copiada, indexada ou correlacionada. Desabilitar listagens e solicitar não indexação reduz descoberta casual, mas não torna o acesso privado. [F5]

RN-01. Publicação requer dois controles independentes: avaliação do risco de reidentificação e validação do uso externo de informações da mediação. A LGPD distingue dados efetivamente anonimizados de dados reversíveis ou associáveis por meios razoáveis; nomes mascarados não resolvem todos os casos. A confidencialidade da mediação também deve ser analisada, mesmo quando não restam identificadores diretos. [F1, F2]

Proposta de estados: privado, saneado, aguardando revisão, aprovado para publicação, publicado e retirado. Com a revisão humana ligada, o artefato aguarda aprovação de um revisor autorizado. Com ela desligada, pode avançar de saneado para aprovado para publicação após as validações obrigatórias; a aprovação é registrada como automática, sem atribuir revisor humano fictício. Somente o estado publicado atende requisições públicas. Caso não seja possível liberar o conteúdo com segurança e finalidade válida, bloquear a análise pública e encaminhar para solução privada a ser avaliada com a GenLayer. O contrato recebe somente o UUID e consulta a API pública da Mediare; não recebe URL pré-assinada, credencial ou acesso direto ao armazenamento.

RF-58. O painel administrativo deve oferecer a opção “Exigir revisão humana antes da publicação pública”, associada à configuração booleana require_human_publication_review. O administrador do site pode ligar ou desligar a exigência, com valor inicial true no piloto. A configuração é centralizada e versionada por ambiente no PostgreSQL, aplicada pelo backend a todas as novas liberações de documentos e snapshots públicos. A tela mostra valor atual, data e autor da última alteração; alterações exigem sessão administrativa válida, reautenticação e motivo conforme RF-34, com registro do valor anterior, novo valor e versão da política. Reinícios e deploys preservam a escolha persistida.

RT-45. O serviço de publicação verifica a política vigente no momento de autorizar a transição para publicado. A política e a aprovação pertencem à versão exata do artefato: mudança de conteúdo exige nova avaliação. Com a exigência ligada, a publicação requer aprovação humana válida; com ela desligada, exige sucesso nas validações automáticas e nos demais controles de liberação, inclusive os definidos em RN-01. A dispensa humana não ignora falhas de anonimização, páginas ausentes, inconsistências ou rejeições ainda não resolvidas. Registrar modo de aprovação, versão da política, resultado dos controles, data e revisor quando existir. Usar transação ou comparação de revisão para impedir publicação com uma configuração desatualizada em caso de alteração concorrente; se a política não puder ser lida, não publicar.

Ao desligar a exigência, itens aguardando revisão podem ser reavaliados pelo worker e liberados somente após os demais controles; a alteração isolada não publica todo o lote diretamente. Ao religar, todos os itens ainda não publicados passam a exigir aprovação humana válida, inclusive trabalhos já em processamento. A mudança não retira automaticamente artefatos já publicados nem altera o histórico de sua liberação. Essa opção controla somente a revisão anterior à publicação pública: não desliga o KYC, a revisão do mediador, a assinatura ou outros controles do procedimento.

RN-02. O JSON publicado será imutável e terá hash SHA-256. Para manter a chamada do IC com um único UUID, esse UUID deve identificar o snapshot de análise, distinto do ID estável da mediação. O endpoint retorna sempre os mesmos bytes. Publicar nova versão exige novo UUID. A serialização e a verificação do hash precisam ser iguais no backend e no adaptador do contrato.

A retirada bloqueia futuros acessos e invalida caches controlados, mas não apaga cópias já obtidas nem registros on-chain. Incidentes de publicação interrompem novas análises, retiram o conteúdo e iniciam o processo de resposta. A escolha de conteúdo on-chain deve considerar essa irreversibilidade antes do primeiro envio.

## 9 Pedido, convite e adesão

RF-17. Somente usuário habilitado pelo KYC abre um pedido. Criar um rascunho com UUIDv7, requerente, valor em disputa em BRL, provas e carta com pedidos. O editor oferece títulos, listas, negrito, itálico e parágrafos; armazena estrutura de documento validada e renderiza HTML saneado. Colagem ou importação não admite scripts ou recursos remotos ativos. Em nome de empresa, exigir os controles da seção 5A e registrar empresa como requerente, usuário como ator e representante, além da revisão cadastral utilizada. O mesmo fluxo atende PF × PF, PF × PJ, PJ × PF e PJ × PJ; permanecem duas partes por mediação.

RF-18. A carta pode ser importada de PDF ou TXT. PDF digital passa por extração e PDF digitalizado por OCR. A importação gera conteúdo para revisão do usuário e preserva o arquivo de origem como anexo; não promete conservar a diagramação original. O usuário confirma o texto antes de enviar.

RF-19. O requerente informa e-mail e/ou telefone do requerido, com pelo menos um canal válido, e propõe o rateio. A tela mostra valor em disputa, honorários totais e valor devido por cada parte antes de enviar o convite. O ID interno pode ser criado no primeiro rascunho para vincular anexos; o protocolo formal é apresentado no envio. Se o requerido for empresa, permitir indicar essa condição e os dados empresariais conhecidos, sem exigir informações que o requerente não possua. O convite deve ser conciliado com a empresa informada por quem adere; divergências de CNPJ ou de parte exigem correção e nova confirmação, nunca troca automática da parte.

RF-20. O convite envia mensagem pelo canal disponível, explicando a finalidade, o rateio e os próximos passos sem anexar provas ou revelar detalhes sensíveis. O link inclui ID da mediação e token aleatório próprio, de uso controlado, revogável e com prazo. Persistir digest do token. O simples conhecimento do ID não autoriza ingresso no caso. Quando a parte convidante for empresa, a mensagem e a página do convite a apresentam como requerente. Quando o convite identificar uma empresa como requerida, o destinatário é orientado a entrar com sua conta pessoal e atuar como representante dessa empresa.

RF-21. O requerido pode indicar interesse ou recusa na página do convite. A adesão definitiva deve ser vinculada a uma conta autenticada e à versão exata do pedido e do rateio exibidos. Em seguida conclui KYC, apresenta provas e redige contra-argumentos. Quem já tem KYC válido não repete toda a identificação, salvo regra de revisão. Em adesão empresarial, o representante conclui ou reutiliza seu KYC, seleciona ou cadastra a empresa e confirma atuação em seu nome. O aceite registra empresa, representante, vínculo, revisão do pedido e rateio; a empresa não passa por KYC.

RF-22. Antes do congelamento, cada parte pode editar somente seus documentos e sua manifestação. O requerente pode corrigir contatos do destinatário. Depois que o convite estiver vinculado a uma pessoa, a alteração do contato não modifica a identidade da parte vinculada: exige cancelamento ou reemissão controlada. Links antigos são revogados quando necessário.

RN-03. Toda alteração material do pedido, valor em disputa ou rateio após aceite invalida esse aceite e exige reconfirmação. Alterações documentais geram novas revisões e aviso à contraparte. O requerido vê a revisão atual antes de “Iniciar mediação”. A API compara a revisão esperada e retorna conflito se houver edição concorrente.

RF-23. “Iniciar mediação” exige KYC habilitado das pessoas que atuam por ambas as partes — em nome próprio ou como representantes —, adesão e rateio atuais, manifestações presentes e todos os anexos em estado válido. Em uma transação, o backend bloqueia o caso, congela as revisões das duas partes, valores, condições comerciais e versões de termos aceitos, gera o snapshot e cria as obrigações de pagamento. Provas e manifestações não podem ser alteradas por endpoints alternativos. Para partes empresariais, validar os vínculos de representação e congelar, em registro privado, os dados da empresa, a identificação do representante e os poderes registrados. O snapshot público recebe exclusivamente a projeção saneada desses dados.

O rótulo do botão representa o início do processamento operacional. O momento jurídico de instituição da mediação tem regra própria e deve ser refletido nos termos da plataforma. [F1]

## 10 Honorários, pagamento e exceções

RN-04. Honorários = R$500,00 + 2% do valor total em disputa. Guardar a tabela de preços e a versão usada em cada caso. Usar centavos inteiros ou Decimal; nunca float binário para cálculos financeiros. Arredondar para centavos com regra única documentada.

| Valor em disputa | Parcela fixa | Parcela percentual | Honorários |
| --- | --- | --- | --- |
| R$10.000,00 | R$500,00 | R$200,00 | R$700,00 |
| R$50.000,00 | R$500,00 | R$1.000,00 | R$1.500,00 |
| R$100.000,00 | R$500,00 | R$2.000,00 | R$2.500,00 |

RN-05. O requerente escolhe pagar 0%, 10%, 20%, até 100%, com complemento para o requerido. Calcular uma cota arredondada e a outra como diferença do total, preservando a igualdade entre a soma das cotas e os honorários. Cota zero é “não devida” e nunca gera cobrança. “Ambos pagaram” significa que todas as cotas positivas foram liquidadas. A obrigação é vinculada à parte: pessoa física ou empresa. No caso empresarial, o representante opera o checkout em nome da empresa, e sua identidade fica registrada como ator; a simulação não altera a identidade da parte obrigada.

RF-24. Após congelamento, enviar a ambos aviso de pagamento pendente por e-mail e WhatsApp, conforme canais verificados. Cada parte acessa apenas sua obrigação. Na V1, o checkout será um simulador com opções PIX e cartão de crédito, identificação permanente “Simulação — nenhum valor será cobrado” e comandos de teste para aprovar, recusar ou expirar a operação. Não solicitar número de cartão, CVV, chave PIX ou transferência. O PIX terá apenas representação visual não pagável. Na etapa 2, substituir o adaptador por PSP com checkout hospedado, tokenização, webhooks, consulta e estorno. Fornecedor, parcelamento, tarifas e responsabilidade fiscal permanecem pendentes.

RT-10. O retorno do navegador não confirma pagamento. Na V1, o simulador executa a confirmação no backend por comandos autenticados restritos ao modo simulado; ele também permite testar eventos duplicados e fora de ordem. Na etapa 2, webhook autenticado e consulta de reconciliação atualizam a obrigação. Deduplicar eventos, tolerar eventos fora de ordem e impedir cobrança duplicada por clique ou retry. A soma líquida confirmada deve satisfazer cada obrigação antes de liberar análise. Eventos com valor, moeda ou referência divergentes vão para revisão.

RF-25. Quando todas as cotas positivas estiverem liquidadas (simuladas na V1) e o snapshot liberado para análise, registrar evento de caso pronto. Em falha entre commit e publicação na fila, a outbox garante reenvio. Uma única chave de execução por snapshot impede iniciar duas análises pela repetição do webhook.

RT-10A. Registrar payment_mode = simulated ou live em orçamento, obrigação, tentativa e evento. A simulação não gera receita, comprovante fiscal ou crédito financeiro. Estados simulados devem ser identificados na tela e nos avisos. Sua liberação do fluxo de análise só vale para casos explicitamente configurados no modo simulado; nunca satisfaz cotas live. Na migração, casos existentes conservam seu modo e não são cobrados retroativamente. Restringir a ativação do modo simulado no servidor e auditar comandos de teste. Chamadas reais a IA, mensagens, assinatura ou blockchain podem gerar custos mesmo com cobrança simulada; usar sandboxes/adaptadores falsos por padrão no desenvolvimento e liberar integrações reais por configuração controlada.

RF-26. Prever convite recusado/expirado, abandono de KYC, pagamento parcial, cobrança expirada, falha de provedor, desistência, estorno e chargeback. Antes do pagamento completo não há análise. Estorno ou disputa após análise gera revisão operacional e financeira, preservando o histórico. Nenhum status apaga um resultado já produzido.

A política de reembolso depende de etapa, custos incorridos e validação jurídica. A afirmação atual do site sobre impossibilidade de reembolso após análise não deve virar bloqueio técnico absoluto. Não cobrar o requerido que não aderiu; lembretes de dívida não podem ser enviados a mero convidado.

## 11 Estados e consistência do processo

O estado principal da mediação representa a etapa do serviço. KYC, documentos, pagamentos, processamento e assinatura têm estados próprios. Isso permite mostrar, por exemplo, “pagamento pendente” com um anexo em revisão sem criar dezenas de estados combinados.

### 11A Diagrama do fluxo principal

![Figura 11.1 · Fluxo principal da mediação](DIAGRAMA_ESTADOS_MEDIARE.svg)

O diagrama segue as setas em três linhas: da esquerda para a direita, depois em sentido inverso e, por fim, da esquerda para a direita. A tabela abaixo detalha a condição exigida para cada transição. Na V1, o pagamento é simulado. “Revisão humana” é a revisão do mediador após o resultado do comitê; a opção administrativa de revisão da publicação pública pertence ao processamento documental e não remove esse estado.


| Estado principal | Condição para avançar | Próximo estado |
| --- | --- | --- |
| Rascunho | Pedido válido e convite emitido | Aguardando adesão |
| Aguardando adesão | Aceite autenticado e atual | Em instrução |
| Em instrução | KYC das pessoas atuantes, representação quando aplicável, documentos e revisões válidos; ação do requerido | Aguardando pagamento |
| Aguardando pagamento | Cotas positivas liquidadas e snapshot liberado | Pronto para análise |
| Pronto para análise | Execução registrada pelo worker | Em análise |
| Em análise | Resultado validado e finalizado | Revisão humana |
| Revisão humana | Mediador salva termo e propõe cinco horários | Em agendamento |
| Em agendamento | Interseção confirmada e horário reservado | Agendado |
| Agendado | Sessão iniciada pelo mediador | Em sessão |
| Em sessão | Versão final concordada | Em assinatura |
| Em assinatura | Três assinaturas válidas da mesma versão | Concluído com acordo |

### 11B Estados alternativos e retomada

![Figura 11.2 · Estados alternativos e retomada](DIAGRAMA_ESTADOS_ALTERNATIVOS_MEDIARE.svg)

Estados alternativos: convite recusado, convite expirado, cancelado, suspenso, falha técnica recuperável e encerrado sem acordo. Toda transição tem autor, data, motivo e condições verificadas no servidor. Termo final de encerramento deve existir também quando não houver acordo, conforme modelo a aprovar. “Etapa ativa elegível” representa uma etapa na qual a regra correspondente permite a interrupção ou o encerramento; não autoriza cancelar ou reabrir qualquer estado indiscriminadamente. As setas tracejadas indicam retomada após resolução e revalidação da última etapa válida, com idempotência e sem apagar o histórico. O diagrama não define reabertura automática de convites recusados/expirados ou de processos encerrados.

RT-11. Usar transações PostgreSQL e controle de concorrência por revisão. Congelamento, cálculo de cotas, emissão do evento e registro do snapshot devem formar uma operação consistente. Integrações externas não permanecem dentro de transações longas; usar estados intermediários, outbox e reconciliação.

RT-12. Comandos relevantes recebem chave de idempotência: convite, cobrança, congelamento, análise, remarcação e assinatura. Repetir a mesma chave e conteúdo retorna a operação existente; reutilizar a chave com conteúdo diferente resulta em conflito. Webhooks têm restrição única por provedor e ID do evento.

## 12 Integração com o comitê GenLayer

RF-27. Um worker consome processos prontos e submete transação ao Intelligent Contract. Persistir rede, endereço do contrato, versão e hash do código, UUID e hash do snapshot, ID da operação, remetente, hash da transação e tentativas. A carteira é da plataforma, com segredo protegido; usuários não precisam de carteira blockchain para mediar.

A interface proposta é analyze_case(snapshot_uuid). O contrato deriva a URL de um domínio fixo autorizado, carrega o snapshot imutável e valida seu esquema. É recomendável também fixar ou verificar o hash de entrada; isso pode exigir registro anterior ou extensão da interface. Não aceitar URLs arbitrárias fornecidas pelo usuário.

RF-28. Acompanhar submissão, execução, eventual decisão provisória e finalização conforme a rede contratada. Não tratar recibo inicial ou resultado provisório como consenso final. Salvar o retorno bruto e a representação normalizada; verificar UUID, esquema e versão esperados antes de liberar o mediador. A infraestrutura GenLayer possui processo próprio de consenso e finalização. [F7]

RT-13. Se houver timeout após envio, procurar a transação existente antes de reenviar. Persistir a transação assinada ou informações suficientes para recuperar seu hash antes da transmissão. Serializar nonces por carteira. Falta de saldo, RPC indisponível, resultado inválido ou ausência de consenso suspendem a operação com motivo e limite de tentativas. Falhas técnicas não podem produzir status de parecer aprovado.

O código ic_v30.py examinado em 29/09/2026 valida IDs numéricos de quatro dígitos, monta URL de dataset e armazena case_id, painel e termo_opcao em um único conjunto de campos. Portanto, não suporta diretamente UUIDv7 e histórico concorrente de várias mediações. A interface pública de análise examinada também precisa de política de autorização e proteção contra reexecução para uso em produção.

Proposta de adaptação: contrato com registros por snapshot UUID, controle do chamador, entrada imutável, resultado recuperável por UUID e execução idempotente. Alternativa a medir: uma instância por processo. Escolher após avaliar armazenamento, taxas e limitações da rede; a instância experimental não deve ser utilizada como armazenamento concorrente de múltiplos casos sem a adaptação correspondente. O adaptador Python ficará isolado das dependências da API web.

RF-29. OpenRouter no backend e consenso on-chain são integrações diferentes. O primeiro prepara documentos e executa tarefas auxiliares. O segundo decide a validade do parecer sob o protocolo GenLayer. O runner local de múltiplas LLMs não será apresentado como consenso on-chain. A configuração de provedores OpenRouter não controla automaticamente os modelos dos validadores.

CA-02. Validar em ambiente de teste dois processos concorrentes, recuperação após reinício do worker, indisponibilidade do endpoint público, resultado provisório, finalização, ausência de consenso e tentativa duplicada. Cada resultado deve permanecer associado ao snapshot correto. A versão do IC promovida será escolhida pelo processo de validação do projeto, com base em evidências de validação, independentemente da numeração da versão.

## 13 Administração e mediadores

RF-30. O primeiro administrador é criado por procedimento de bootstrap de uso único, vinculado a identidade previamente autorizada. Deve completar o mesmo KYC e autenticação adicional antes de acessar operações administrativas. Desabilitar o bootstrap após uso. Administradores ativos podem convidar outros administradores; o convite não contorna o KYC.

RF-31. Mediadores somente entram por convite administrativo e completam cadastro, KYC e verificação de capacitação pela operação. Registrar situação ativa/inativa, disponibilidade, conflitos de interesse, atribuições e aceite das regras. KYC verifica identidade; não comprova qualificação profissional.

RF-32. Na criação formal do caso, sortear um mediador elegível, registrando candidatos elegíveis, resultado, data e regra utilizada. A atribuição inicialmente fica oculta às partes. Caso não haja mediador elegível, manter em fila de atribuição e alertar a operação; preservar o caso e sua posição no fluxo operacional. Limites de carga podem filtrar os elegíveis antes do sorteio, como política proposta.

RF-33. Após consenso final e liberação para revisão, o mediador é notificado e acessa documentos originais de identificação, provas, cartas, valor em disputa e parecer de IA do caso atribuído. Impedimento, suspeição ou indisponibilidade levam a reassociação auditada. Proposta: revelar o mediador às partes antes do agendamento, com possibilidade de objeção; a seleção interna não substitui sua aceitação pelas partes. [F1] Em casos empresariais, o mediador também acessa o cadastro privado da empresa, os dados de seu representante e os registros de representação autorizados para aquele caso.

RF-34. O painel administrativo gerencia convites, habilitação de mediadores, exceções KYC, filas com falha, pagamentos em reconciliação, casos suspensos e políticas versionadas, incluindo ligar ou desligar a revisão humana de publicações públicas conforme RF-58. Ações críticas exigem motivo e reautenticação. Não permitir editar diretamente snapshots, transações pagas, pareceres originais ou acordos assinados, mesmo pelo administrador.

## 14 Revisão humana e versões do termo

RF-35. O resultado estruturado do comitê será preservado integralmente. A primeira minuta de termo derivada dele recebe v1 e referência ao resultado. Se o IC fornecer alternativas ou Termos de Opção, mostrá-los como propostas de negociação; a plataforma não deve selecionar um acordo em nome das partes.

RF-36. O mediador edita livremente a minuta em editor com formatação. Cada clique em Salvar cria nova versão imutável com autor, horário, motivo opcional e referência à versão anterior. Autosave pode preservar um rascunho de recuperação, mas não substitui as versões explícitas. Usar controle de concorrência para que duas abas não sobrescrevam silenciosamente o trabalho.

RF-37. O mediador pode aprovar para discussão, rejeitar o parecer com justificativa ou solicitar complementação. Complementação não desbloqueia o snapshot original: abre uma rodada adicional, com novos anexos, ciência das partes, nova versão de entrada e eventual análise separada. Custos e necessidade de novo aceite dessa rodada são decisões pendentes.

RF-38. “Notificar as partes para agendamento” exige termo salvo e cinco horários válidos. A notificação diz que a minuta está pronta para discussão, sem afirmar que já existe acordo. Registrar qual versão foi apresentada e disponibilizada em cada etapa.

O gerador termo_mediador.py poderá apoiar a apresentação das opções; termo_acordo.py poderá apoiar a minuta final. Sua adaptação deve preservar valores definidos pelas partes, não cumulatividade, pendências e proveniência, com revisão das regras já existentes em docs/TERMO_ACORDO_FORMAL.md.

## 15 Agendamento, remarcação e sessão

RF-39. O mediador propõe exatamente cinco opções futuras, distintas e reserváveis em sua agenda. Guardar início, término, fuso IANA e rodada. Persistir instantes em UTC e mostrar America/Sao_Paulo por padrão, com fuso explícito para participantes em outras localidades. Proposta inicial: sessões de sessenta minutos, duração ajustável pela operação.

RF-40. Para responder à rodada de agendamento, cada parte deve escolher pelo menos três das mesmas cinco opções — podendo marcar três, quatro ou todas as cinco — ou solicitar remarcação com multa conforme RF-42. A interface mostra a quantidade selecionada e permite confirmar a seleção somente com três a cinco opções distintas da rodada vigente. A API rejeita confirmação com menos de três opções, opções repetidas, inexistentes ou pertencentes a outra rodada, bem como rodada expirada. Como cada conjunto contém pelo menos três elementos entre cinco, há ao menos uma interseção quando ambas as partes confirmam seleções válidas da mesma rodada. A garantia não se aplica enquanto houver remarcação pendente ou ausência de resposta; esses eventos não equivalem a seleção nem geram aceite automático.

RF-41. Uma única interseção confirma o horário se a reserva ainda estiver válida. Com mais de uma, o mediador escolhe uma delas. Antes de confirmar, verificar conflitos de agenda e reservar atomicamente; liberar as demais opções. Enviar confirmação, instruções e lembretes. Prazos de resposta e de validade das opções são parâmetros pendentes.

RF-42. Como alternativa à seleção de pelo menos três horários, a parte pode solicitar remarcação com justificativa e pagamento de multa. Essa opção atende inclusive quem dispõe de somente um ou dois dos cinco horários. Na V1, a multa é simulada. Mantém-se o valor inicial proposto de R$99 e a progressão R$99 × 2^(n−1), em que n é a remarcação paga solicitada por aquela parte naquele caso: R$99, R$198, R$396 e assim por diante. Mostrar a multa aplicável antes de confirmar a solicitação. O contador é individual; solicitação abandonada ou pagamento falho não o incrementa. A nova rodada depende da confirmação do pagamento, conforme RF-43.

RF-43. Após confirmação do pagamento, o mediador abre nova rodada com cinco opções, considerando a justificativa. Invalidar escolhas anteriores e pedir nova seleção a ambos. Para solicitações simultâneas, vincular à mesma rodada de substituição e bloquear cobrança duplicada para a mesma necessidade; regra de quem paga quando ambos pedem deve ser definida antes da produção.

Proposta: remarcação por erro da plataforma ou indisponibilidade do mediador é gratuita e não incrementa o contador. Teto, isenções, contestação, ausência na sessão e desistência precisam de política aprovada. A multa de remarcação não elimina a possibilidade de encerrar voluntariamente a mediação.

RF-44. Após a confirmação do dia e horário da sessão, o mediador responsável pode cadastrar na Mediare o link da videoconferência criada no serviço de sua preferência, como Zoom, Google Meet, Microsoft Teams ou outro equivalente. O link pode ser inserido posteriormente ao agendamento, inclusive no dia da sessão, e deve estar disponível até seu início. Não exigir o link para confirmar o horário; enquanto ausente, mostrar às partes “Link da videoconferência a ser informado pelo mediador”. Na V1, a plataforma armazena e disponibiliza a URL externa; não cria salas automaticamente nem exige integração por API, contas conectadas ou vídeo incorporado.

O cadastro da sala permite informar serviço, URL HTTPS e instruções de acesso opcionais. Somente o mediador atualmente atribuído ao caso pode inserir ou alterar o link; o backend registra autor, data, versão e sessão vinculada. Validar o formato e o esquema da URL sem buscar automaticamente seu conteúdo. Publicar o botão “Entrar na videoconferência” na área autenticada do caso, abrindo o serviço externo. O link fica restrito às partes, aos representantes autorizados quando houver empresa e ao mediador, sem inclusão no JSON público ou no resultado on-chain.

Ao cadastrar ou alterar o link, notificar ambas as partes pelos canais previstos, direcionando-as à área autenticada da sessão para consultar o endereço vigente e as instruções. A confirmação inicial do horário pode ser enviada antes da inclusão do link. Alterar apenas a URL não modifica o agendamento nem gera multa de remarcação. Após uma mudança de dia ou horário, exigir que o mediador confirme a validade do link para a nova sessão ou informe outro; não reutilizar silenciosamente dados da rodada anterior. Preservar o histórico, sem apresentar links substituídos como vigentes.

O mediador administra a sala e os controles de entrada no serviço escolhido, acompanha o acesso das partes e utiliza os recursos externos para discutir a minuta. A Mediare continua responsável pelo termo, versões, agendamento e assinatura. Não gravar a sessão por padrão. O início e o encerramento da sessão são registrados pelo mediador no sistema; abrir o link não comprova presença nem inicia automaticamente o estado “Em sessão”.

## 16 Acordo, assinatura e encerramento

RF-45. Durante a sessão, o mediador apresenta e ajusta o termo com as partes. Antes de solicitar assinaturas, todas as obrigações devem estar fechadas: partes, objeto, valores ou fórmulas plenamente determinadas, prazos, forma de cumprimento e escopo da quitação. O aceite da sugestão de IA não substitui concordância sobre a redação final.

RF-46. Congelar a versão final e gerar PDF para assinatura. Criar envelope de assinatura com requerente, requerido e mediador, vinculando versão, hash do conteúdo e identidades verificadas. Cada signatário acessa sua conta, realiza autenticação adicional quando exigida e manifesta intenção de assinar a versão exibida. Imagem de assinatura colada no PDF não atende, por si, a esse requisito. Quando requerente ou requerido for empresa, o signatário humano correspondente é seu representante habilitado, com a empresa indicada como parte representada. No fluxo padrão permanecem três assinaturas: uma por cada parte, prestada pessoalmente ou por representante, e a do mediador. Eventual exigência de representação conjunta deve ser tratada na definição de D-18, antes de habilitar esse caso.

RF-47. Usar fornecedor de assinatura eletrônica/digital com trilha de evidências, integridade verificável, API, webhooks e exportação do documento e comprovante. Escolher se o produto exige certificado ICP-Brasil ou outro mecanismo adequado ao ato. Modalidade, fornecedor e requisitos de testemunhas/representação devem ser validados para os casos atendidos; não prometer validade automática de qualquer clique. A integração escolhida deve permitir envio e recuperação do documento pelo backend, sem depender de acesso do fornecedor a um bucket ou URL pré-assinada do S3.

RF-48. As três assinaturas precisam corresponder à mesma revisão do conteúdo. Se o texto mudar durante a coleta, cancelar o envelope, preservar seu histórico e solicitar novas assinaturas. PDFs podem receber revisões incrementais do provedor ao incorporar assinaturas; manter o hash da minuta e o hash final, além da evidência de integridade de cada etapa. Se houver substituição de representante antes da conclusão, cancelar o envelope pendente e gerar outro com o signatário atualizado, preservando os registros anteriores e solicitando novas assinaturas. A assinatura concluída de representante depois substituído permanece no histórico, sem transferência da assinatura ao novo usuário.

RF-49. Após confirmação verificada de todas as assinaturas, arquivar PDF final e evidências em S3 privado, registrar conclusão e notificar os participantes. Permitir download autenticado pelas partes e mediador conforme retenção. O acordo final contém dados pessoais e não integra o endpoint público nem o blockchain. Para empresa, o download é realizado por representante com vínculo e permissão atuais para o caso; a simples titularidade de um cadastro com o mesmo CNPJ não concede acesso.

RF-50. Se não houver consenso, assinatura for recusada ou o procedimento for encerrado, registrar termo de encerramento sem acordo e motivo adequado. O fundamento do termo final com acordo inclui o art. 20 da Lei de Mediação; requisitos de exigibilidade e assinatura devem ser conferidos no modelo aplicável. [F1, F8]

## 17 Arquitetura lógica e tecnologias

### 17A Infraestrutura AWS do piloto

![Figura 17.1 · Infraestrutura AWS do piloto — ECS Fargate, sem Kubernetes](DIAGRAMA_INFRA_AWS_MEDIARE.svg)

O diagrama utiliza os ícones coloridos originais do pacote oficial AWS Architecture Icons de 31/07/2026, incorporados ao documento para leitura offline. As caixas distinguem serviços globais de entrada, região, VPC, sub-redes e serviços gerenciados. S3, DynamoDB e SQS ficam fora da VPC como serviços regionais, acessados internamente por endpoints e políticas; somente PostgreSQL está nas sub-redes privadas de banco. A faixa de suporte é uma referência lógica: IAM tem escopo global, e os demais serviços usam a região aplicável. Não representa um segundo caminho de entrada para clientes. [F22]

Clientes acessam CloudFront e o Application Load Balancer, que encaminha tráfego aos serviços web e API no ECS Fargate. Route 53 resolve DNS; não é um proxy no caminho dos dados. ACM fornece os certificados TLS conforme o recurso. O ALB deve aceitar o tráfego da origem autorizada e encaminhar somente às tarefas esperadas. O frontend é servido por container; o S3 não é origem pública do site. A API e os workers acessam os dados privados; integrações externas usam saída controlada por NAT e Internet Gateway. A resposta HTTP retorna pelo mesmo caminho de entrada, embora as setas mostrem apenas o sentido da solicitação.

O desenho é uma visão lógica, não um dimensionamento de réplicas ou zonas de disponibilidade. O Terraform define a distribuição em sub-redes/AZs exigida pelos serviços e a capacidade do piloto. Endpoints gateway atendem S3 e DynamoDB; o endpoint de interface para SQS é a proposta representada. Serviços de suporte incluem IAM, KMS, Secrets Manager, ECR e CloudWatch. Não há componentes Kubernetes neste diagrama nem na implantação do piloto.

### 17B Componentes e responsabilidades

RT-14. Adotar domínio modular com API e workers implantáveis e escaláveis separadamente. Cada módulo expõe serviços de aplicação e interfaces de repositório/adaptador; integrações AWS ficam nas implementações dessas interfaces. API e workers podem compartilhar uma biblioteca de domínio versionada. Os módulos não devem depender de memória compartilhada, disco local persistente ou invocação direta de objetos de outro processo. Kubernetes não exige decompor todas as entidades em microsserviços; transações relacionais continuam no módulo responsável.

| Camada | Proposta | Responsabilidade |
| --- | --- | --- |
| Site público e aplicação web | Frontend em container; CloudFront com origem HTTP da aplicação | Distribuição dos arquivos estáticos e TLS, sem origem S3 exposta |
| Aplicação web | React e TypeScript, preservando componentes visuais | Fluxos autenticados, uploads, editor e painéis |
| API | Python, Django e Django REST Framework | Autenticação, autorização e regras transacionais |
| Banco transacional | Amazon RDS PostgreSQL privado | Identidade, acesso, casos, pagamentos e auditoria; somente serviços internos |
| Banco de artefatos JSON | Amazon DynamoDB restrito à rede e aos papéis internos | Projeções imutáveis consultadas por serviços internos, nunca pelo cliente externo |
| Arquivos | S3 interno com SSE-KMS e endpoint VPC | Quarentena, originais, JSON canônico e acordos; toda entrega externa é pela API |
| Filas | SQS e filas de falhas | Documentos, notificações e operações externas |
| Execução do piloto | Amazon ECS com AWS Fargate | API e workers isolados por carga; sem Kubernetes/EKS no piloto |
| Infraestrutura como código | Terraform modular por ambiente | Rede, segurança, dados, filas e execução |
| IA auxiliar | OpenRouter por adaptadores de leitura e semântica | KYC, OCR/visão quando necessário, resumo e apoio à anonimização; controles locais no worker |
| Comitê | Adaptador Python para GenLayer | Submissão, acompanhamento e resultado on-chain |
| Comunicação | E-mail transacional, GREEN-API e SMS | Convites, códigos e avisos |
| Videoconferência | Link externo cadastrado pelo mediador | Zoom, Google Meet, Teams ou outro serviço de sua escolha; sem integração por API na V1 |
| Pagamento | Simulador PIX/cartão na V1; PSP na etapa 2 | Obrigações, eventos e liberação do fluxo |
| Assinatura | Adaptador para fornecedor escolhido | Assinatura verificável e evidências |

A escolha de Django considera a quantidade de cadastros, permissões e operações administrativas. Django REST Framework atende a exposição de APIs. FastAPI é uma alternativa válida se a equipe já o dominar, mas exigirá compor autenticação, administração e outras peças; não há benefício demonstrado em usar os dois frameworks simultaneamente nesta fase. [F9]

Fluxo principal de dados: navegador → API → PostgreSQL privado; navegador → API de upload → quarentena S3 por endpoint interno; outbox → SQS → worker → JSON canônico no S3 e projeção no DynamoDB; ativação e liberação no PostgreSQL → API pública de JSON por UUID → GenLayer; resultado final → camada de artefatos e vínculo transacional → mediador; termo final → provedor de assinatura → arquivo privado. Somente a projeção aprovada para publicação atravessa a fronteira pública.

Módulos sugeridos: accounts, identity, cases, documents, billing, notifications, committee, mediation, scheduling, agreements e audit. Adaptadores externos devem oferecer operações pequenas e testáveis, mantendo os formatos específicos dos fornecedores restritos à camada de integração.

## 18 Infraestrutura AWS do piloto e evolução futura

RT-15. AWS é requisito desde o primeiro ambiente implantado. Manter desenvolvimento local, homologação e produção isolados, preferencialmente com contas AWS distintas para produção e ambientes de teste. Bancos, buckets, filas, chaves, carteiras e credenciais são próprios de cada ambiente. Dados reais de KYC não serão copiados para homologação. Docker Compose serve ao desenvolvimento; a homologação usa os serviços AWS reais necessários para validar IAM, filas e armazenamento.

Decisão de implantação: o piloto executará no Amazon ECS com AWS Fargate, com API e workers em serviços separados. Não haverá cluster Kubernetes ou EKS, nodes/pods Kubernetes, instalação de Helm, KEDA ou ferramentas de operação de Kubernetes no piloto. Não há validação em cluster como condição de lançamento dessa versão. Amazon EKS permanece uma alternativa de evolução posterior, a ser planejada quando houver decisão específica de migração. RDS, DynamoDB, S3 e SQS permanecem serviços gerenciados fora do cluster; os dados continuam acessíveis somente pelos serviços internos autorizados da plataforma. Migrar o runtime não deve recriar esses recursos nem alterar a identidade dos casos.

A região primária proposta é sa-east-1, São Paulo, sujeita à disponibilidade dos serviços e ao orçamento. Essa escolha não garante residência brasileira de OpenRouter, Google, WhatsApp, assinatura ou GenLayer; as transferências externas precisam ser tratadas separadamente. A aplicação começa em uma região; replicação multirregional exige projeto próprio.

### 18A Unidades de execução

RT-24. Definir comandos de entrada independentes para api, worker-documents, worker-notifications, worker-committee, outbox-dispatcher e reconciliation. API não executa OCR nem espera inferência ou consenso dentro de uma requisição. A mesma imagem pode atender comandos diferentes, mas cada unidade terá recursos, escala e identidade IAM próprios. Na V1, extração textual simples permanece no worker e a leitura complexa usa a rota OpenRouter autorizada. Se OCR local for incorporado depois, suas dependências pesadas podem ter imagem separada. A distribuição do frontend pode usar um serviço separado de arquivos estáticos em container, atrás da entrada HTTPS, sem abrir acesso externo ao S3. A API de upload será dimensionada para transferência de arquivos; processamento documental continua nos workers.

RT-25. Containers OCI serão reproduzíveis, executados como usuário não privilegiado, com configuração externa, limites de CPU/memória e logs estruturados em stdout/stderr. Arquivos temporários são descartáveis, limitados e limpos. Sessões, progresso de tarefas, locks e resultados ficam em serviços externos. Nenhuma requisição exige afinidade com um pod específico.

RT-26. Tratar SIGTERM e encerramento gradual: a API deixa de aceitar tráfego antes de sair; workers param de buscar mensagens e só confirmam as concluídas. Tarefa interrompida deve voltar à fila de modo seguro. Configurar tempo de invisibilidade, renovação e período de encerramento conforme a carga, sem depender de terminar qualquer OCR ou chamada externa antes do encerramento do container. No piloto, aplicar esses controles às tasks ECS Fargate; pods e seu ciclo de vida aplicam-se somente a uma futura migração Kubernetes. [F14]

RT-27. Requisito exclusivo de evolução futura, fora das entregas e critérios de conclusão do piloto: prever Helm chart com Deployments da API, workers e dispatcher; Services; configuração de entrada HTTPS; ServiceAccounts; ConfigMaps; referências a segredos; requests/limits; probes; e Job exclusivo de migração. Readiness controla admissão de tráfego; liveness detecta travamento local e não deve provocar reinícios em massa em razão exclusiva da indisponibilidade de um fornecedor externo. Migrações não serão executadas por cada réplica ao iniciar.

RT-28. No piloto ECS Fargate, cada serviço usa task roles IAM próprias. Somente em uma futura migração para EKS, cada workload usará identidade IAM por ServiceAccount, com EKS Pod Identity quando compatível ou IRSA quando necessário. Não distribuir chaves AWS estáticas. Os requisitos de RBAC, acesso ao cluster, políticas de rede Kubernetes e privilégios de pods aplicam-se apenas à eventual fase EKS, não ao piloto. [F13]

RT-29. No piloto, usar mecanismos de escalabilidade do ECS para a API por carga e para workers por backlog/idade das mensagens, com métricas CloudWatch adequadas ao serviço. KEDA para SQS será avaliado somente se houver migração futura para EKS. Definir máximo de réplicas, conexões ao banco, concorrência de LLM e orçamento. O aumento de workers deve respeitar os limites dos fornecedores e preservar a prevenção de envios duplicados. O worker GenLayer coordena nonce por carteira de forma externa e transacional. [F13]

### 18B Filas de mensagens

RT-17. Adotar Amazon SQS com fila de falhas própria por classe de trabalho: documents, notifications e committee. Separar códigos de autenticação das notificações comuns para evitar atraso atrás de grandes lotes. O dispatcher lê eventos da outbox PostgreSQL e publica nas filas; o consumidor reconhece a mensagem somente após registrar o efeito durável. Duplicatas são esperadas e tratadas por chave de idempotência. [F6]

Proposta de envelope: event_id, event_type, schema_version, job_id, case_id, artifact_id, artifact_version, correlation_id e occurred_at. Mensagens carregam referências, nunca documentos completos, números de identificação, senhas, códigos OTP em claro ou URLs assinadas. Segredos temporários necessários ao envio serão obtidos pelo worker em armazenamento controlado e eliminados após uso.

RT-30. Usar SQS Standard como padrão; adotar FIFO apenas se um fluxo tiver necessidade demonstrada de ordenação por grupo. Mesmo com FIFO, efeitos externos continuam idempotentes. O banco valida revisão/estado para eventos atrasados. Configurar long polling, invisibilidade, renovação, tentativas limitadas, fila de falhas, alarmes e reprocessamento auditado. Reprocessar não pode reativar um arquivo excluído ou um caso cancelado.

### 18C Rede, segurança e hospedagem

RT-16. PostgreSQL, DynamoDB e S3 não permitem acesso externo direto aos dados. O RDS PostgreSQL terá acesso público desabilitado, sub-redes privadas e security groups limitados aos serviços internos autorizados. DynamoDB e S3 serão acessados por endpoints VPC e papéis IAM próprios da plataforma; suas políticas de recurso devem negar operações de dados fora dos endpoints autorizados, inclusive quando uma credencial de aplicação válida for usada pela internet. Os serviços gerenciados não são bancos instalados dentro dos pods ou das sub-redes: a restrição resulta da combinação de rota privada, políticas de endpoint, IAM e políticas de recurso. Criar apenas um endpoint VPC não elimina outros caminhos de acesso; o bloqueio deve estar nas políticas e ser verificado. [F20, F21]

Somente os pontos de entrada HTTPS da aplicação e das APIs serão expostos. Para consulta pública de processos, disponibilizar exclusivamente GET /public/v1/cases/{snapshot_uuid}.json, conforme RF-16. A API devolve o JSON saneado aprovado; nenhuma rota expõe dados brutos de tabelas ou acesso genérico ao S3. Endpoints de upload, documentos originais e acordos permanecem autenticados. GenLayer e demais consumidores públicos chamam a API, nunca o armazenamento. O acesso autorizado a provedores externos de IA ou assinatura ocorre pelo backend, que transmite o conteúdo necessário conforme as políticas próprias, sem conceder acesso ao S3.

Serviços, futuras instâncias/pods, jobs operacionais e executores de implantação usam redes e identidades controladas. Manutenção de políticas deve preservar a capacidade administrativa de recuperação sem criar exceção de leitura ou gravação de dados pela internet. Rotinas internas de backup e restauração recebem permissões específicas e são validadas com as restrições em vigor. Planejar saída para OpenRouter, GREEN-API e RPC por rota controlada, contabilizando NAT e transferência; não abrir bancos ou buckets para viabilizar essas integrações.

O destino do frontend será AWS: arquivos estáticos empacotados na imagem de um serviço web, com CloudFront apontando para a origem HTTP controlada da aplicação, domínio próprio e certificados ACM. Não usar bucket S3 como origem diretamente acessada pela distribuição, nem habilitar website público em S3. Essa proposta mantém toda a comunicação com S3 restrita aos serviços internos. A landing page na Netlify permanece até a migração. Frontend e API podem compartilhar a origem com comportamentos separados de roteamento e cache; encaminhar /api e /public/v1 ao backend. Cache de arquivos estáticos não se aplica a documentos privados nem ao endpoint público de snapshots no piloto. Snapshots seguem o controle de publicação e retirada da seção 8.

### 18D Terraform desde a fundação

RT-31. O provisionamento AWS será uma entrega obrigatória da primeira fase técnica. O artefato será um projeto Terraform declarativo e modular, acompanhado de comandos de operação e documentação, e não um único script imperativo. Esta especificação define seu escopo; a implementação dos arquivos .tf e o provisionamento são entregas posteriores.

| Diretório planejado | Recursos ou responsabilidade | Independência |
| --- | --- | --- |
| infra/terraform/bootstrap | Bucket de estado, chave KMS e acesso inicial | Estado separado da aplicação |
| infra/terraform/modules/network | VPC, sub-redes, rotas, endpoints privados e security groups | Acesso aos dados restrito à rede interna, independente do runtime |
| infra/terraform/modules/data | RDS privado, DynamoDB/S3 com políticas por endpoint e backup | Sem acesso externo aos dados; preservado na migração ao EKS |
| infra/terraform/modules/messaging | SQS, filas de falhas, políticas e alarmes | Consumidores intercambiáveis |
| infra/terraform/modules/security | IAM, KMS e referências de segredos | Papéis por workload |
| infra/terraform/modules/observability | Logs, métricas, alertas e orçamento | Identificação por ambiente |
| infra/terraform/modules/frontend | CloudFront com origem HTTP da aplicação, DNS e TLS | Sem origem S3 direta; arquivos estáticos no serviço web |
| infra/terraform/modules/registry | Repositórios ECR e política de imagens | Compartilhado pelos runtimes |
| infra/terraform/modules/runtime_ecs | Serviços ECS Fargate, tarefas e balanceador | Runtime do piloto |
| infra/terraform/modules/runtime_eks | Planejamento de EKS, capacidade e identidades | Futuro; não implementar ou provisionar no piloto |
| infra/terraform/environments | Configuração e estados de dev, staging e prod | Sem credenciais no Git |
| deploy/helm/mediare | Recursos da aplicação Kubernetes | Futuro; não compõe a entrega do piloto |

RT-32. Manter estados separados para bootstrap, recursos persistentes e runtime, por ambiente/conta. O backend remoto usa S3 cifrado, versionamento, acesso mínimo e bloqueio nativo com use_lockfile. O mecanismo atual de locking em tabela DynamoDB está depreciado no backend S3 do Terraform; a tabela de JSON da aplicação não será utilizada como mecanismo de bloqueio do estado Terraform. Preparar o bucket de estado antes de migrar o estado de bootstrap. [F15] O bucket de estado também obedece ao acesso interno: operações Terraform com acesso ao estado usam executor autorizado com conectividade ao endpoint VPC. O bootstrap deve preparar esse caminho antes de impor a restrição definitiva; não depender de um runner público para acessar o estado protegido.

RT-33. Variáveis incluem região, CIDRs, domínios, ambiente, tags, capacidade, retenção, orçamento, réplicas e modo de pagamento. Fixar versões de providers e módulos. CI usa credenciais temporárias por OIDC, executa fmt, validate e verificações de política, e apresenta plan revisável. Aplicar o plano exato aprovado; mudanças destrutivas em produção exigem revisão explícita. Marcar valores como sensitive não impede que apareçam no estado: restringir o estado e evitar gravar valores de segredos nele. Quando o pipeline precisar acessar estado S3 ou dados internos, o executor roda na rede autorizada. OIDC identifica o executor, mas não substitui o controle de origem de rede. O plano valida endpoints, políticas de recurso e ausência de caminhos alternativos pela internet.

RT-34. Recursos persistentes de produção exigem proteção de exclusão quando disponível, guardas de plano e procedimento de recuperação; prevent_destroy é uma proteção adicional, não substitui backup ou revisão. Não usar force_destroy para buckets de documentos de produção. Terraform cria infraestrutura e configura referências de segredo; migrações de banco e releases de aplicação pertencem ao pipeline de deploy. Não colocar dependência circular entre criação do EKS e instalação de workloads no mesmo passo.

### 18E Implantação, observabilidade e migração

RT-18. CI executa testes de domínio, integração PostgreSQL/DynamoDB/SQS e testes de contrato. Publicar imagens imutáveis no ECR, aplicar migrações compatíveis em job único, verificar saúde e permitir rollback da aplicação. Deploy de frontend, API e workers tem versões rastreáveis. Dados e segredos de produção não são disponibilizados para previews.

RT-19. CloudWatch e instrumentação de aplicação registram latência, erros, idade da fila, tentativas, falhas de OCR/IA, tokens, custo, conexões PostgreSQL, throttling DynamoDB e tempo de consenso. Usar correlation_id entre API, fila, worker e transação. Alertas têm responsável e procedimento de resposta; logs excluem conteúdo sigiloso.

RT-35. Aplicável somente a uma futura migração, fora do piloto. Antes da migração para EKS, instalar e testar workloads em homologação, validar identidades e acesso aos mesmos contratos de dados, ensaiar interrupções e medir custos. No corte, drenar o runtime anterior e transferir consumidores gradualmente. Evitar dois schedulers ou escritores de carteira sem coordenação; deduplicação continua obrigatória. Alterar roteamento somente após smoke tests e preservar plano de retorno. A restauração deve recuperar referências coerentes entre PostgreSQL, S3 e DynamoDB, não apenas iniciar um novo cluster.

## 19 Modelo conceitual de dados

IDs principais serão UUIDv7 gerados no backend. Campos monetários usam centavos; datas operacionais usam UTC. Dados pessoais que exigem busca exata poderão usar índice HMAC separado do valor cifrado. Hash simples de identificador de baixa entropia não é proteção adequada contra enumeração.

| Entidade | Conteúdo principal | Relação ou invariável |
| --- | --- | --- |
| User e AuthIdentity | E-mail, hash local, vínculo Google, situação | Um usuário pode ter credenciais vinculadas |
| Profile e KYCVerification | Nome, documento, endereço, telefone e revisões | Histórico preservado; acesso restrito |
| Session e OTPChallenge | Sessões, fator, expiração e tentativas | Código de uso único |
| RoleInvitation e RoleGrant | Convite, papel, emissor e aceite | Concessão somente após habilitação |
| Company e CompanyRevision | Nome fantasia, razão social, CNPJ, endereço e versões | Identidade empresarial separada da conta e do KYC pessoal |
| CompanyRepresentation | Empresa, usuário, estado, escopo e registro de poderes | Vínculo explícito; CNPJ ou e-mail não concedem acesso |
| MediationCase e CaseParty | ID, papéis, etapa, tipo PF/PJ, pessoa ou empresa e revisão | Duas partes; cada parte aponta exclusivamente para pessoa ou empresa |
| CaseRepresentation | Parte empresarial, representante responsável, vínculo e histórico | Ator autenticado distinto da empresa que é parte |
| CaseInvitation e Acceptance | Destinatário, token, versão, parte PF/PJ, ator e aceite | Aceite vinculado às condições, empresa e representação exibidas |
| SubmissionRevision | Carta estruturada e vínculo às provas | Imutável depois de congelada |
| Document e DocumentVersion | Tipo, objeto S3, versionId, hash e dono | Original não sobrescrito |
| ProcessingJob e DocumentDerivative | Pipeline, estado, JSON e referências | Derivado ligado à origem e à versão |
| AnalysisSnapshot e PublicationReview | Manifesto, hash, UUID público, modo de aprovação, versão da política e revisor quando houver | Liberação rastreável da versão exata; bytes públicos imutáveis |
| PublicationPolicy e PolicyRevision | Exigência de revisão humana, ambiente, versão, autor, data e motivo | Valor inicial ligado no piloto; política vigente verificada na publicação |
| FeeQuote e PaymentObligation | Tabela, rateio, cota e moeda | Soma das cotas igual ao total |
| PaymentAttempt e ProviderEvent | Checkout, eventos e estornos | ID do evento único por provedor |
| CommitteeRun | Snapshot, contrato, transação e resultado | Uma execução lógica por chave |
| MediatorAssignment | Elegíveis, sorteio e substituições | Apenas atribuição ativa dá acesso |
| AgreementVersion | Conteúdo, autor, v1 e revisões | Versões nunca sobrescritas |
| SchedulingRound e SlotSelection | Cinco opções e seleção de três a cinco opções distintas por parte | Seleções da mesma rodada; remarcação com multa como fluxo alternativo |
| MediationSession e MeetingLinkRevision | Horário confirmado, serviço externo, URL, instruções, versão, autor e data | Link pode ser pendente ao agendar; disponível no início; revalidado após remarcação |
| RescheduleRequest | Parte, contador, justificativa e cobrança | Incremento após pagamento confirmado |
| SignatureEnvelope e Signature | Revisão final, parte, signatário humano, representação e evidências | Mesmo conteúdo aceito por todos; assinatura vinculada à empresa quando aplicável |
| Notification e DeliveryAttempt | Canal, destinatário e status | Envio separado de confirmação de entrega |
| AuditEvent e OutboxEvent | Ação, recurso e evento a publicar | Auditoria protegida e entrega recuperável |

No PostgreSQL, exigir chaves estrangeiras, unicidade por caso/parte e versão, restrições de percentuais e valores não negativos. O acesso a objetos S3 depende do vínculo e autorização no banco transacional. A propriedade e a autorização de acesso não podem ser determinadas pelo nome do arquivo. O catálogo acima é conceitual: metadados e estados ficam no PostgreSQL; os payloads documentais seguem a separação abaixo. O CNPJ normalizado terá unicidade cadastral. CaseParty referencia exatamente uma identidade de parte, pessoa física ou empresa; CaseRepresentation vincula a parte empresarial ao usuário autorizado. Registros de ação preservam actor_user_id e a parte em cujo nome a ação ocorreu, com company_id e representation_id quando aplicáveis.

### 19A Distribuição dos dados

| Armazenamento | Dados e papel | Padrão de acesso |
| --- | --- | --- |
| RDS PostgreSQL | Fonte de verdade de identidade, autorização, estado, financeiro e vínculos | Transações, relações e consultas operacionais |
| DynamoDB | Projeção consultável dos JSONs imutáveis e metadados de artefatos | GetItem por UUID/versão e Query por partição |
| S3 privado | Originais, PDFs e bytes canônicos de todos os JSONs preservados | Leitura por chave e versão exatas |

RT-36. Adotar DynamoDB como componente proposto para o repositório consultável de JSON, sem substituir PostgreSQL por mera expectativa de velocidade. PostgreSQL JSONB também atende documentos estruturados; DynamoDB se justifica por acessos previsíveis por chave e escala independente. A equipe deve medir latência p95/p99 e custo por leitura/escrita com o tamanho real dos artefatos. Não prever Scan em rotas de atendimento ao usuário.

Modelo inicial da tabela artifacts: PK = ARTIFACT#{uuid}, SK = VERSION#{versao}, schema_version, content_hash, payload quando couber, s3_key, s3_version_id, byte_size e created_at. UUIDs não contêm identidade pessoal. A lista de artefatos de um caso vem do PostgreSQL; criar índices adicionais somente para consultas identificadas. O cliente do navegador nunca acessa a tabela diretamente.

DynamoDB limita cada item a 400 KB, incluindo nomes e valores dos atributos. Proposta: aceitar payload inline somente quando o tamanho estimado do item for inferior a 300 KB; acima disso, guardar ponteiro para S3. Não fragmentar um processo em itens arbitrários apenas para contornar o limite. O S3 preserva os bytes canônicos mesmo quando há projeção inline, permitindo verificar integridade e reconstruí-la. [F11]

RT-37. A representação canônica no S3 é a autoridade do conteúdo imutável; DynamoDB é sua projeção de consulta. Guardar hash e versão exatos em ambos. Quando a publicação exige bytes idênticos para o IC, servi-los do objeto canônico, sem reconstruí-los a partir de mapas DynamoDB. Tipos numéricos não podem alterar centavos, precisão ou hashes na conversão.

### 19B Consistência e recuperação

RT-38. Não existe uma transação única de aplicação abrangendo PostgreSQL, S3 e DynamoDB. O worker grava artefato imutável e projeção idempotente, verifica sua disponibilidade e só então ativa a referência no PostgreSQL junto com o evento de conclusão. Falha intermediária deixa o job pendente e recuperável. Um reconciliador identifica projeções ausentes, divergências de hash e objetos órfãos, respeitando prazo de segurança antes de descartar.

RT-39. Permissões, aprovação de publicação e retirada continuam sob controle transacional no PostgreSQL. Uma cópia antiga de status em DynamoDB nunca autoriza divulgação. No piloto, o endpoint público consulta a liberação corrente e não aplica cache compartilhado que possa servir artefato retirado. Se a autorização estiver indisponível, negar o acesso. Otimização posterior precisa preservar a política de revogação.

Leituras DynamoDB imediatamente dependentes de uma escrita usam ConsistentRead na tabela base quando necessário; consultas por GSI não devem ser usadas como garantia de atualização imediata. Escritas condicionais impedem sobrescrever uma versão existente com outro hash. TTL é coleta posterior, não prazo exato de eliminação nem mecanismo de revogação: a aplicação verifica a expiração no momento do acesso. [F12]

RT-40. Prever DynamoDB on-demand como capacidade inicial, PITR para dados que precisem de recuperação e alarmes de throttling/custo. O restore de PostgreSQL deve apontar para versões S3 preservadas; projeções DynamoDB podem ser reconstruídas dos objetos canônicos e referências válidas. Ensaiar restauração consistente e impedir que conteúdo retirado reapareça publicamente após um restore. Retenção e recuperação obedecem à mesma política nos três armazenamentos.

## 20 Contratos de API propostos

Prefixo privado /api/v1. Endpoints abaixo são um contrato inicial de escopo, a detalhar em OpenAPI antes da implementação. Retornos assíncronos usam 202 com job_id; criação usa 201; conflitos de revisão usam 409; acesso negado usa 403 ou 404 conforme política contra enumeração. Erros incluem código estável, mensagem e correlation_id. Criação e adesão de casos aceitam party_type e company_id quando aplicável; actor_user_id é obtido da sessão, nunca confiado ao corpo da requisição. O backend resolve e valida o vínculo antes de registrar qualquer ação em nome da empresa.

| Grupo | Operações principais | Controle específico |
| --- | --- | --- |
| Auth | POST /auth/register, /login, /google, /logout | Rate limit e validação do provedor |
| Recuperação e fator | POST /auth/password-reset, /auth/mfa/challenges, /auth/mfa/verify | Uso único e sessão limitada |
| Perfil e KYC | GET/PATCH /me; POST /kyc/documents, /kyc/submit, /me/phone/verify | Conta pessoal e KYC exclusivo da pessoa física |
| Empresas | POST /companies; GET/PATCH /companies/{id}; GET /me/companies | Campos empresariais, revisão, vínculo ativo e CNPJ único |
| Representação | POST /companies/{id}/representation-requests; GET /cases/{id}/representations; POST /cases/{id}/representative-changes | Concessão controlada, poderes registrados, KYC pessoal e auditoria |
| Casos | POST /cases; GET /cases/{id}; PATCH /cases/{id}/draft | Papel, vínculo e revisão |
| Convites | POST /cases/{id}/invitations; POST /invitations/{token}/accept | Token não é acesso aos documentos |
| Manifestações | POST /cases/{id}/submissions e /imports | Autoria e sanitização |
| Documentos | POST /uploads/intents; PUT /uploads/{id}/content; POST /uploads/{id}/complete | Bytes enviados à API autenticada; backend valida checksum/versão e acessa S3 internamente |
| Provas | DELETE /cases/{id}/documents/{doc}; GET /documents/{id}/content | Editabilidade e streaming privado |
| Congelamento | POST /cases/{id}/freeze | Revisão esperada e transação |
| Pagamentos | GET /cases/{id}/payments; POST /payments/{id}/checkout | Somente a cota do pagador |
| Progresso | GET /jobs/{id}; GET /cases/{id}/timeline | Somente dados visíveis ao papel |
| Mediador | GET /mediator/cases; POST /cases/{id}/agreement-versions | Atribuição e liberação |
| Agenda | POST /cases/{id}/rounds, /rounds/{id}/selections | Cinco opções; confirmação exige seleção de três a cinco opções distintas |
| Videoconferência | GET /cases/{id}/session; PATCH /cases/{id}/session/meeting-link | Leitura pelos participantes autorizados; edição pelo mediador atribuído, com revisão e auditoria |
| Remarcação | POST /cases/{id}/reschedules | Rodada, contador e pagamento |
| Assinatura | POST /cases/{id}/signature-envelopes | Versão final congelada |
| Administração | POST /admin/invitations; POST /admin/cases/{id}/reassign | Papel, motivo e auditoria |
| Política de publicação | GET/PATCH /admin/publication-policy | Administrador, reautenticação, motivo, revisão esperada e auditoria |
| Webhooks | POST /webhooks/{provider} | Autenticação e deduplicação |
| Público | GET /public/v1/cases/{snapshot_uuid}.json | Sem login; JSON canônico saneado e publicado no corpo da resposta, sem redirecionamento ao armazenamento |

Webhooks não dependem da sessão de navegador. Verificar assinatura criptográfica quando o fornecedor a oferecer, timestamp e replay; caso contrário, combinar credencial de callback e reconciliação autenticada conforme capacidade real do serviço. Nunca aceitar um evento financeiro ou de assinatura apenas por conter o ID correto.

## 21 Segurança, privacidade e requisitos operacionais

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

As metas apresentadas são premissas iniciais de dimensionamento, sujeitas à validação de capacidade e operação. Para operação comercial com maior exigência, propor 99,9%, RPO de quinze minutos e RTO de quatro horas, com PITR, redundância e ensaio de recuperação antes de assumir o compromisso. Tempo de OCR, IA e consenso será medido; não prometer conclusão em minutos para todo caso.

## 22 Requisitos de validação jurídica

O sistema deve apresentar IA e mediador como apoio à composição consensual, sem atribuir a eles poder de impor um acordo. A Lei de Mediação preserva voluntariedade e confidencialidade; a escolha/aceitação do mediador, impedimentos e assistência por advogado afetam o fluxo. Se uma parte comparecer assistida, a situação da outra deve ser tratada conforme a regra legal aplicável. [F1]

O convite do produto precisa ser compatibilizado com os elementos e prazos dos arts. 21 e 22, incluindo escopo, primeira reunião e efeitos da ausência de resposta. O convite preliminar digital e o convite formal podem ser etapas distintas, mas essa distinção exige definição jurídica. Não anunciar que o fluxo atual já satisfaz esses dispositivos. [F1]

Pessoas físicas e empresas estão incluídas na primeira entrega por decisão de produto. A empresa possui cadastro próprio e é parte no procedimento; somente seu representante realiza KYC. A conferência de poderes para atuar e assinar é uma verificação de representação separada, cujo procedimento e evidências serão definidos em D-18; ela não corresponde a KYC empresarial. Menores, incapazes, matérias especiais e direitos que exigem homologação precisam de triagem e encaminhamento próprios. A elegibilidade não deve ser decidida autonomamente por uma LLM.

Antes de produção, validar o regulamento de mediação, tratamento das provas compartilhadas, publicação/transferência a terceiros, retenção, honorários, remarcações, reembolsos e assinatura. Essas são dependências da definição do serviço, não afirmações de que qualquer configuração técnica assegura conformidade.

## 23 Critérios de aceite e homologação

| ID | Cenário | Resultado esperado |
| --- | --- | --- |
| CA-03 | Cadastro local e Google | Contas vinculadas corretamente; nenhum segredo em claro |
| CA-04 | KYC incompleto ou código errado | Abertura/instrução bloqueada; erro recuperável |
| CA-05 | Login de conta habilitada | APIs privadas bloqueadas até segundo fator válido |
| CA-06 | Troca de telefone | Novo número só usado após verificação |
| CA-07 | Upload múltiplo com uma falha | Itens válidos preservados e retry individual |
| CA-08 | PDF malicioso ou tentativa de reutilizar intenção de upload concluída | Sem execução; API não sobrescreve original conferido e não emite URL S3 |
| CA-09 | Dado identificável em resumo | Publicação bloqueada e revisão solicitada |
| CA-10 | Convite aberto por pessoa errada | Sem acesso a provas e sem vínculo automático |
| CA-11 | Pedido alterado após aceite | Nova revisão exige reconfirmação |
| CA-12 | Edição concorrente ao congelamento | Uma revisão consistente; conflito explícito |
| CA-13 | Disputa de R$50 mil e rateio 70/30 | Total R$1.500; cotas R$1.050 e R$450 |
| CA-14 | Rateio 100/0 | Uma obrigação simulada na V1; análise liberada após confirmação |
| CA-15 | Webhook duplicado ou fora de ordem | Ausência de crédito duplicado e de análise repetida |
| CA-16 | Reinício após envio on-chain | Recupera a transação e o snapshot corretos |
| CA-17 | Falta de consenso ou retorno inválido | Suspensão explicada; sem termo aprovado fictício |
| CA-18 | Mediador salva duas edições | v1 preservada e versões posteriores recuperáveis |
| CA-19 | Cada parte confirma três, quatro ou cinco opções entre as mesmas cinco | Seleções aceitas e interseção calculada corretamente; ao menos uma opção comum |
| CA-20 | Segunda remarcação paga da mesma parte | Multa de R$198; contador da outra parte não muda; pagamento simulado na V1 |
| CA-21 | Alteração durante assinaturas | Envelope anterior invalidado; novos aceites |
| CA-22 | Três assinaturas completas | PDF final privado e evidências disponíveis |
| CA-23 | Acesso cruzado entre casos | API, arquivo e listagens recusam a exposição |
| CA-24 | Perda simulada do banco | Restauração recupera vínculos, versões e pagamentos |
| CA-25 | PIX/cartão na V1 | Aviso de simulação e ausência de dados financeiros reais |
| CA-26 | Aprovação, recusa e expiração simuladas | Backend preserva estados e idempotência |
| CA-27 | Evento simulado em caso live | Nenhuma liquidação nem liberação do caso |
| CA-28 | Worker interrompido durante OCR/IA | Nova tentativa sem perda nem efeito duplicado |
| CA-29 | Duas réplicas recebem o mesmo evento | Uma conclusão lógica e vínculos coerentes |
| CA-30 | JSON acima do limite inline | Payload no S3, referência e hash íntegros |
| CA-31 | Falha entre S3, DynamoDB e PostgreSQL | Sem liberação prematura; retomada consistente |
| CA-32 | Projeção antiga após retirada | Endpoint público nega acesso |
| CA-33 | Terraform em homologação | Plan revisado, implantação reproduzível e segundo plan sem drift esperado |
| CA-34 | Futuro — API e workers em Kubernetes | Probes, encerramento, IAM e processamento validados antes da migração; não bloqueia o piloto |
| CA-35 | Futuro — troca ECS para EKS | Mesmos dados preservados, sem recriar RDS, tabelas ou buckets; não integra a homologação do piloto |
| CA-36 | Seleção de Empresa no cadastro | Formulário adicional com nome fantasia, razão social, CNPJ e endereço; dados pessoais preservados |
| CA-37 | Representante com KYC pendente e empresa cadastrada | Atuação no caso bloqueada até habilitação pessoal; nenhuma etapa de KYC exigida da empresa |
| CA-38 | Convite e comunicações de uma parte empresarial | Empresa identificada como parte; envio ao canal autorizado e ator humano registrado |
| CA-39 | Acordo entre pessoa física e empresa, ou entre duas empresas | Dados empresariais no termo e assinatura pessoal do representante em nome da empresa |
| CA-40 | Usuário informa CNPJ já cadastrado sem vínculo | Não obtém acesso a cadastro privado, documentos ou casos; vinculação segue fluxo controlado |
| CA-41 | Atualização empresarial ou substituição de representante | Histórico preservado, autorização reavaliada e envelope pendente substituído quando necessário |
| CA-42 | Publicação de snapshot com parte empresarial | Razão social, nome fantasia, CNPJ e referências identificáveis do representante não aparecem no JSON liberado |
| CA-43 | PDF com texto e página ou evidência visual sem texto | Rota por página identifica a lacuna; evidência não é descartada e cobertura é verificada |
| CA-44 | Falta de rota externa autorizada ou falha de IA | Job pendente/recuperável; sem envio alternativo indevido e sem resumo aprovado fictício |
| CA-45 | Resposta JSON válida com valor incorreto ou trecho sem fonte | Validação factual aponta divergência e impede liberação até resolução |
| CA-46 | Documento extenso com resposta truncada ou página ausente | Incompletude detectada; retomada por unidade e consolidação somente com cobertura confirmada |
| CA-47 | Piloto com configuração inicial ou exigência religada | Publicação nova bloqueada até revisão humana válida da versão; política indisponível também bloqueia |
| CA-48 | Administrador desliga a exigência de revisão humana | Itens podem ser liberados após validações; decisão registra modo automático, política e alteração auditada |
| CA-49 | Política muda enquanto worker prepara a publicação | Backend revalida a política atual; trabalhos pendentes seguem a nova regra e histórico publicado é preservado |
| CA-50 | Usuário não administrador tenta mudar a política | Requisição negada; flag enviada pelo cliente não altera a exigência aplicada no servidor |
| CA-51 | Parte tenta confirmar zero, uma ou duas opções, ou opções inválidas/repetidas | Confirmação recusada no servidor; permanece disponível solicitar remarcação com multa e justificativa |
| CA-52 | Parte solicita remarcação em vez de selecionar pelo menos três horários | Multa exibida; nova rodada somente após confirmação do pagamento, sem incrementar contador em tentativa falha |
| CA-53 | Horário confirmado antes do cadastro do link | Agendamento preservado; partes veem link pendente e recebem aviso quando o mediador o informar |
| CA-54 | Mediador cadastra ou altera link de Zoom, Meet, Teams ou equivalente | URL vigente disponível na área autenticada; participantes notificados; horário e multa inalterados |
| CA-55 | Outro usuário tenta alterar ou acessar link sem vínculo | Acesso negado; edição restrita ao mediador atribuído; link ausente de artefatos públicos |
| CA-56 | Sessão remarcada com link de uma rodada anterior | Link requer confirmação ou substituição pelo mediador antes de ser apresentado como vigente |
| CA-57 | Tentativa externa de acesso a PostgreSQL, DynamoDB ou S3 | Conexão/operação de dados negada; testar DynamoDB/S3 também com credencial de aplicação fora do endpoint autorizado |
| CA-58 | Consulta pública com UUID publicado | API retorna 200, application/json e bytes canônicos; nenhum redirecionamento ou endereço do armazenamento |
| CA-59 | Consulta com UUID desconhecido, privado ou retirado | API retorna 404 sem conteúdo privado; nenhuma listagem pública |
| CA-60 | Upload e download pelo navegador | Transferência exclusivamente por API autenticada; nenhum acesso direto ao S3 ou credencial AWS entregue ao cliente |
| CA-61 | Implantação da infraestrutura do piloto | Serviços em ECS Fargate; plano Terraform e inventário sem cluster EKS/Kubernetes, Helm ou KEDA |

A homologação combina testes automatizados de domínio, contrato e integração com testes manuais de identidade, documentos, acessibilidade, assinatura e revisão por mediador. Usar casos sintéticos nas integrações de teste e verificar que a análise local não seja rotulada como consenso GenLayer.

## 24 Plano de implementação e custos

Recomenda-se implementar um fluxo completo com dados sintéticos antes de ampliar o volume de operação. Cada fase abaixo produz uma entrega verificável, e não apenas componentes isolados.

| Fase | Entrega | Condição de conclusão |
| --- | --- | --- |
| 0 Decisões e contratos | Escopo do piloto, políticas e prova de integração | Resolver publicação, KYC, assinatura e interface do IC |
| 1 Fundação | Repositório, Terraform AWS, CI, containers, API, KYC pessoal e cadastro empresarial | Infraestrutura reproduzível, usuário habilitado e representação isolada por empresa/caso |
| 2 Instrução | Upload, extração local, integração documental OpenRouter, carta, convite e revisões | Caso das duas partes congelado de forma consistente |
| 3 Simulação e comitê | Cotas, simulador PIX/cartão, snapshot e worker GenLayer | Confirmação simulada libera resultado recuperável |
| 4 Mediação humana | Convites de mediadores, termo, agenda e cadastro de link externo de vídeo | Sessão agendada, link inserido pelo mediador e remarcação rastreável |
| 5 Formalização | Assinaturas, PDF, encerramento e auditoria | Três signatários e recuperação dos artefatos |
| 6 Piloto assistido | V1 com revisão humana de publicação ligada por padrão e sem cobrança real | Métricas, restore e incidentes validados |
| Etapa 2 Cobrança real | PSP, webhooks, reconciliação e estornos reais | Homologação financeira e políticas aprovadas |

A fase de fundação do piloto inclui bootstrap de estado, módulos Terraform persistentes e runtime ECS Fargate. Os arquivos .tf serão desenvolvidos no repositório do website. Helm, módulos EKS e ensaios Kubernetes ficam fora dessa entrega. Containers OCI, configuração externa, dados persistentes fora do runtime e adaptadores modulares preservam a possibilidade de migração; isso não equivale a declarar a aplicação já homologada em Kubernetes. A implementação e os testes EKS pertencem a uma fase futura independente, também separada da cobrança real.

O backend e o frontend podem avançar em paralelo com base em OpenAPI e simuladores, sem acoplar o cronograma à otimização contínua do IC. A integração real e os testes de contrato continuam obrigatórios antes do piloto.

Mesmo sem cobrar as partes na V1, a plataforma pode ter custos reais de infraestrutura e fornecedores. O custo mensal deve ser calculado por: infraestrutura fixa + armazenamento e transferência + OCR/LLM + execução GenLayer + mensagens + pagamento + assinaturas + vídeo + trabalho operacional. Custo por caso deve separar documentos, tokens por etapa, tentativas, chamadas on-chain, número de mensagens e revisões humanas. Honorários recebidos não são margem líquida.

Esta especificação não estabelece uma estimativa financeira definitiva. Volume, tamanho dos arquivos, retenção, região, fornecedores, nível de disponibilidade e equipe ainda precisam ser definidos. Antes de contratar, medir um lote sintético representativo, consultar preços vigentes e estabelecer teto de gasto por caso e por mês, com alerta e interrupção controlada. Não executar chamadas pagas de benchmark sem orçamento autorizado.

## 25 Registro de decisões e dependências

| ID | Decisão necessária | Responsável sugerido | Marco |
| --- | --- | --- | --- |
| D-01 | Resolvida: pessoas físicas e empresas na V1; conta e KYC do representante, empresa nas comunicações e no acordo | Produto — confirmado pelo responsável | Incorporada na revisão 1.3 |
| D-02 | Garantia do KYC, revisão e eventual prova de vida | Produto e segurança | Antes de habilitar usuários reais |
| D-03 | Publicação do JSON, confidencialidade e transferências | Produto e jurídico | Antes de enviar casos reais à rede |
| D-04 | PSP, parcelamento, reembolsos e fiscal | Financeiro e produto | Etapa 2 antes da cobrança real |
| D-05 | Provedor/modalidade de assinatura e evidências | Jurídico e engenharia | Antes do acordo final |
| D-06 | Rede, contrato multi-caso, versão e custos GenLayer | Engenharia do IC | Antes da integração de produção |
| D-07 | Compartilhamento de provas e complementações | Produto e jurídico | Antes da instrução |
| D-08 | Retenção, eliminação e recuperação de identidade | Jurídico e segurança | Antes de coletar dados reais |
| D-09 | Remarcação, teto, isenções e ausência | Produto e jurídico | Antes do agendamento |
| D-10 | Fornecedores de e-mail, SMS e modalidade GREEN-API | Engenharia e operação | Antes da homologação externa |
| D-11 | Prazos de convite, pagamento, resposta e primeira reunião | Produto e jurídico | Antes dos termos de adesão |
| D-12 | Volume, orçamento, disponibilidade e equipe | Responsável pelo projeto | Antes de contratar infraestrutura |
| D-13 | Idiomas das áreas privadas e das minutas | Produto | Antes do frontend autenticado |
| D-14 | Formatos de arquivo, limites e validação do pipeline | Engenharia e mediadores | Antes do piloto documental |
| D-15 | Resolvida: piloto em ECS Fargate, sem Kubernetes/EKS; eventual migração é futura | Produto e engenharia | Incorporada na revisão 1.8; EKS não bloqueia o piloto |
| D-16 | Padrões de consulta e benchmark DynamoDB/JSONB | Engenharia | Antes do repositório de artefatos |
| D-17 | Contas AWS, região, DNS, retenção e orçamento | Infraestrutura e responsável pelo projeto | Antes do primeiro Terraform apply |
| D-18 | Procedimento e evidências de poderes de representação; representantes adicionais, substituição e eventual assinatura conjunta | Produto, jurídico e engenharia | Antes de habilitar atuação empresarial real; sem KYC da empresa |
| D-19 | Modelos, provedores, parser/OCR e rotas de privacidade do OpenRouter; limiares de qualidade, limites e orçamento do pipeline | Engenharia, produto e segurança | Antes de processar documentos reais; avaliar corpus autorizado |

A decisão confirmada para a V1 é pagamento simulado por PIX ou cartão; cobrança real somente na etapa 2. A regra financeira adotada para a simulação é a do rascunho: R$500 + 2%. A publicação do site deve ser atualizada para refletir essa fórmula e o momento correto da cobrança, junto com linguagem precisa sobre IA, sigilo, mediador e assinatura. A especificação não promove uma nova versão do IC e não altera seus resultados experimentais. Também está confirmada a inclusão de empresas, com KYC somente do representante, identificação empresarial nas comunicações e assinatura do representante em nome da empresa. D-01 está encerrada; D-18 trata apenas da operacionalização dos poderes de representação.

## 26 Histórico da especificação

Versão 1.0: definição funcional e arquitetura inicial; pagamentos simulados por PIX e cartão na V1.

Versão 1.1: AWS e Terraform desde a fundação; requisitos explícitos para API/workers portáveis a Kubernetes; SQS detalhado; proposta DynamoDB para projeções JSON com S3 canônico e PostgreSQL transacional; plano de migração ECS para EKS e critérios de consistência e recuperação. Os requisitos funcionais e a simulação de pagamentos permanecem vigentes.

Versão 1.2: revisão editorial e publicação em HTML com índice navegável, busca por seção, links permanentes para requisitos e apresentação para impressão. Identificadores, regras de negócio e decisões técnicas da versão 1.1 preservados. A revisão não constitui aprovação das decisões ainda pendentes.

Versão 1.3: inclusão confirmada de pessoas jurídicas na V1. Formulário empresarial, KYC exclusivo do representante, identidade da empresa em convites e comunicações, acordo com qualificação empresarial e assinatura do representante. Modelo de dados, autorização, APIs e critérios de aceite atualizados; D-01 resolvida e D-18 registrada para o procedimento de representação.

Versão 1.4: proposta de processamento híbrido desde a V1. Extração simples no worker Python; leitura complexa, resumo e apoio à anonimização via OpenRouter. Rotas autorizadas, cobertura por página, validação factual, limites e critérios de aceite detalhados; seleção dos modelos e do parser registrada em D-19. Configuração administrativa confirmada para ligar ou desligar a revisão humana de publicação, ligada por padrão no piloto, com política versionada e auditoria.

Versão 1.5: inclusão de diagramas do fluxo principal, estados alternativos e retomada na seção 11, mantendo a tabela de transições. RF-40 ajustado para seleção obrigatória de pelo menos três das cinco opções, aceitando três, quatro ou cinco, ou solicitação de remarcação com multa. RF-42, modelo de dados, API e critérios de aceite alinhados à regra. Diagramas incorporados ao HTML para leitura offline e impressão.

Versão 1.6: RF-44 confirmado como videoconferência externa à escolha do mediador. Link pode ser inserido após o agendamento, com acesso autenticado, avisos de inclusão/alteração e confirmação após remarcação. Modelo de dados, API e critérios de aceite atualizados; integração com fornecedor de vídeo deixa de ser requisito da V1.

Versão 1.7: PostgreSQL, DynamoDB e S3 restritos ao acesso interno. Publicação de processos exclusivamente por API pública que recebe UUID e devolve o JSON aprovado. Uploads e downloads passam pelo backend; eliminada a distribuição de URLs S3. Rede, Terraform, hospedagem do frontend, integrações e critérios de aceite alinhados à restrição.

Versão 1.8: diagrama AWS com ícones oficiais coloridos na seção 17. Piloto definido em ECS Fargate, explicitamente sem Kubernetes/EKS, Helm ou KEDA. Requisitos e critérios EKS classificados como evolução futura; D-15 resolvida e CA-61 adicionado.

## 27 Referências

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

F11. AWS. Limites de itens e objetos grandes no DynamoDB. https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Constraints.html e https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-use-s3-too.html

F12. AWS. Consistência de leitura e expiração no DynamoDB. https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html e https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ttl-expired-items.html

F13. AWS. Identidades de workloads EKS e autoscaling por SQS com KEDA. https://docs.aws.amazon.com/eks/latest/userguide/service-accounts.html e https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/event-driven-auto-scaling-with-eks-pod-identity-and-keda.html

F14. Kubernetes. Pod lifecycle. https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/

F15. HashiCorp. Terraform S3 backend e locking. https://developer.hashicorp.com/terraform/language/backend/s3

F16. PyMuPDF. Extração de texto e reconhecimento óptico local. https://pymupdf.readthedocs.io/en/latest/recipes-text.html e https://pymupdf.readthedocs.io/en/latest/recipes-ocr.html

F17. OpenRouter. Entrada de PDFs, mecanismos de parsing, limites e cobrança. https://openrouter.ai/docs/guides/overview/multimodal/pdfs

F18. OpenRouter. Saídas estruturadas e compatibilidade por endpoint. https://openrouter.ai/docs/guides/features/structured-outputs

F19. OpenRouter. Controles de retenção zero. https://openrouter.ai/docs/guides/features/zdr

F20. AWS. Restrição de acesso a buckets S3 por endpoint VPC. https://docs.aws.amazon.com/AmazonS3/latest/userguide/example-bucket-policies-vpc-endpoint.html

F21. AWS. Políticas de recurso DynamoDB, incluindo restrição por endpoint VPC. https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/rbac-examples.html

F22. AWS Architecture Icons. Pacote oficial de ícones de 31/07/2026, obtido pela página oficial. https://aws.amazon.com/architecture/icons/

Referências do projeto: site https://mediarev1.netlify.app/; arquivo index.html fornecido; README.md; ic_v30.py, em especial analyze_case e get_case; studio_cycle.py; docs/TERMO_ACORDO_FORMAL.md. Caminhos relativos de código são relativos ao repositório mediare-dataset. O HTML fornecido está em /Users/cgmello/Documents/Projetos/Mediare/index.html.
