"""Build the standalone HTML specification using only the Python standard library.

The source format uses headings, paragraphs, pipe tables and local SVG figures.
Run: python3 docs/website/build_spec_html.py
"""
from pathlib import Path
import html
import re
from build_state_diagrams import build as build_state_diagrams
from build_aws_diagram import build as build_aws_diagram
from build_data_model import build as build_data_model, dictionary as data_dictionary
from build_local_architecture import build as build_local_architecture

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'ESPECIFICACAO_SISTEMA_MEDIARE_v1_10.md'
OUTPUT = SOURCE.with_suffix('.html')

CSS = r'''
.aws-figure figcaption,.mer-figure figcaption{display:flex;align-items:center;justify-content:space-between;gap:15px}.expand-diagram{font-size:12px;white-space:nowrap}.aws-dialog{padding:0;border:1px solid #9cabb3;border-radius:8px;width:96vw;max-width:none;height:94vh;max-height:94vh;background:#fff;color:var(--ink)}.aws-dialog[open]{display:flex;flex-direction:column}.aws-dialog::backdrop{background:#0f263ab3}.aws-dialog header{padding:12px 18px;display:flex;justify-content:space-between;align-items:center;gap:16px;border-bottom:1px solid var(--line)}.aws-dialog header strong{font-size:14px}.aws-dialog header div{display:flex;gap:8px}.aws-dialog .diagram-canvas{overflow:auto;flex:1;padding:16px}.aws-dialog img{width:1640px;max-width:none;height:auto;display:block}.diagram-help{font-size:12px;color:var(--muted);padding:7px 18px;margin:0;background:#f4f8f7}@media print{.expand-diagram,.aws-dialog{display:none!important}}

.state-figure{margin:24px 0 28px;border:1px solid var(--line);border-radius:5px;break-inside:avoid}.state-figure figcaption{font-size:12px;font-weight:600;padding:13px 18px;background:#f3f8f6;border-bottom:1px solid var(--line)}.state-scroll{overflow-x:auto;padding:10px}.state-scroll svg{display:block;width:100%;min-width:780px;height:auto}@media print{.state-figure{break-inside:avoid}.state-scroll{overflow:visible;padding:0}.state-scroll svg{min-width:0;width:100%}.state-figure figcaption{font-size:9pt}}

:root{--ink:#172c38;--muted:#536570;--accent:#176e69;--line:#dbe3e4;--paper:#fff;--wash:#f3f6f5;--nav:282px;--header:70px}
*{box-sizing:border-box}html{scroll-padding-top:94px}body{margin:0;color:var(--ink);background:var(--wash);font:16px/1.75 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}a{color:var(--accent);text-underline-offset:3px}button,input{font:inherit}button{cursor:pointer}button:focus-visible,a:focus-visible,input:focus-visible,[tabindex]:focus-visible{outline:3px solid #c49137;outline-offset:4px}button{border:1px solid var(--line);border-radius:5px;padding:7px 14px;background:#fff;color:var(--ink)}button:hover{background:var(--wash)}.skip{position:fixed;left:12px;top:-100px;z-index:10;background:#fff;padding:12px}.skip:focus{top:10px}
.topbar{height:var(--header);position:fixed;inset:0 0 auto;z-index:5;display:flex;align-items:center;justify-content:space-between;padding:0 30px;background:#fff;border-bottom:1px solid var(--line)}.wordmark{font:700 26px Georgia,serif;letter-spacing:-1px;text-decoration:none;color:var(--ink)}.wordmark b{color:var(--accent)}.topmeta{display:flex;align-items:center;gap:20px;font-size:12px;color:var(--muted)}.edition{letter-spacing:.1em;text-transform:uppercase}.menu-button{display:none}
.sidebar{position:fixed;top:var(--header);bottom:0;left:0;width:var(--nav);background:#fafbfa;border-right:1px solid var(--line);padding:26px 20px;overflow-y:auto}.nav-label,.eyebrow{font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}.sidebar .nav-label{margin:0 9px 15px}.sidebar nav a{display:flex;gap:11px;padding:7px 9px;text-decoration:none;font-size:12px;line-height:1.5;color:var(--muted);border-left:2px solid transparent}.sidebar nav a span{min-width:20px;color:#70838c;font-variant-numeric:tabular-nums}.sidebar nav a:hover,.sidebar nav a[aria-current]{color:var(--ink);background:#e9f0ee;border-left-color:var(--accent)}.nav-group{margin:22px 9px 6px;font-size:10px;color:var(--accent);letter-spacing:.13em;text-transform:uppercase;font-weight:700}.sidebar nav a.sub{padding-left:20px;font-size:11px}.nav-foot{margin:24px 9px 0;font-size:11px;color:var(--muted);border-top:1px solid var(--line);padding-top:15px}
main{margin:var(--header) 0 0 var(--nav);padding:44px 5vw 60px;max-width:1550px}.cover{background:var(--paper);border:1px solid var(--line);padding:48px 52px 36px;position:relative}.cover:before{content:"";position:absolute;top:0;left:0;width:96px;height:4px;background:var(--accent)}.doc-status{display:inline-block;border:1px solid #c8ddda;color:var(--accent);padding:3px 10px;border-radius:3px;font-size:11px;margin-bottom:24px}.cover h1{font:400 clamp(36px,4vw,58px)/1.08 Georgia,"Times New Roman",serif;letter-spacing:-1.6px;margin:13px 0 20px;max-width:780px}.deck{font-size:17px;color:var(--muted);max-width:710px;margin:0 0 30px}.metadata{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;border-top:1px solid var(--line);padding-top:20px;margin:0}.metadata dt{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.12em}.metadata dd{font-size:13px;font-weight:600;margin:4px 0 0}.summary{margin-top:28px;background:#eaf2ef;border-left:3px solid var(--accent);padding:20px 24px}.summary h2{font-size:14px;margin:0 0 6px}.summary p{font-size:13px;margin:0;color:#35534e}.summary a{font-weight:600}
.reader-tools{display:flex;gap:18px;align-items:center;margin:28px 0 12px;flex-wrap:wrap}.searchbox{display:flex;flex:1;min-width:220px;align-items:center;background:white;border:1px solid #bdcdcf;border-radius:5px;padding:0 13px}.searchbox label{font-size:12px;color:var(--muted);padding-right:12px}.searchbox input{width:100%;border:0;outline-offset:0;background:transparent;padding:11px 0;font-size:13px;min-width:0}.reader-tools output{font-size:12px;color:var(--muted)}.noscript{font-size:13px}.legend{display:flex;gap:17px;flex-wrap:wrap;font-size:11px;color:var(--muted);margin:16px 0 30px}.legend b{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;color:var(--accent);margin-right:4px}
.chapter{background:#fff;border:1px solid var(--line);padding:34px 44px;margin:0 0 24px;scroll-margin-top:94px}.chapter>h2{font:400 29px/1.25 Georgia,serif;margin:0 0 28px;letter-spacing:-.45px;display:flex;gap:20px;align-items:baseline;border-bottom:1px solid var(--line);padding-bottom:20px}.section-number{font:500 13px/1.5 ui-monospace,SFMono-Regular,Consolas,monospace;color:var(--accent);min-width:25px}.chapter h3{font-size:18px;margin:36px 0 20px;padding-top:14px;border-top:1px solid var(--line);scroll-margin-top:95px}.chapter p{font-size:14px;line-height:1.85;margin:0 0 19px;overflow-wrap:anywhere}.chapter>p:last-child{margin-bottom:0}.requirement{position:relative;padding-left:80px;scroll-margin-top:100px}.req-id{position:absolute;left:0;top:3px;font:600 11px/1.65 ui-monospace,SFMono-Regular,Consolas,monospace;background:#edf4f2;color:#185f5a;border:1px solid #d5e7e2;border-radius:3px;padding:3px 7px;text-decoration:none}.requirement[data-kind="RN"] .req-id{background:#f8f2e7;border-color:#e9dec7;color:#75521b}.requirement[data-kind="CA"] .req-id{background:#edf0f8;border-color:#d8dfed;color:#3c5583}.requirement:target{background:#fff6d8;outline:8px solid #fff6d8}.reference{scroll-margin-top:100px}.reference:target{background:#fff6d8}.citation{font-size:11px;white-space:nowrap;font-weight:600;text-decoration:none}.chapter code{font:12px ui-monospace,SFMono-Regular,Consolas,monospace;background:#f1f4f5;padding:2px 4px;border-radius:3px}.table-wrap{overflow-x:auto;margin:24px 0 28px;border:1px solid var(--line);border-radius:4px}.table-wrap table{border-collapse:collapse;width:100%;font-size:12px;line-height:1.65;table-layout:auto}.table-wrap th{text-align:left;background:#203e4b;color:#fff;font-size:11px;font-weight:600;padding:13px 14px}.table-wrap td{padding:12px 14px;border-top:1px solid var(--line);vertical-align:top;overflow-wrap:anywhere;min-width:85px}.table-wrap td:first-child{font-weight:600;color:#244953}.table-wrap tr:nth-child(even) td{background:#f5f8f7}.table-wrap tr:target td{background:#fff4cf}.table-wrap tr{scroll-margin-top:100px}.table-wrap tr[id]>td:first-child{white-space:nowrap}.table-wrap a{overflow-wrap:anywhere}.table-label{font-size:11px;color:var(--muted);padding:8px 14px;border-bottom:1px solid var(--line);background:#fafcfb}
.arch{margin:25px 0 32px;padding:25px;border:1px solid #ccdbd9;background:#f5f9f7}.arch figcaption{font-size:12px;font-weight:600;margin-bottom:20px}.arch-flow{display:grid;grid-template-columns:1fr 24px 1fr 24px 1fr;align-items:center;gap:6px}.node{background:#fff;border:1px solid #c6d6d3;padding:13px;font-size:12px;line-height:1.5;text-align:center}.node strong{display:block;color:var(--accent);font-size:13px;margin-bottom:4px}.arrow{text-align:center;color:var(--accent)}.data-row{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:18px}.arch-note{font-size:11px;color:var(--muted);margin:15px 0 0}.diagram-caption{font-size:11px;margin:16px 0 0;color:var(--muted)}.empty{padding:30px;background:#fff;border:1px solid var(--line)}[hidden]{display:none!important}.doc-footer{border-top:1px solid var(--line);margin-top:38px;padding-top:20px;color:var(--muted);display:flex;justify-content:space-between;gap:20px;font-size:11px}.print-note{display:none}
@media(min-width:1600px){main{padding-left:7vw;padding-right:7vw}}@media(max-width:1100px){:root{--nav:246px}main{padding:30px}.cover{padding:36px}.chapter{padding:30px}.edition{display:none}}
@media(max-width:800px){:root{--header:62px}.topbar{padding:0 18px}.menu-button{display:inline-block}.topmeta{gap:8px}.sidebar{display:none;z-index:4;width:290px;box-shadow:12px 0 24px #17343c18}.sidebar.open{display:block}main{margin-left:0;padding:22px 16px}.cover{padding:30px 24px}.cover h1{font-size:40px}.metadata{grid-template-columns:1fr 1fr}.chapter{padding:26px 23px}.chapter>h2{font-size:26px;gap:12px}.requirement{padding-left:0;padding-top:33px}.requirement .req-id{top:0}.table-wrap table{min-width:590px}.doc-footer{flex-direction:column}.legend{gap:9px 18px}}
@media(max-width:460px){.wordmark{font-size:24px}.topmeta button{font-size:11px;padding:6px 9px}.metadata{grid-template-columns:1fr}.arch{padding:16px}.arch-flow{grid-template-columns:1fr}.arrow{transform:rotate(90deg)}.data-row{grid-template-columns:1fr}.chapter p{font-size:14px}.cover h1{font-size:35px}.reader-tools output{width:100%}}
@media print{@page{size:A4;margin:17mm 16mm 19mm;@bottom-left{content:"Mediare · MED-SYS-SPEC · v1.10";font:8pt Arial;color:#536570}@bottom-right{content:counter(page) " / " counter(pages);font:8pt Arial;color:#536570}}body{background:white;font:10pt/1.5 Arial,sans-serif;color:#111}.topbar,.sidebar,.reader-tools,.legend,.skip,.noscript,.summary,.doc-footer{display:none!important}main{margin:0;padding:0;max-width:none}.cover{border:0;padding:20mm 0 10mm;break-after:page}.cover h1{font-size:38pt}.cover .deck{font-size:13pt}.metadata{margin-top:20mm}.print-note{display:block;font-size:10pt;color:#555;margin-top:15mm}.chapter,.chapter[hidden]{display:block!important;border:0;border-radius:0;padding:0;margin:0 0 9mm;break-before:page}.chapter h2{font-size:22pt;break-after:avoid}.chapter h3{font-size:13pt;break-after:avoid}.chapter p{font-size:10pt;line-height:1.6;orphans:3;widows:3}.requirement{padding-left:0}.req-id{position:static;display:inline;border:0;padding:0;margin-right:6px;background:none!important;color:#111!important;font-size:9pt}.table-wrap{overflow:visible;border:0}.table-wrap table{min-width:0!important;width:100%;font-size:8pt}.table-wrap th{background:#e9eeee!important;color:#111;padding:7px}.table-wrap td{padding:7px;min-width:0}.table-wrap thead{display:table-header-group}.table-wrap tr{break-inside:avoid}.table-label{display:none}a{color:inherit;text-decoration:none}.reference{font-size:9pt!important}.arch{break-inside:avoid}.node,.arch figcaption{font-size:9pt}.node strong{font-size:10pt}.arch-flow{grid-template-columns:1fr 24px 1fr 24px 1fr}.data-row{grid-template-columns:repeat(3,1fr)}.arrow{transform:none}.cover:before{display:none}}
'''

JS = r'''
const search = document.querySelector('#search');
const chapters = [...document.querySelectorAll('.chapter')];
const count = document.querySelector('#result-count');
const navLinks = [...document.querySelectorAll('nav a')];
const normal = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const contents = chapters.map(c => normal(c.textContent));
function filter() {
  const terms = normal(search.value.trim()).split(/\s+/).filter(Boolean);
  let shown = 0;
  chapters.forEach((c,i) => {
    c.hidden = !terms.every(t => contents[i].includes(t));
    if (!c.hidden) shown++;
  });
  count.textContent = terms.length ? `${shown} de ${chapters.length} seções encontradas` : `${chapters.length} seções · leitura integral`;
  document.querySelector('#empty').hidden = shown > 0;
}
search.addEventListener('input',filter);
document.querySelector('#clear').addEventListener('click',()=>{search.value='';filter();search.focus();});
const sidebar = document.querySelector('.sidebar');
const menu = document.querySelector('#menu');
menu.addEventListener('click',()=>{const open=sidebar.classList.toggle('open');menu.setAttribute('aria-expanded',String(open));});
function closeMenu(){sidebar.classList.remove('open');menu.setAttribute('aria-expanded','false');}
document.addEventListener('keydown',e=>{if(e.key==='Escape'){closeMenu();if(sidebar.contains(document.activeElement))menu.focus();}});
document.addEventListener('click',e=>{if(!sidebar.contains(e.target)&&!menu.contains(e.target))closeMenu();});
function reveal(hash){let id;try{id=decodeURIComponent(hash.slice(1));}catch{return;}const el=document.getElementById(id);if(el){const section=el.closest('.chapter');if(section?.hidden){search.value='';filter();}return el;}}
document.querySelectorAll('a[href^="#"]').forEach(link=>link.addEventListener('click',()=>{reveal(link.hash);if(sidebar.contains(link)){closeMenu();const el=document.getElementById(link.hash.slice(1));if(el){el.tabIndex=-1;el.focus({preventScroll:true});}}}));
window.addEventListener('hashchange',()=>reveal(location.hash)?.scrollIntoView());
document.querySelector('#print').addEventListener('click',()=>window.print());
const observer=new IntersectionObserver(entries=>{const visible=entries.filter(e=>e.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top);if(!visible.length)return;const hash='#'+visible[0].target.id;navLinks.forEach(a=>{if(a.hash===hash)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});},{rootMargin:'-80px 0px -65% 0px',threshold:0});
chapters.forEach(c=>observer.observe(c));filter();reveal(location.hash);
const awsDialog=document.querySelector('#aws-diagram-dialog');
let awsImageURL;
let diagramFilename;
document.querySelectorAll('.expand-diagram').forEach(button=>button.addEventListener('click',()=>{
 const svg=button.closest('figure').querySelector('svg');
 diagramFilename=button.dataset.filename;
 awsDialog.querySelector('strong').textContent=button.dataset.label;
 awsDialog.querySelector('img').alt=button.dataset.label;
 awsDialog.querySelector('img').style.width=svg.viewBox.baseVal.width+'px';
 awsImageURL=URL.createObjectURL(new Blob([svg.outerHTML],{type:'image/svg+xml'}));
 awsDialog.querySelector('img').src=awsImageURL;
 awsDialog.showModal();
}));
awsDialog.querySelector('.close-diagram').addEventListener('click',()=>awsDialog.close());
awsDialog.addEventListener('close',()=>{if(awsImageURL){URL.revokeObjectURL(awsImageURL);awsImageURL=undefined;}});
awsDialog.querySelector('.download-diagram').addEventListener('click',()=>{if(!awsImageURL)return;const link=document.createElement('a');link.href=awsImageURL;link.download=diagramFilename;link.click();});

'''



def inline(value):
    value = html.escape(value)
    def link(match):
        url = match[0].rstrip('.,;')
        suffix = match[0][len(url):]
        return f'<a href="{url}" rel="noreferrer">{url}</a>{suffix}'
    value = re.sub(r'https?://[^\s<>]+', link, value)
    value = re.sub(r'\[(F\d+(?:, F\d+)*)\]', lambda m: ' '.join(f'<a class="citation" href="#ref-{x}">[{x}]</a>' for x in m[1].split(', ')), value)
    return value


def render():
    build_state_diagrams()
    build_aws_diagram()
    build_local_architecture()
    build_data_model()
    source = SOURCE.read_text()
    assert data_dictionary() in source, "Data dictionary differs from the model source"
    chunks = re.split(r'^## (\d+) (.+)$', source, flags=re.M)
    chapters, nav = [], ['<a href="#documento"><span>—</span>Visão geral</a>']
    groups = {'1':'Contexto e escopo','3':'Requisitos do produto','17':'Arquitetura e infraestrutura','21':'Governança e entrega','26':'Controle documental'}
    for i in range(1, len(chunks), 3):
        num, title, body = chunks[i:i+3]
        if num in groups:
            nav.append(f'<div class="nav-group">{groups[num]}</div>')
        nav.append(f'<a href="#sec-{num}"><span>{int(num):02}</span>{html.escape(title)}</a>')
        parts = [f'<section class="chapter" id="sec-{num}" aria-labelledby="heading-{num}"><h2 id="heading-{num}"><span class="section-number">{int(num):02}</span>{html.escape(title)}</h2>']
        table_num = 0
        for block in re.split(r'\n\s*\n', body.strip()):
            block = block.strip()
            if not block:
                continue
            figure = re.fullmatch(r'!\[([^\]]+)\]\((DIAGRAMA_(?:ESTADOS(?:_ALTERNATIVOS)?|INFRA_(?:AWS|LOCAL)|MER_[A-Z]+)_MEDIARE\.svg)\)', block)
            if figure:
                label, filename = figure.groups()
                svg = (ROOT / filename).read_text()
                prefix = 'states-alt' if 'ALTERNATIVOS' in filename else 'states-main'
                for key in ('title', 'desc', 'arrow'):
                    svg = svg.replace(f'id="{key}"', f'id="{prefix}-{key}"').replace(f'url(#{key})', f'url(#{prefix}-{key})')
                svg = svg.replace('aria-labelledby="title desc"', f'aria-labelledby="{prefix}-title {prefix}-desc"')
                aws = 'INFRA_AWS' in filename
                mer = 'MER_' in filename or 'INFRA_LOCAL' in filename
                expand = f'<button class="expand-diagram{" expand-aws" if aws else ""}" data-filename="{filename}" data-label="{html.escape(label)}" type="button">Ampliar diagrama</button>' if aws or mer else ''
                parts.append(f'<figure class="state-figure{" aws-figure" if aws else " mer-figure" if mer else ""}"><figcaption>{html.escape(label)}{expand}</figcaption><div class="state-scroll" role="region" tabindex="0" aria-label="{html.escape(label)}">{svg}</div></figure>')
            elif block.startswith('### '):
                match = re.fullmatch(r'### (\d+[A-Z]) (.+)', block)
                sub, label = match.groups()
                parts.append(f'<h3 id="sec-{sub}">{sub} · {html.escape(label)}</h3>')
                nav.append(f'<a class="sub" href="#sec-{sub}"><span>{sub}</span>{html.escape(label)}</a>')
            elif block.startswith('|'):
                table_num += 1
                rows = [[c.strip() for c in line.strip().strip('|').split('|')] for line in block.splitlines()]
                parts.append(f'<div class="table-wrap" role="region" tabindex="0" aria-label="Tabela {num}.{table_num} — {html.escape(title)}"><div class="table-label">Tabela {num}.{table_num} · {html.escape(title)}</div><table><thead><tr>')
                parts.extend(f'<th scope="col">{inline(c)}</th>' for c in rows[0])
                parts.append('</tr></thead><tbody>')
                for row in rows[2:]:
                    row_id = re.fullmatch(r'(CA|D)-\d+', row[0])
                    parts.append(f'<tr id="{row[0]}">' if row_id else '<tr>')
                    parts.extend(f'<td>{inline(c)}</td>' for c in row)
                    parts.append('</tr>')
                parts.append('</tbody></table></div>')
            else:
                requirement = re.match(r'^((RF|RT|RN|CA)-\d+[A-Z]?)\. (.*)', block, re.S)
                reference = re.match(r'^(F\d+)\. ', block)
                if requirement:
                    rid, kind, text = requirement.groups()
                    parts.append(f'<p class="requirement" data-kind="{kind}" id="{rid}"><a class="req-id" href="#{rid}" aria-label="Link para {rid}">{rid}</a>{inline(text)}</p>')
                elif reference:
                    parts.append(f'<p class="reference" id="ref-{reference[1]}">{inline(block)}</p>')
                else:
                    parts.append(f'<p>{inline(block)}</p>')
        parts.append('</section>')
        chapters.append('\n'.join(parts))
    page = f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="Especificação funcional e técnica da plataforma Mediare. Requisitos, arquitetura AWS, segurança e critérios de aceite."><title>Mediare — Especificação do Sistema · v1.10</title><style>{CSS}</style></head>
<body><a class="skip" href="#conteudo">Ir para o conteúdo</a>
<header class="topbar"><a class="wordmark" href="#documento">mediare<b>.</b></a><div class="topmeta"><span class="edition">Documentação de produto e engenharia</span><button id="menu" class="menu-button" aria-controls="indice" aria-expanded="false">Índice</button><button id="print" type="button">Imprimir / PDF</button></div></header>
<aside class="sidebar" id="indice"><div class="nav-label">Nesta especificação</div><nav aria-label="Índice do documento">{''.join(nav)}</nav><div class="nav-foot">MEDIARE · ESPECIFICAÇÃO 1.10<br>29 de setembro de 2026<br>Documento para revisão</div></aside>
<main id="conteudo"><header class="cover" id="documento"><span class="doc-status">Proposta para validação</span><div class="eyebrow">Mediação extrajudicial online</div><h1>Especificação<br>do Sistema Mediare</h1><p class="deck">Requisitos funcionais, arquitetura de software e infraestrutura para o ciclo completo de mediação com apoio de inteligência artificial e supervisão humana.</p><dl class="metadata"><div><dt>Documento</dt><dd>MED-SYS-SPEC · Versão 1.10</dd></div><div><dt>Revisão</dt><dd>29 de setembro de 2026</dd></div><div><dt>Público</dt><dd>Produto, engenharia e operação</dd></div></dl><p class="print-note">Edição HTML · pessoas físicas e empresas na V1. Processamento documental híbrido proposto: extração local simples e IA via OpenRouter para leitura complexa, resumo e apoio à anonimização. Parâmetros propostos estão sujeitos à validação indicada no documento.</p></header>
<aside class="summary" aria-label="Diretrizes da entrega"><h2>Base da primeira versão</h2><p>Fase 1 local com Docker Compose, PostgreSQL e LocalStack para S3, DynamoDB e SQS. OpenRouter, Google e consenso GenLayer permanecem reais e externos. Fase 2 em AWS/ECS Fargate com Terraform; fase 3 futura em Kubernetes. Pessoas físicas e empresas na V1, com KYC somente das pessoas que atuam no caso. Processamento documental híbrido proposto com OpenRouter desde a V1. Pagamentos por PIX e cartão serão simulados. O MER e os contratos de dados são preservados entre as fases; emulação local não substitui homologação AWS. Consulte <a href="#sec-18">infraestrutura</a>, <a href="#sec-23">critérios de aceite</a> e <a href="#sec-25">decisões pendentes</a>.</p></aside>
<div class="reader-tools"><div class="searchbox"><label for="search">Buscar</label><input id="search" type="search" placeholder="Requisito, tecnologia ou assunto…" autocomplete="off" aria-describedby="result-count"></div><button id="clear" type="button">Limpar</button><output id="result-count" aria-live="polite"></output></div><noscript><p class="noscript">O documento completo está disponível abaixo. Para localizar termos, use a busca do navegador; para exportar, use a impressão do navegador.</p></noscript>
<div class="legend" aria-label="Convenções"><span><b>RF</b> Requisito funcional</span><span><b>RN</b> Regra de negócio</span><span><b>RT</b> Requisito técnico</span><span><b>CA</b> Critério de aceite</span><span><b>D</b> Decisão pendente</span></div>
<p id="empty" class="empty" hidden>Nenhuma seção encontrada. Tente outro termo ou limpe a busca para consultar o documento completo.</p>
{''.join(chapters)}
<footer class="doc-footer"><span>Mediare · MED-SYS-SPEC · v1.10</span><span>Pessoas físicas e empresas · requisitos e arquitetura</span><a href="#documento">Voltar ao início ↑</a></footer></main><dialog id="aws-diagram-dialog" class="aws-dialog" aria-labelledby="aws-dialog-title"><header><strong id="aws-dialog-title">Diagrama ampliado</strong><div><button class="download-diagram" type="button">Baixar SVG</button><button class="close-diagram" type="button" autofocus>Fechar</button></div></header><p class="diagram-help">Role para navegar pelo diagrama ampliado. O download preserva o formato vetorial SVG.</p><div class="diagram-canvas" tabindex="0" role="region" aria-label="Diagrama ampliado"><img alt="Infraestrutura AWS proposta para o piloto Mediare, usando ECS Fargate e armazenamento privado"></div></dialog><script>{JS}</script></body></html>'''
    OUTPUT.write_text(page)
    print(f'Generated {OUTPUT.name}: {len(chapters)} sections, {len(page):,} characters')


if __name__ == '__main__':
    render()
