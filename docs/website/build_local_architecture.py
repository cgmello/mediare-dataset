"""Render Docker/LocalStack development and external production integrations."""
from pathlib import Path
from html import escape
ROOT=Path(__file__).resolve().parent

def build():
    parts=['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1640 1390" role="img" aria-labelledby="local-title local-desc">
<title id="local-title">Mediare — fase 1 Docker Compose, PostgreSQL e LocalStack</title><desc id="local-desc">Evolução em três fases: Docker e LocalStack locais; AWS com ECS Fargate; Kubernetes futuro. Frontend, API, workers, PostgreSQL e LocalStack ficam na máquina local. LocalStack emula S3, DynamoDB e SQS. OpenRouter, Google e consenso GenLayer permanecem serviços reais externos. GenLayer consulta somente a API de snapshots de teste por uma ponte HTTPS restrita.</desc>
<defs><marker id="local-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10z" fill="#527685"/></marker></defs>
<style>.local-title{font:700 28px Arial;fill:#183845}.local-heading{font:700 21px Arial;fill:#214758}.local-label{font:17px Arial;fill:#3e5966}.local-small{font:15px Arial;fill:#526978}.local-flow{fill:none;stroke:#527685;stroke-width:2;marker-end:url(#local-arrow)}</style><rect width="1640" height="1390" fill="#fff"/>
<text x="35" y="44" class="local-title">Mediare · fase 1 local e evolução da infraestrutura</text>''']
    def text(x,y,value,cls='local-label'):
        parts.append(f'<text x="{x}" y="{y}" class="{cls}">{escape(value)}</text>')
    def box(x,y,w,h,title,lines,fill='#fff',stroke='#b3c8d0'):
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        text(x+20,y+32,title,'local-heading')
        for i,line in enumerate(lines):text(x+20,y+62+i*25,line,'local-small')
    def flow(path,dashed=False):parts.append(f'<path d="{path}" class="local-flow"'+(' stroke-dasharray="7 5"' if dashed else '')+'/>')
    box(35,85,470,120,'Fase 1 · Docker + LocalStack',['Aplicação e dependências locais','OpenRouter, Google e GenLayer reais'],'#eaf5ef','#5d9b81')
    box(585,85,470,120,'Fase 2 · AWS',['ECS Fargate · serviços gerenciados','Terraform · sem Kubernetes'],'#f3f6fc')
    box(1135,85,470,120,'Fase 3 · Kubernetes',['EKS proposto · migração futura','Dados e contratos preservados'],'#f7f4fb')
    flow('M505 145 H585');flow('M1055 145 H1135')
    parts.append('<rect x="35" y="255" width="1060" height="1060" rx="8" fill="#f7fafb" stroke="#7ba7b7" stroke-width="2"/>')
    text(60,292,'MÁQUINA DO DESENVOLVEDOR · DOCKER COMPOSE','local-heading')
    box(65,335,225,95,'Navegador',['localhost · TLS local'])
    box(355,335,295,95,'gateway',['Proxy local · entrada única'])
    box(735,335,320,95,'frontend',['React / TypeScript'])
    flow('M290 382 H355');flow('M650 382 H735')
    box(355,535,295,145,'api',['Python · Django / DRF','/api/v1 · /public/v1','Upload e download pela API'])
    box(735,535,320,190,'Workers separados',['worker-documents','worker-notifications / committee','outbox-dispatcher','reconciliation'])
    flow('M505 430 V535');text(525,485,'HTTP interno','local-small')
    box(65,535,225,145,'mailpit',['E-mail de teste / OTP','Sem entrega real','Ferramenta local'])
    flow('M735 690 H675 V740 H320 V650 H290')
    # Shared internal data bus; tasks still communicate asynchronously via SQS.
    parts.append('<path d="M505 680 V790 H215 M895 725 V790 H505" fill="none" stroke="#527685" stroke-width="2"/>')
    flow('M215 790 V865');flow('M755 790 V865')
    text(65,1087,'Rede de dados interna · sem portas PostgreSQL / LocalStack publicadas','local-small')
    box(65,865,300,195,'postgres',['PostgreSQL real em container','Mesmo motor e migrations do RDS','Volume: postgres_data','Não é emulação de RDS'])
    box(425,865,630,195,'localstack · endpoint interno :4566',['Um container emula S3, DynamoDB e SQS','SDKs com endpoint local; credenciais AWS fictícias','Buckets versionados · tabelas JSON · filas e DLQs','Persistência habilitada · volume: localstack_data'],'#f0edf9','#a599bd')
    box(65,1110,990,100,'Bootstrap e testes',['Healthchecks → recursos locais → migrations → dados sintéticos → API / workers','Mocks são opcionais para testes; não substituem os provedores reais do desenvolvimento.'],'#edf4f6')
    text(65,1250,'Sem provisionamento AWS na fase 1. LocalStack requer token/plano compatível.','local-small')
    text(65,1280,'Sem Docker socket para o escopo S3 / DynamoDB / SQS, salvo necessidade validada.','local-small')
    # External providers are deliberately outside the local machine boundary.
    text(1165,295,'INTERNET · SERVIÇOS REAIS','local-heading')
    box(1195,380,410,115,'OpenRouter',['LLMs reais · KYC e documentos','Chamadas pelo backend / workers'],'#fff8ed','#ccb891')
    box(1195,555,410,115,'Google',['OAuth real · usuário de teste','Navegador e callback da API'],'#fff8ed','#ccb891')
    box(1195,730,410,145,'GenLayer',['RPC / contrato em rede de teste','Consenso real · carteira de teste','Resultado acompanhado pelo worker'],'#fff8ed','#ccb891')
    flow('M1055 570 H1120 V437 H1195')
    flow('M650 610 H700 V470 H1135 V612 H1195')
    flow('M1055 650 H1150 V803 H1195')
    box(1195,1000,410,225,'API de snapshot em HTTPS',['Ponte restrita para o ensaio real','Somente GET /public/v1/cases/{snapshot_uuid}.json','Snapshots sintéticos aprovados','Sem acesso ao admin, banco ou S3','localhost não é acessível aos validadores'],'#f0f7f4','#90b09e')
    flow('M1400 875 V1000',True)
    flow('M1195 1145 H1125 V755 H695 V650 H650',True)
    text(1195,1280,'Retorno ao endpoint local por proxy autorizado.','local-small')
    text(35,1350,'Visão lógica. Saída externa controlada; acesso público de teste limitado à rota de snapshot. Demais integrações seguem os adaptadores da especificação.','local-small')
    text(35,1375,'Persistência e APIs emuladas devem ser verificadas na versão/plano do LocalStack. Segurança e comportamento AWS são homologados na fase 2.','local-small')
    parts.append('</svg>')
    path=ROOT/'DIAGRAMA_INFRA_LOCAL_MEDIARE.svg';path.write_text('\n'.join(parts));return path

if __name__=='__main__':print(build())
