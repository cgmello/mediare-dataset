#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gerador de casos sintéticos de mediação — Mediare. Reproduzível (seed fixa)."""
import json, os, random, shutil

random.seed(42)
NOMES = ["A.S.M.","B.O.C.","C.R.F.","D.L.P.","E.T.V.","F.G.N.","H.J.B.","I.K.D.",
         "J.P.R.","L.M.A.","M.C.S.","N.F.O.","P.H.L.","R.A.T.","S.B.G.","T.V.M."]
EMPRESAS = ["Construtora Horizonte Ltda.","Móveis Planejados Aurora ME","AutoCenter Vitória Ltda.",
            "Refrigeração Polar ME","Eventos & Festas Jardim Ltda.","TecnoInfo Assistência Ltda.",
            "Transportes Rápido Sul ME","Marcenaria Bom Corte ME","Clínica Vet Amigo Fiel Ltda.",
            "Pinturas & Acabamentos Silva ME"]
CIDADES = ["São Paulo","Campinas","Santos","Sorocaba","Ribeirão Preto","São José dos Campos",
           "Bauru","Piracicaba","Jundiaí","Mogi das Cruzes"]

def par(): 
    a,b = random.sample(NOMES,2); return a,b

def dinheiro(lo,hi,step=100): return round(random.randrange(lo,hi,step),2)

def caso_cobranca():
    a=random.choice(EMPRESAS); b=random.choice(NOMES)
    men=random.choice([80,100,120,150,200]); qtd=random.randint(3,6); multa=men*2
    twist=random.choice(["claro","pagou_parte","sem_contrato_multa"])
    devido=men*qtd+multa; obs=[]
    if twist=="pagou_parte":
        pago=men; devido-=pago
        obs.append(f"requerida comprovou pagamento de 1 parcela (R$ {pago:.2f}) que deve ser abatida")
    if twist=="sem_contrato_multa":
        devido-=multa; multa=0
        obs.append("clausula de multa nao consta do contrato juntado - multa indevida")
    return dict(cat="cobranca-servicos",
      p1=f"""**Requerente:** {a}\n**Requerida:** {b}\n**Conflito:** cobrança de mensalidades de serviço contratado\n
## Fatos\nA requerida contratou nossos serviços por mensalidades de R$ {men:.2f}. Deixou de pagar {qtd} parcelas e nunca formalizou o cancelamento{', embora alegue ter pago uma das parcelas' if twist=='pagou_parte' else ''}. O contrato {'prevê' if multa else 'preveria'} multa de duas mensalidades pela rescisão sem aviso.\n
## Pedidos\n1. Parcelas em aberto: R$ {men*qtd:.2f}\n2. Multa contratual: R$ {men*2:.2f}""",
      d1=f"1. Contrato de prestação de serviços (mensalidade R$ {men:.2f}){' — SEM cláusula de multa legível' if twist=='sem_contrato_multa' else ' com cláusula de multa de 2 mensalidades'}.\n2. Boletos em aberto.\n3. Planilha do débito.",
      p2=f"""**Requerida:** {b}\n\nParei de usar o serviço e entendo nada dever após deixar de frequentar.{' Paguei uma das parcelas cobradas, tenho o comprovante.' if twist=='pagou_parte' else ''}{' A multa cobrada não está prevista no contrato que assinei.' if twist=='sem_contrato_multa' else ''} Não fiz cancelamento formal por desconhecimento.""",
      d2="1. Comprovantes de pagamentos anteriores." + ("\n2. Comprovante da parcela paga e cobrada indevidamente." if twist=="pagou_parte" else ""),
      gab=dict(responsavel="requerida",resultado="procedente" if twist=="claro" else "parcialmente procedente",
        valores={"total_devido":round(devido,2),"multa_contratual":float(multa)},
        pedidos_rejeitados=obs,
        fundamentos=["forca obrigatoria do contrato","ausencia de cancelamento formal mantem a obrigacao"]+obs))

def caso_locacao():
    a,b=par(); cau=dinheiro(3000,20000,500); mrec=dinheiro(2000,15000,500)
    twist=random.choice(["vicios_sem_vistoria","danos_com_vistoria","atraso_alugueis"])
    if twist=="vicios_sem_vistoria":
        gab=dict(responsavel="requerido_locador",resultado="procedente",
          valores={"devolucao_caucao":cau,"multa_contratual":mrec},
          fundamentos=["Lei 8.245/91 art. 22 - vicios anteriores a locacao","sem vistoria inicial nao ha prova de danos do locatario"])
        p1=f"Aluguei imóvel de {b} com caução de R$ {cau:.2f}. O imóvel apresentou vícios ocultos (infiltrações, mofo, fiação precária). Saí e ele reteve a caução. Peço devolução integral + multa contratual de R$ {mrec:.2f}."
        p2="O imóvel foi entregue em ordem; os danos são de mau uso. Retenho a caução legitimamente. (NÃO possuo laudo de vistoria inicial assinado.)"
    elif twist=="danos_com_vistoria":
        rep=dinheiro(1000,int(cau),100)
        gab=dict(responsavel="parcial_ambos",resultado="parcialmente procedente",
          valores={"devolucao_caucao":round(cau-rep,2),"retencao_reparos":rep},
          fundamentos=["vistoria inicial + final comprova danos alem do desgaste natural","retencao proporcional; saldo deve ser devolvido"])
        p1=f"Devolvi o imóvel de {b} e ele reteve TODA a caução de R$ {cau:.2f}. Aceito descontar pequenos reparos, mas a retenção integral é abusiva."
        p2=f"A vistoria de saída, comparada à de entrada (ambas assinadas), aponta danos de R$ {rep:.2f}. Retive a caução para cobri-los."
    else:
        atras=random.randint(2,4); alug=dinheiro(1200,4000,100); dev=alug*atras
        gab=dict(responsavel="requerido_locatario",resultado="procedente",
          valores={"alugueis_devidos":round(dev,2),"abatimento_caucao":min(cau,dev)},
          fundamentos=["inadimplencia incontroversa","caucao compensavel com o debito"])
        p1,p2=f"Sou locador; {b} deixou {atras} aluguéis de R$ {alug:.2f} em aberto antes de sair. Peço o débito, compensável com a caução de R$ {cau:.2f}.", "Atrasei por desemprego; peço abatimento da caução e parcelamento."
        a,b=b,a
    return dict(cat="locacao-caucao",
      p1=f"**Requerente:** {a}\n**Requerido:** {b}\n**Conflito:** locação residencial — caução\n\n## Fatos e pedidos\n{p1}",
      d1="1. Contrato de locação com cláusula de caução.\n2. Comprovante de pagamento da caução.\n3. Fotos do imóvel.\n4. Comprovante de devolução das chaves.",
      p2=f"**Requerido:** {b}\n\n{p2}",
      d2="1. Contrato (mesma via).\n2. Fotos após desocupação." + ("\n3. Laudos de vistoria inicial e final assinados." if twist=="danos_com_vistoria" else ""),
      gab=gab)

def caso_consumo():
    a=random.choice(NOMES); b=random.choice(EMPRESAS)
    prod=random.choice([("geladeira duplex",3500,9000),("sofá retrátil",2500,8000),
                        ("notebook",2800,7500),("piscina de fibra",15000,40000),("fogão de embutir",1800,5000)])
    val=dinheiro(prod[1],prod[2],100); twist=random.choice(["claro","fora_prazo_garantia","mau_uso_provado"])
    if twist=="claro":
        dm=dinheiro(1000,8000,500)
        gab=dict(responsavel="requerida_fornecedora",resultado="procedente",
          valores={"restituicao":val,"danos_morais":dm},
          fundamentos=["CDC art. 18 - vicio nao sanado em 30 dias","laudo confirma defeito de fabricacao"])
    elif twist=="fora_prazo_garantia":
        gab=dict(responsavel="requerida_fornecedora",resultado="parcialmente procedente",
          valores={"restituicao":val,"danos_morais":0.0},
          pedidos_rejeitados=["danos morais - mero aborrecimento"],
          fundamentos=["vicio oculto: prazo conta da descoberta (CDC art. 26 par.3)","restituicao devida; sem dano moral"])
    else:
        gab=dict(responsavel="requerente_consumidor",resultado="improcedente",
          valores={"restituicao":0.0,"danos_morais":0.0},
          fundamentos=["laudo tecnico da assistencia constatou mau uso (queda/liquido)","excludente de responsabilidade do fornecedor"])
    return dict(cat="consumo-produto",
      p1=f"**Requerente:** {a}\n**Requerida:** {b}\n**Conflito:** vício do produto\n\n## Fatos\nComprei um(a) {prod[0]} por R$ {val:.2f}. Apresentou defeito {'logo após a compra' if twist!='fora_prazo_garantia' else 'meses depois — vício oculto'} e a loja não resolveu em 30 dias.\n\n## Pedidos\n1. Restituição: R$ {val:.2f}\n2. Danos morais.",
      d1="1. Nota fiscal.\n2. Fotos/vídeos do defeito.\n3. Protocolos de reclamação e ordens de serviço.",
      p2=f"**Requerida:** {b}\n\n"+("O produto saiu conforme; o defeito alegado não foi reproduzido integralmente em bancada."
         if twist=="claro" else "A reclamação veio fora do prazo de garantia contratual." if twist=="fora_prazo_garantia"
         else "O laudo da assistência constatou sinais claros de mau uso (queda e ingresso de líquido), excluindo a garantia."),
      d2="1. Laudo da assistência técnica."+("\n2. Fotos do dano físico por mau uso." if twist=="mau_uso_provado" else ""),
      gab=gab)

def caso_transito():
    a,b=par(); rep=dinheiro(2000,25000,250)
    twist=random.choice(["traseira","lucros_sem_prova","concorrente"])
    if twist=="traseira":
        gab=dict(responsavel="requerido",resultado="procedente",valores={"danos_materiais":rep},
          fundamentos=["presuncao de culpa na colisao traseira (CTB art. 29 II)","menor orcamento deferido"])
        extra=""
    elif twist=="lucros_sem_prova":
        lc=dinheiro(2000,12000,100)
        gab=dict(responsavel="requerido",resultado="parcialmente procedente",
          valores={"danos_materiais":rep,"lucros_cessantes":0.0},
          pedidos_rejeitados=[f"lucros cessantes de R$ {lc:.2f} - sem prova do prejuizo liquido"],
          fundamentos=["culpa do requerido comprovada","lucros cessantes exigem prova efetiva, nao estimativa"])
        extra=f"\n2. Lucros cessantes (uso profissional do veículo): R$ {lc:.2f}"
    else:
        gab=dict(responsavel="ambos_culpa_concorrente",resultado="parcialmente procedente",
          valores={"danos_materiais":round(rep/2,2)},
          fundamentos=["conversao irregular do requerido + velocidade incompativel do requerente","reparticao 50/50 dos danos"])
        extra=""
    return dict(cat="transito",
      p1=f"**Requerente:** {a}\n**Requerido:** {b}\n**Conflito:** acidente de trânsito — danos materiais\n\n## Fatos\nEm via urbana de {random.choice(CIDADES)}, meu veículo foi atingido pelo do requerido ({'colisão traseira' if twist!='concorrente' else 'colisão em cruzamento durante conversão'}).\n\n## Pedidos\n1. Reparos (menor orçamento): R$ {rep:.2f}{extra}",
      d1="1. Boletim de ocorrência com croqui.\n2. Fotos dos danos e do local.\n3. Três orçamentos de reparo.",
      p2=f"**Requerido:** {b}\n\n"+("Houve parada brusca injustificada do requerente." if twist=="traseira"
         else "Reconheço a colisão, mas os lucros cessantes são estimativa sem comprovação contábil." if twist=="lucros_sem_prova"
         else "O requerente vinha em velocidade incompatível; a culpa é no mínimo concorrente."),
      d2="1. Fotos do próprio veículo.\n2. Versão registrada no BO.",
      gab=gab)

def caso_reforma():
    a,b=random.choice(NOMES),random.choice(EMPRESAS); tot=dinheiro(8000,80000,500)
    twist=random.choice(["abandono","vicios","concorrente"])
    if twist=="abandono":
        pago=round(tot*random.choice([0.4,0.5,0.6]),2); exec_=round(pago*random.choice([0.3,0.5]),2)
        gab=dict(responsavel="requerida_empreiteira",resultado="procedente",
          valores={"restituicao":round(pago-exec_,2),"multa_contratual":round(tot*0.1,2)},
          fundamentos=["abandono injustificado da obra","restituicao do pago menos servicos efetivamente executados"])
        rel=f"Contratei reforma por R$ {tot:.2f}, paguei R$ {pago:.2f} adiantado e a empresa abandonou a obra com fração executada."
        resp="Paralisamos por falta de pagamento de extras verbais (sem aditivo escrito)."
    elif twist=="vicios":
        rep=dinheiro(3000,int(tot),250)
        gab=dict(responsavel="requerida_empreiteira",resultado="procedente",
          valores={"custo_reparos":rep},
          fundamentos=["vicios construtivos comprovados por laudo","responsabilidade do empreiteiro pela solidez e perfeicao (CC art. 618)"])
        rel=f"A reforma de R$ {tot:.2f} foi entregue com infiltrações e trincas; laudo aponta má execução. Reparos: R$ {rep:.2f}."
        resp="A obra seguiu o projeto; problemas decorrem de manutenção inadequada posterior."
    else:
        rep=dinheiro(4000,int(tot),250)
        gab=dict(responsavel="ambos_culpa_concorrente",resultado="parcialmente procedente",
          valores={"custo_reparos_total":rep,"quota_empreiteira_50pct":round(rep/2,2)},
          fundamentos=["falha de impermeabilizacao do empreiteiro","alteracoes feitas pelo dono apos a entrega contribuiram para o dano"])
        rel=f"Reforma de R$ {tot:.2f} entregue; surgiram infiltrações. Reparos orçados em R$ {rep:.2f}."
        resp="Após a entrega o proprietário alterou a drenagem/acabamento por estética, agravando o problema."
    return dict(cat="reforma-empreitada",
      p1=f"**Requerente:** {a}\n**Requerida:** {b}\n**Conflito:** empreitada de reforma residencial\n\n## Fatos e pedidos\n{rel}",
      d1="1. Contrato de empreitada e comprovantes de pagamento.\n2. Fotos da obra.\n3. Orçamentos/laudo de reparação.",
      p2=f"**Requerida:** {b}\n\n{resp}",
      d2="1. Contrato (mesma via).\n2. Registro fotográfico da entrega.\n3. Mensagens trocadas.",
      gab=gab)

def caso_vizinhanca():
    a,b=par()
    twist=random.choice(["obra_do_reu","defeito_proprio","barulho"])
    if twist=="obra_do_reu":
        rep=dinheiro(2000,15000,250)
        gab=dict(responsavel="requerido",resultado="procedente",
          valores={"danos_materiais":rep},
          obrigacoes_de_fazer={"impermeabilizar_e_drenar":True,"prazo_dias":60,"multa_diaria":200.0},
          fundamentos=["obra do requerido alterou escoamento das aguas","laudo confirma nexo causal"])
        rel=f"A obra/aterro do vizinho desviou as águas de chuva contra minha parede: infiltrações e mofo. Gastei R$ {rep:.2f} em reparos."
        resp="Minha obra foi regular; a casa da requerente é antiga e mal conservada."
    elif twist=="defeito_proprio":
        rep=dinheiro(2000,12000,250)
        gab=dict(responsavel="parcial_ambos",resultado="parcialmente procedente",
          valores={"danos_materiais":0.0},
          obrigacoes_de_fazer={"impermeabilizar_e_drenar":True,"prazo_dias":60,"multa_diaria":200.0},
          pedidos_rejeitados=[f"ressarcimento de R$ {rep:.2f} - infiltracao interna decorre de defeito da propria requerente"],
          fundamentos=["requerido deve conter/drenar seu terreno elevado","danos internos tem causa em impermeabilizacao propria deficiente"])
        rel=f"O aterro do vizinho joga água na minha divisa. Gastei R$ {rep:.2f} em reformas internas e quero ressarcimento + drenagem."
        resp="A parede dela não tem impermeabilização própria; os danos internos são da construção dela. Farei drenagem se preciso."
    else:
        dm=dinheiro(1000,6000,500)
        gab=dict(responsavel="requerido",resultado="parcialmente procedente",
          valores={"danos_morais":dm},
          obrigacoes_de_fazer={"cessar_ruido_apos_22h":True,"multa_por_evento":300.0},
          fundamentos=["perturbacao reiterada do sossego comprovada (videos, BOs)","dano moral pela reiteracao; valor moderado"])
        rel="O vizinho promove festas com som alto até de madrugada, várias vezes por semana. Tenho vídeos e boletins de ocorrência."
        resp="As reuniões são esporádicas e dentro de horários razoáveis; há exagero da requerente."
    return dict(cat="vizinhanca",
      p1=f"**Requerente:** {a}\n**Requerido:** {b}\n**Conflito:** direito de vizinhança\n\n## Fatos e pedidos\n{rel}",
      d1="1. Fotos/vídeos.\n2. Laudo/orçamentos (quando aplicável).\n3. Boletins de ocorrência / atas de condomínio.",
      p2=f"**Requerido:** {b}\n\n{resp}",
      d2="1. Fotos da própria obra/imóvel.\n2. Testemunhos de outros vizinhos.",
      gab=gab)

def caso_condominio():
    a="Condomínio Edifício "+random.choice(["Primavera","Alvorada","Solar das Acácias","Monte Verde"]); b=random.choice(NOMES)
    cota=dinheiro(300,1500,50); qtd=random.randint(3,10); twist=random.choice(["claro","pagou_algumas"])
    dev=cota*qtd; obs=[]
    if twist=="pagou_algumas":
        pag=random.randint(1,2); dev-=cota*pag
        obs.append(f"{pag} cota(s) comprovadamente paga(s) devem ser excluidas")
    return dict(cat="condominio",
      p1=f"**Requerente:** {a}\n**Requerido:** {b} (unidade {random.randint(11,158)})\n**Conflito:** cobrança de cotas condominiais\n\n## Fatos\nO requerido acumulou {qtd} cotas de R$ {cota:.2f}. Pedimos o principal com multa de 2% e juros de 1% a.m.",
      d1="1. Convenção do condomínio.\n2. Demonstrativo do débito por competência.\n3. Atas de assembleia fixando a cota.",
      p2=f"**Requerido:** {b}\n\nPassei por dificuldades financeiras."+(" Algumas das cotas cobradas EU JÁ PAGUEI — segue comprovante." if twist=="pagou_algumas" else "")+" Peço parcelamento e isenção da multa.",
      d2="1. Comprovantes de pagamento parcial." if twist=="pagou_algumas" else "1. (sem documentos)",
      gab=dict(responsavel="requerido",resultado="procedente" if twist=="claro" else "parcialmente procedente",
        valores={"principal":round(dev,2),"multa_2pct":round(dev*0.02,2)},
        pedidos_rejeitados=obs,
        fundamentos=["obrigacao propter rem do condomino","multa limitada a 2% (CC art. 1.336 par.1)"]+obs))

def caso_veiculo():
    a,b=par(); val=dinheiro(15000,80000,500)
    twist=random.choice(["vicio_oculto","desgaste_natural"])
    if twist=="vicio_oculto":
        rep=dinheiro(2000,15000,250)
        gab=dict(responsavel="requerido_vendedor",resultado="procedente",
          valores={"abatimento_ou_reparo":rep},
          fundamentos=["vicio oculto preexistente (motor retificado ocultado) - CC art. 441","laudo mecanico comprova anterioridade"])
        rel=f"Comprei de {b} um carro usado por R$ {val:.2f}. Dias depois, o motor falhou: laudo aponta retífica antiga ocultada. Reparo: R$ {rep:.2f}."
        resp="Vendi o carro no estado, com test-drive livre; nunca soube de retífica."
    else:
        gab=dict(responsavel="requerente_comprador",resultado="improcedente",
          valores={"indenizacao":0.0},
          fundamentos=["desgaste natural compativel com idade/km do veiculo","venda entre particulares no estado, sem garantia"])
        rel=f"Comprei de {b} um usado por R$ {val:.2f}; a embreagem gastou 3 meses depois. Quero o conserto."
        resp=f"Veículo com {random.randint(80,180)} mil km, vendido no estado; embreagem é item de desgaste."
    return dict(cat="venda-veiculo",
      p1=f"**Requerente:** {a}\n**Requerido:** {b}\n**Conflito:** compra e venda de veículo usado entre particulares\n\n## Fatos e pedidos\n{rel}",
      d1="1. Recibo/CRV de compra e venda.\n2. Laudo mecânico.\n3. Orçamentos de reparo.\n4. Anúncio da venda.",
      p2=f"**Requerido:** {b}\n\n{resp}",
      d2="1. Anúncio com a quilometragem.\n2. Mensagens da negociação.",
      gab=gab)

GERADORES=[caso_cobranca,caso_locacao,caso_consumo,caso_transito,caso_reforma,caso_vizinhanca,caso_condominio,caso_veiculo]

def main(n=300, outdir="casos_sinteticos"):
    if os.path.exists(outdir): shutil.rmtree(outdir)
    os.makedirs(outdir)
    for i in range(1,n+1):
        c=random.choice(GERADORES)()
        d=f"{outdir}/caso_sint_{i:03d}"
        os.makedirs(d)
        open(f"{d}/README.md","w").write(f"# Caso sintético {i:03d} — {c['cat']}\n\nGerado artificialmente (sem dados pessoais reais) para teste do comitê de IA da Mediare.\nInspirado em padrões de sentenças públicas do TJSP.\n")
        open(f"{d}/01_peticao_requerente.md","w").write("# Pedido de mediação — Parte Requerente\n\n"+c["p1"]+"\n")
        open(f"{d}/02_documentos_requerente.md","w").write("# Documentos comprobatórios — Requerente\n\n"+c["d1"]+"\n")
        open(f"{d}/03_resposta_requerido.md","w").write("# Resposta da Parte Requerida\n\n"+c["p2"]+"\n")
        open(f"{d}/04_documentos_requerido.md","w").write("# Documentos comprobatórios — Requerida\n\n"+c["d2"]+"\n")
        gab={"caso":f"sint-{i:03d}-{c['cat']}","fonte":"sintetico-mediare-v1 (seed 42)",
             "parecer_esperado":c["gab"],
             "criterios_equivalencia_sugeridos":{"responsavel":"match exato","valores":"tolerancia +/- 15% por rubrica; rubricas negadas = 0","fundamentos":"minimo 2 fundamentos centrais em comum"}}
        json.dump(gab,open(f"{d}/gabarito.json","w"),ensure_ascii=False,indent=2)
    # índice
    import collections
    cnt=collections.Counter()
    for i in range(1,n+1):
        g=json.load(open(f"{outdir}/caso_sint_{i:03d}/gabarito.json"))
        cnt[g["caso"].split("-",2)[2]]+=1
    open(f"{outdir}/INDICE.md","w").write("# Distribuição por categoria\n\n"+"\n".join(f"- {k}: {v}" for k,v in sorted(cnt.items()))+f"\n\nTotal: {n} casos\n")
    print(dict(cnt)); print("total:",n)

if __name__=="__main__": main(319)
