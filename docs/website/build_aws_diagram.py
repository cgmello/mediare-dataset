"""Generate the phase 2 AWS architecture using unmodified official AWS icon assets."""
from pathlib import Path
from html import escape
import base64
import hashlib
import json

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets' / 'aws-icons'


def build():
    manifest = json.loads((ASSETS / 'manifest.json').read_text())
    parts = ['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1640 1470" role="img" aria-labelledby="aws-title aws-desc">
<title id="aws-title">Mediare — infraestrutura AWS da fase 2, com ECS e Fargate, sem Kubernetes</title>
<desc id="aws-desc">Clientes e GenLayer consultam a aplicação pelo CloudFront e Application Load Balancer. Frontend, API e workers executam no ECS Fargate em sub-redes privadas. PostgreSQL fica privado na VPC. S3, DynamoDB e SQS ficam como serviços regionais acessados por endpoints VPC. IAM, KMS, Secrets Manager, ECR e CloudWatch apoiam a operação. Nenhum cliente acessa diretamente os bancos ou o S3.</desc>
<defs><marker id="aws-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#526978"/></marker><marker id="aws-egress" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#b76616"/></marker></defs>
<style>.aws-title{font:700 28px Arial;fill:#172c38}.aws-label{font:600 19px Arial;fill:#233b4b}.aws-text{font:16px Arial;fill:#3f5665}.aws-small{font:14px Arial;fill:#526978}.aws-group{font:700 16px Arial;fill:#355364;letter-spacing:.6px}.aws-flow{stroke:#526978;stroke-width:2;fill:none;marker-end:url(#aws-arrow)}.aws-dash{stroke-dasharray:7 5}.aws-out{stroke:#b76616;stroke-width:2;fill:none;marker-end:url(#aws-egress)}</style>
<rect width="1640" height="1470" fill="#fff"/>
<text x="30" y="40" class="aws-title">Mediare · fase 2 · infraestrutura AWS</text>
<rect x="1180" y="16" width="425" height="38" rx="5" fill="#e7f3ec"/><text x="1392" y="42" text-anchor="middle" class="aws-label">ECS + Fargate · sem Kubernetes</text>
''']

    def text(x,y,value,cls='aws-text',anchor='start'):
        parts.append(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{escape(value)}</text>')

    def box(x,y,w,h,fill='#fff',stroke='#b9c8cf',dash=False):
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}" stroke="{stroke}" stroke-width="1.5"'+(' stroke-dasharray="7 5"' if dash else '')+'/>')

    def icon(key,x,y,size=54):
        item=manifest['icons'][key];data=(ASSETS/item['file']).read_bytes()
        assert hashlib.sha256(data).hexdigest()==item['sha256'], key
        encoded=base64.b64encode(data).decode()
        parts.append(f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="data:image/svg+xml;base64,{encoded}"/>')

    def service(key,x,y,w,title,details,h=105):
        box(x,y,w,h);icon(key,x+15,y+18)
        text(x+83,y+38,title,'aws-label')
        for i,line in enumerate(details):text(x+83,y+64+i*21,line,'aws-small')

    def flow(d,dashed=False,out=False):
        parts.append(f'<path d="{d}" class="{"aws-out" if out else "aws-flow"}{" aws-dash" if dashed else ""}"/>')

    # AWS and regional boundaries. Managed services remain outside the VPC.
    box(300,80,1305,1330,'#fff','#647582')
    text(322,109,'AWS Cloud','aws-group')
    box(330,340,1245,800,'#fcfdff','#839aad')
    text(353,370,'Região proposta: sa-east-1 · São Paulo','aws-group')
    box(350,395,760,715,'#faf8ff','#8c6bb1')
    icon('vpc',365,407,35);text(412,432,'Amazon VPC','aws-group')
    box(375,465,710,155,'#f3f9f0','#83a761')
    text(392,491,'SUB-REDES PÚBLICAS · ENTRADA E SAÍDA CONTROLADAS','aws-group')
    box(375,660,710,235,'#f2f8fc','#6b9fbe')
    text(392,685,'APLICAÇÃO · SUB-REDES PRIVADAS','aws-group')
    icon('ecs',398,699,40);text(450,726,'Amazon ECS','aws-label')
    icon('fargate',789,699,40);text(841,726,'AWS Fargate','aws-label')
    box(375,951,430,133,'#f4f8fc','#6b9fbe')
    text(392,978,'SUB-REDES PRIVADAS · BANCO','aws-group')
    box(838,951,247,133,'#f6f4fa','#a293b9')
    text(1160,430,'SERVIÇOS REGIONAIS','aws-group')
    text(1160,453,'Fora da VPC; acesso privado','aws-small')

    # Public clients and explicit DNS versus HTTPS paths.
    box(30,155,225,95,'#f8fafb');text(142,191,'Partes e mediadores','aws-label','middle');text(142,219,'Navegador HTTPS','aws-text','middle')
    box(30,362,225,123,'#f8fafb');text(142,397,'GenLayer / leitores','aws-label','middle');text(142,425,'API pública por UUID','aws-text','middle');text(142,452,'Somente JSON aprovado','aws-small','middle')
    service('route53',350,137,230,'Route 53',['DNS do domínio'])
    service('cloudfront',650,137,250,'CloudFront',['HTTPS · site e API'])
    service('acm',1140,137,390,'Certificate Manager',['Certificados TLS para entrada','Região conforme o recurso'])
    flow('M 255 172 H 350',True);text(275,156,'DNS','aws-small')
    flow('M 255 225 H 270 V 258 H 615 V 191 H 650');text(417,251,'HTTPS','aws-small')
    flow('M 255 423 H 278 V 280 H 635 V 215 H 650');text(347,300,'GET /public/v1/cases/{snapshot_uuid}.json','aws-small')
    flow('M 1140 189 H 900',True)
    # CloudFront origin is the ALB, not S3.
    flow('M 775 242 V 452 H 365 V 555 H 410');text(795,320,'Origem HTTP da aplicação','aws-small')
    service('alb',410,512,295,'Application LB',['Rotas do site e das APIs'],h=86)
    service('nat',790,512,265,'NAT Gateway',['Saída dos serviços'],h=86)
    icon('igw',948,402,36);text(992,424,'IGW','aws-small')

    # Application services; business modules are not drawn as invented AWS services.
    for x,title,lines in [
        (395,'Frontend',['Arquivos estáticos','Serviço web em container']),
        (625,'API Python',['Django / DRF','JSON público por UUID']),
        (855,'Workers',['Documentos · notificações','Comitê · outbox'])]:
        box(x,762,207,107,'#fff','#98b9cc');text(x+103,793,title,'aws-label','middle')
        for i,line in enumerate(lines):text(x+103,821+i*22,line,'aws-small','middle')
    flow('M 520 598 V 636 H 750 V 746 H 498 V 762')
    flow('M 590 598 V 644 H 728 V 762')
    text(398,654,'/', 'aws-small');text(780,649,'/api · /public/v1','aws-small')

    # Data access: both API and workers use private connectivity.
    icon('rds',402,996,55);text(474,1019,'Amazon RDS · PostgreSQL','aws-label');text(474,1048,'Sem endpoint público','aws-small')
    icon('endpoints',853,993,40);text(903,1004,'Endpoints VPC','aws-label');text(853,1040,'Gateway: S3 / DynamoDB','aws-small');text(853,1064,'Interface: SQS','aws-small')
    flow('M 728 869 V 923 H 780 V 990 H 552 V 1000')
    flow('M 959 869 V 923 H 780')
    flow('M 728 923 H 959 V 988')
    text(384,942,'Dados e estado: acesso interno com IAM / security groups','aws-small')
    service('sqs',1195,495,340,'Amazon SQS',['Documentos · notificações','Comitê · filas de falhas'],h=112)
    service('dynamodb',1195,728,340,'Amazon DynamoDB',['Projeção dos JSONs','Política por endpoint + IAM'],h=112)
    service('s3',1195,932,340,'Amazon S3',['Originais · JSON · acordos','SSE-KMS · acesso interno'],h=112)
    flow('M 1085 996 H 1135 V 551 H 1195')
    flow('M 1085 1030 H 1154 V 784 H 1195')
    flow('M 1085 1064 H 1173 V 988 H 1195')
    text(1208,642,'Publicação / consumo pelo backend','aws-small')
    text(1208,671,'Nenhum acesso direto de clientes','aws-small')

    # Egress from tasks through NAT and the internet gateway.
    box(30,700,225,232,'#fffaf2','#d1b285');text(142,737,'Integrações externas','aws-label','middle')
    for i,line in enumerate(['OpenRouter / LLM','GREEN-API · e-mail / SMS','GenLayer RPC','Fornecedor de assinatura']):text(142,776+i*32,line,'aws-small','middle')
    flow('M 959 762 V 735 H 1073 V 555 H 1055',out=True)
    flow('M 922 512 V 449 H 966 V 438',out=True)
    flow('M 966 402 V 306 H 292 V 816 H 255',out=True)
    text(142,981,'Saída HTTPS pelo backend','aws-small','middle')
    text(142,1004,'sem acesso externo ao S3','aws-small','middle')

    # Cross-cutting support deliberately separated from request-path arrows.
    box(330,1180,1245,205,'#fafbfc','#bdc9d0')
    text(350,1210,'SEGURANÇA, ENTREGA E OPERAÇÃO · SERVIÇOS DE SUPORTE','aws-group')
    support=[('iam','IAM','Papéis por serviço'),('kms','KMS','Chaves de criptografia'),('secrets','Secrets Manager','Credenciais protegidas'),('ecr','Amazon ECR','Imagens OCI'),('cloudwatch','CloudWatch','Logs, métricas e alarmes')]
    for i,(key,title,detail) in enumerate(support):
        x=358+i*242;icon(key,x+67,1231,52);text(x+93,1310,title,'aws-label','middle');text(x+93,1337,detail,'aws-small','middle')
    text(350,1368,'Terraform: rede, políticas, dados, filas e runtime ECS. Conexões de suporte omitidas para legibilidade.','aws-small')
    text(30,1436,'Visão lógica da fase 2. Sub-redes, réplicas e zonas de disponibilidade são dimensionadas no Terraform. EKS / Helm ficam fora desta implantação.','aws-small')
    text(30,1459,'Ícones oficiais AWS Architecture Icons · pacote 31/07/2026 · cores e formas originais preservadas. Arquitetura proposta pela Mediare.','aws-small')
    parts.append('</svg>')
    output=ROOT/'DIAGRAMA_INFRA_AWS_MEDIARE.svg';output.write_text('\n'.join(parts))
    return output


if __name__ == '__main__':
    print(build())
