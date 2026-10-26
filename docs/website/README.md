# Especificação do website Mediare

A especificação foi congelada como **2.0** e transferida para o repositório
privado [cgmello/mediare-website](https://github.com/cgmello/mediare-website),
na tag `spec-v2.0`.

- [Baseline 2.0 no novo repositório](https://github.com/cgmello/mediare-website/blob/main/docs/spec/v2.0/SYSTEM_SPECIFICATION_v2_0.md)
- [Plano de implementação](https://github.com/cgmello/mediare-website/blob/main/docs/planning/IMPLEMENTATION_PLAN.md)

Esta pasta preserva as revisões históricas. A última revisão de trabalho aqui
é a **1.10**, de 29 de setembro de 2026; novas implementações e revisões devem
ocorrer em `mediare-website`.

- [Especificação em HTML — histórico 1.10](ESPECIFICACAO_SISTEMA_MEDIARE_v1_10.html)
- [Fonte editorial em Markdown](ESPECIFICACAO_SISTEMA_MEDIARE_v1_10.md)
- [Especificação em Word — revisão técnica 1.1](ESPECIFICACAO_SISTEMA_MEDIARE_v1_1.docx)

A edição 1.10 define três fases de infraestrutura:

1. **Local:** Docker Compose, PostgreSQL e LocalStack para S3, DynamoDB e SQS.
   OpenRouter, Google e consenso GenLayer permanecem reais e externos.
2. **AWS:** ECS Fargate, serviços gerenciados e Terraform; sem Kubernetes.
3. **Kubernetes:** migração futura, com EKS como destino proposto.

A seção 17 inclui o desenho da fase 1, a conexão HTTPS restrita para snapshots
consultados pela GenLayer e o diagrama oficial AWS identificado como fase 2.
Bootstrap, volumes, credenciais, LocalStack e critérios de migração estão na
seção 18. `build_local_architecture.py` gera o novo diagrama.

A edição 1.9 tornou obrigatório o inglês no código, identificadores e estruturas
de dados. Acrescenta um MER com 49 entidades em sete visões, acompanhado de
chaves, cardinalidades, regras de integridade e dicionário na seção 19.
O modelo fonte está em `assets/data-model/model.json`; os diagramas são
gerados por `build_data_model.py` e podem ser ampliados e baixados no HTML.

A edição 1.8 adicionou o diagrama de infraestrutura com ícones coloridos oficiais
da AWS. Na revisão atual, ECS Fargate pertence à **fase 2**; Helm, KEDA
e validação de cluster ficam somente na **fase 3**.

O diagrama pode ser ampliado no HTML. Os SVGs originais e seus checksums estão
em `assets/aws-icons`; a geração usa `build_aws_diagram.py`.

Mantém o acesso a PostgreSQL, DynamoDB e S3 restrito aos serviços internos.
O JSON aprovado do processo é servido por API pública mediante UUID; uploads
e downloads também passam pela API, sem URLs pré-assinadas ou acesso direto
aos armazenamentos. Rede, Terraform e hospedagem foram alinhados à restrição.

Mantém o uso de videoconferência externa à escolha do mediador.
O link pode ser cadastrado depois da confirmação do horário, com aviso às
partes e acesso pela área autenticada. Integração com API de vídeo não é
requisito da V1.

Mantém os diagramas do fluxo principal e dos estados alternativos
na seção 11, mantendo a tabela de transições. Os SVGs são incorporados ao HTML
e regenerados por `build_state_diagrams.py` durante a geração do documento.
No agendamento, cada parte confirma três a cinco opções ou solicita remarcação
com multa; o valor inicial proposto continua R$99 e o pagamento é simulado na V1.

Mantém a proposta de extração textual simples no worker Python e IA via
OpenRouter desde a V1 para leitura complexa, resumo e apoio à anonimização.
Inclui controles de cobertura, qualidade factual, privacidade e custo.
A exigência de revisão humana para publicação pode ser ligada ou desligada
pelo administrador; inicia ligada no piloto e toda mudança é auditada.

Mantém pessoas físicas e empresas na primeira versão do produto.
O representante mantém conta e KYC pessoais; a empresa tem cadastro próprio,
aparece como parte nos convites e comunicações e é qualificada no acordo,
assinado pelo representante em seu nome. A decisão D-01 foi resolvida.

A apresentação HTML mantém índice navegável, busca por seção,
links permanentes para requisitos e layout para impressão. O HTML é autônomo:
abre diretamente no navegador, sem servidor, bibliotecas externas ou fontes
remotas. O botão **Imprimir / PDF** imprime o documento completo, mesmo com uma
busca ativa. Os identificadores anteriores foram preservados, com novos
requisitos de cadastro empresarial e critérios de aceite.

Para regenerar o HTML após editar o Markdown, executar a partir da raiz:

```sh
python3 docs/website/build_spec_html.py
```

AWS e Terraform são entregas da fase 2; a fase 1 usa Compose e LocalStack.
A especificação prevê backend modular e os mesmos contratos de dados e filas
nas três fases. Conta/token/plano LocalStack e credenciais dos provedores
reais são requisitos de configuração; não houve instalação, contratação,
provisionamento ou chamada paga nesta revisão.

Pagamentos continuam simulados por PIX e cartão na primeira versão do produto.
As revisões 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8 e 1.9 foram preservadas para consulta histórica.
