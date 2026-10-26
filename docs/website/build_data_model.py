"""Build self-contained entity relationship diagrams and the data dictionary."""
from pathlib import Path
from html import escape
import heapq
import json

ROOT = Path(__file__).resolve().parent
MODEL = ROOT / 'assets/data-model/model.json'


def build():
    model = json.loads(MODEL.read_text())
    entities = model['entities']
    outputs = []
    for view in model['views']:
        prefix = 'mer-' + view['key'].lower()
        width, height = 1380, 1120
        positions = {name: (40 + (i % 3) * 480, 130 + (i // 3) * 320) for i, name in enumerate(view['nodes'])}
        box_width, box_height = 340, 190
        occupied = set()
        for x, y in positions.values():
            for gx in range((x - 20)//10, (x + box_width + 20)//10 + 1):
                for gy in range((y - 20)//10, (y + box_height + 20)//10 + 1):
                    occupied.add((gx, gy))
        used = set()
        def port(name, side):
            x,y=positions[name]
            return {'right': ((x+340,y+100),(x+370,y+100)), 'left': ((x,y+100),(x-30,y+100)),
                    'bottom': ((x+170,y+190),(x+170,y+220)), 'top': ((x+170,y),(x+170,y-30))}[side]
        def route(start, end):
            start=tuple(v//10 for v in start);end=tuple(v//10 for v in end)
            queue=[(0,0,start)];previous={};cost={start:0}
            while queue:
                _,distance,current=heapq.heappop(queue)
                if current==end:break
                if distance!=cost[current]:continue
                for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                    nxt=(current[0]+dx,current[1]+dy)
                    if nxt in occupied or not (1<=nxt[0]<=137 and 9<=nxt[1]<=104):continue
                    value=distance+1+(4 if nxt in used else 0)
                    if value<cost.get(nxt,float('inf')):
                        cost[nxt]=value;previous[nxt]=current
                        heapq.heappush(queue,(value+abs(nxt[0]-end[0])+abs(nxt[1]-end[1]),value,nxt))
            assert end in cost,(view['key'],start,end)
            path=[end]
            while path[-1]!=start:path.append(previous[path[-1]])
            path.reverse();used.update(path)
            return [(x*10,y*10) for x,y in path]
        parts=[f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="{prefix}-title {prefix}-desc">
<title id="{prefix}-title">MER · {escape(view['title'])}</title><desc id="{prefix}-desc">Entidades relacionais com chaves e cardinalidades. As setas seguem da entidade referenciada para a dependente; campos e relações completas estão no dicionário da seção 19E.</desc>
<defs><marker id="{prefix}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#537784"/></marker></defs>
<style>.{prefix}-name{{font:700 18px Arial;fill:#fff}}.{prefix}-field{{font:15px monospace;fill:#263f4b}}</style><rect width="1380" height="1120" fill="#fff"/>
<text x="40" y="43" font-family="Arial" font-size="25" font-weight="700" fill="#172c38">{escape(view['title'])}</text>
<text x="40" y="76" font-family="Arial" font-size="17" fill="#536570">PostgreSQL · entidades e campos em inglês · PK = chave primária · FK = chave estrangeira · ? = opcional</text>''']
        paths=[]
        for source,target,one,many in view['edges']:
            sx,sy=positions[source];tx,ty=positions[target]
            if sy==ty:a,b=('right','left') if tx>sx else ('left','right')
            else:a,b=('bottom','top') if ty>sy else ('top','bottom')
            actual_start,start=port(source,a);actual_end,end=port(target,b)
            path=[actual_start]+route(start,end)+[actual_end]
            # Collapse collinear steps to improve SVG readability and label placement.
            simple=[path[0]]
            for i in range(1,len(path)-1):
                p,q,r=path[i-1:i+2]
                if (q[0]-p[0])*(r[1]-q[1]) != (q[1]-p[1])*(r[0]-q[0]):simple.append(q)
            simple.append(path[-1]);paths.append((simple,one,many))
            points=' '.join(f'{x},{y}' for x,y in simple)
            parts.append(f'<polyline points="{points}" fill="none" stroke="#537784" stroke-width="2" marker-end="url(#{prefix}-arrow)"><title>{source} ({one}) → {target} ({many})</title></polyline>')
        # Cardinalities sit on the longest available segment, away from entity labels.
        labels=[]
        for path,one,many in paths:
            segments=sorted(zip(path,path[1:]),key=lambda pair:abs(pair[0][0]-pair[1][0])+abs(pair[0][1]-pair[1][1]),reverse=True)
            chosen=None
            for a,b in segments:
                for fraction in (0.5,0.3,0.7):
                    cx=a[0]+(b[0]-a[0])*fraction;cy=a[1]+(b[1]-a[1])*fraction
                    for dx,dy in ((0,0),(30,0),(-30,0),(0,25),(0,-25)):
                        x,y=cx+dx,cy+dy
                        clear_nodes=all(x+48<bx or x-48>bx+340 or y+16<by or y-16>by+190 for bx,by in positions.values())
                        clear_labels=all(abs(x-px)>95 or abs(y-py)>28 for px,py in labels)
                        if clear_nodes and clear_labels and 48<x<1332 and 95<y<1040:
                            chosen=(x,y);break
                    if chosen:break
                if chosen:break
            assert chosen, (view['key'], 'No clear cardinality label position')
            x,y=chosen
            labels.append((x,y));label=f'{one} → {many}'
            parts.append(f'<rect x="{x-45}" y="{y-13}" width="90" height="24" rx="4" fill="#fff" stroke="#c6d6db"/><text x="{x}" y="{y+5}" text-anchor="middle" font-family="Arial" font-size="15" fill="#294f5f">{escape(label)}</text>')
        for name,(x,y) in positions.items():
            parts.append(f'<rect x="{x}" y="{y}" width="340" height="190" rx="6" fill="#f5f9fa" stroke="#9db9c3"/><path d="M{x+6} {y} H{x+334} Q{x+340} {y} {x+340} {y+6} V{y+38} H{x} V{y+6} Q{x} {y} {x+6} {y}" fill="#244d5d"/><text x="{x+14}" y="{y+26}" class="{prefix}-name">{name}</text>')
            for i,field in enumerate(entities[name]):
                display=field.split(' -> ')[0]
                font_size = min(15, 310 / (max(len(display), 1) * 0.61))
                parts.append(f'<text x="{x+14}" y="{y+63+i*22}" class="{prefix}-field" style="font-size:{font_size:.1f}px">{escape(display)}</text>')
        parts.append('<text x="40" y="1082" font-family="Arial" font-size="16" fill="#536570">Seta: entidade referenciada → dependente. Rótulo: cardinalidade na origem → cardinalidade no destino.</text><text x="40" y="1106" font-family="Arial" font-size="16" fill="#536570">Visão parcial do mesmo modelo; entidades repetidas são a mesma tabela. FKs secundárias constam no dicionário.</text></svg>')
        output=ROOT/f'DIAGRAMA_MER_{view["key"]}_MEDIARE.svg';output.write_text('\n'.join(parts));outputs.append(output)
    return outputs


def dictionary():
    model=json.loads(MODEL.read_text())
    rows=['| Tabela proposta | Campos principais e referências |','| --- | --- |']
    for name,fields in model['entities'].items():rows.append(f'| {name} | '+ '; '.join(fields)+' |')
    return '\n'.join(rows)


if __name__=='__main__':
    for path in build():print(path.name)
