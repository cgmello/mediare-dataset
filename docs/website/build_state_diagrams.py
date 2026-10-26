"""Generate self-contained SVG state diagrams for the HTML specification."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parent


def canvas(height, title, description):
    return [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#316c69"/></marker></defs>
<style>text{{font-family:Arial,sans-serif;fill:#203e4b}}.name{{font-size:20px;font-weight:600}}.detail{{font-size:15px;fill:#526971}}.tag{{font-size:13px;fill:#176e69;font-weight:700;letter-spacing:1px}}.edge{{fill:none;stroke:#316c69;stroke-width:2;marker-end:url(#arrow)}}.return{{stroke-dasharray:7 5}}.lane{{font-size:14px;fill:#176e69;font-weight:700;letter-spacing:1px}}</style>
<rect width="1120" height="{height}" fill="#fff"/>''']


def node(x, y, width, height, lines, detail='', tag='', tone='normal'):
    fill, border = {'normal': ('#f4f8f7','#b4cdca'), 'end':('#e2f0e9','#459378'), 'alt':('#faf5eb','#cdbb94')}[tone]
    out = [f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8" fill="{fill}" stroke="{border}" stroke-width="1.5"/>']
    if tag:
        out.append(f'<text x="{x+16}" y="{y+23}" class="tag">{escape(tag)}</text>')
    start = y + (49 if tag else (height-(len(lines)-1)*25)/2+7)
    out.extend(f'<text x="{x+width/2}" y="{start+i*25}" text-anchor="middle" class="name">{escape(line)}</text>' for i,line in enumerate(lines))
    if detail:
        out.append(f'<text x="{x+width/2}" y="{y+height-13}" text-anchor="middle" class="detail">{escape(detail)}</text>')
    return ''.join(out)


def edge(path, dashed=False):
    return f'<path d="{path}" class="edge{" return" if dashed else ""}"/>'


def build():
    main = canvas(660, 'Fluxo principal da mediação', 'Doze estados, do rascunho até a conclusão com acordo. A leitura segue as setas em três linhas alternadas. As condições completas de avanço estão na tabela da seção 11.')
    states = [
        (35,60,['Rascunho'],'Pedido em preparação'),
        (310,60,['Aguardando','adesão'],'Convite emitido'),
        (585,60,['Em instrução'],'Documentos e manifestações'),
        (860,60,['Aguardando','pagamento'],'Dados congelados'),
        (860,260,['Pronto para','análise'],'Cotas e snapshot liberados'),
        (585,260,['Em análise'],'Comitê GenLayer'),
        (310,260,['Revisão humana'],'Mediador do caso'),
        (35,260,['Em agendamento'],'Cinco opções de horário'),
        (35,460,['Agendado'],'Horário reservado'),
        (310,460,['Em sessão'],'Discussão do termo'),
        (585,460,['Em assinatura'],'Versão final congelada'),
        (860,460,['Concluído com','acordo'],'Três assinaturas válidas'),
    ]
    for i,(x,y,note,detail) in enumerate(states):
        main.append(node(x,y,225,124,note,detail,f'{i+1:02}', 'end' if i==11 else 'normal'))
    for y in (122,522):
        for x in (260,535,810):main.append(edge(f'M {x} {y} H {x+50}'))
    for x in (860,585,310):main.append(edge(f'M {x} 322 H {x-50}'))
    main += [edge('M 972.5 184 V 260'), edge('M 147.5 384 V 460')]
    main.append('<text x="35" y="25" class="lane">FLUXO PRINCIPAL · SEGUIR AS SETAS</text>')
    main.append('<text x="35" y="624" class="detail">Entrada em pagamento: congelamento das revisões. Na V1, PIX e cartão são simulados.</text>')
    main.append('<text x="35" y="648" class="detail">A revisão humana deste fluxo é do mediador; a política de revisão da publicação é um controle separado.</text></svg>')
    (ROOT/'DIAGRAMA_ESTADOS_MEDIARE.svg').write_text('\n'.join(main))

    alt = canvas(810, 'Estados alternativos e retomada', 'Convites podem ser recusados ou expirar. Uma etapa ativa elegível pode ser suspensa, apresentar falha técnica recuperável, ser cancelada ou encerrar sem acordo, conforme as regras do caso. A retomada exige resolução e revalidação da última etapa válida.')
    alt += ['<text x="35" y="28" class="lane">CONVITE · AUSÊNCIA DE ADESÃO</text>',
            node(35,76,265,80,['Aguardando adesão']),
            node(535,48,305,65,['Convite recusado'],tone='alt'),
            node(535,143,305,65,['Convite expirado'],tone='alt'),
            edge('M 300 116 H 420 V 80.5 H 535'),edge('M 420 116 V 175.5 H 535'),
            '<text x="440" y="65" class="detail">Recusa</text>',
            '<text x="440" y="163" class="detail">Prazo</text>',
            '<path d="M 35 239 H 1085" stroke="#dbe3e4"/>',
            '<text x="35" y="273" class="lane">INTERRUPÇÃO · RESOLUÇÃO E RETOMADA CONTROLADA</text>',
            node(35,343,265,85,['Etapa ativa elegível']),
            node(410,303,265,66,['Suspenso'],tone='alt'),
            node(410,401,265,85,['Falha técnica','recuperável'],tone='alt'),
            node(820,345,265,85,['Última etapa','válida']),
            edge('M 300 385.5 H 350 V 336 H 410'),edge('M 350 385.5 V 443.5 H 410'),
            edge('M 675 336 H 743 V 387.5 H 820',True),edge('M 675 443.5 H 743 V 387.5',True),
            '<text x="706" y="299" class="detail">Resolver e</text><text x="706" y="321" class="detail">revalidar</text>',
            '<text x="35" y="521" class="detail">Retomar sem duplicar efeitos; preservar o estado anterior, as revisões e os resultados já produzidos.</text>',
            '<path d="M 35 550 H 1085" stroke="#dbe3e4"/>',
            '<text x="35" y="583" class="lane">ENCERRAMENTO · CONFORME REGRA DA ETAPA</text>',
            node(35,650,265,80,['Etapa ativa elegível']),
            node(535,620,305,65,['Cancelado'],tone='alt'),
            node(535,716,305,65,['Encerrado sem acordo'],tone='alt'),
            edge('M 300 690 H 420 V 652.5 H 535'),edge('M 420 690 V 748.5 H 535'),
            '<text x="440" y="638" class="detail">Cancelar</text>',
            '<text x="854" y="738" class="detail">Sem consenso, recusa</text><text x="854" y="760" class="detail">ou encerramento</text>',
            '</svg>']
    (ROOT/'DIAGRAMA_ESTADOS_ALTERNATIVOS_MEDIARE.svg').write_text('\n'.join(alt))


if __name__ == '__main__':
    build()
