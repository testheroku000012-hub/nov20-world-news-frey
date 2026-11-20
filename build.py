from weasyprint import HTML
from PIL import Image, ImageChops, ImageFont
from pathlib import Path
import html, subprocess, tempfile, re
W=H=1024; PAPER='#f5f0e6'; NAVY='#10233b'; RED='#d44735'; GOLD='#e4b84a'; INK='#111820'; BLUE='#d8e6ed'
texts=[]
def esc(s): return html.escape(s)
def rect(x,y,w,h,fill,stroke='none',sw=1,rx=0): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="{rx}"/>'
def tx(x,y,s,size=12,fill=INK,weight=400,anchor='start',family='Arial',panel=None):
    svg = f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}px" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{esc(s)}</text>'
    if panel is None:
        panel=(0,0,1024,1024)
        if 325 <= y <= 499:
            panel=next((hx,325,hw,174) for hx,hw in [(38,300),(356,300),(674,312)] if hx <= x <= hx+hw)
        elif x >= 682 and 528 <= y <= 702: panel=(682,528,304,174)
        elif x >= 682 and 712 <= y <= 820: panel=(682,712,304,108)
    texts.append(dict(x=x,y=y,s=s,svg=svg,panel=panel))
    return svg
def line(x,y,s,size,fill=INK,weight=400,panel=None): return tx(x,y,s,size,fill,weight,panel=panel)
def card(x,y,num,tag,title,body,color=RED):
    p=(x,y,300,40); return rect(x,y,300,40,'#fffdf8','#c9c0b1',1,5)+rect(x,y,6,40,color)+tx(x+14,y+12,f'{num:02d} · {tag}',8,color,700,panel=p)+tx(x+14,y+24,title,10,INK,700,panel=p)+tx(x+14,y+34,body,8,INK,700,panel=p)
def brief(x,y,num,city,deck,tag):
    p=(x,y,458,20)
    label=f'{num:02d} · {city}'
    font=ImageFont.truetype('/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf',40)
    label_end=x+4+font.getlength(label)/4
    deck_x=label_end+12 if label_end+4 > x+90 else x+90
    return tx(x+4,y+13,label,10,RED,700,panel=p)+tx(deck_x,y+13,f'{deck} · {tag}',9,INK,700,panel=p)
def build_svg():
    global texts; texts=[]; a=[rect(0,0,W,H,PAPER)]
    a += [tx(38,34,'THE WORLD IN ONE DAY',15,RED,700),tx(38,91,'Friday 20 November 2026',53,NAVY,700,family='Georgia'),tx(39,119,'A FRONT PAGE OF WHAT MOVED · 03:15 UTC EDITION',13,NAVY,700),rect(38,133,948,3,NAVY)]
    stats=[('NIKKEI','−4.5%'),('KOSPI','−4.7%'),('S&P 500','−2.02%'),('DOW','−2.2%'),('NASDAQ','−2.3%'),('USD/JPY','~159')]
    for i,(k,v) in enumerate(stats):
        x=38+i*158; a += [tx(x,160,k,11,NAVY,700),tx(x,184,v,24,RED,700),rect(x,194,140,2,GOLD)]
    a += [tx(38,218,'FRIDAY TIMELINE · UTC',11,NAVY,700)]
    events=[('00:00','Asia opens in rout'),('01:30','Nikkei below 57,000'),('03:00','Riyadh strike claimed'),('05:00','Wall Street selloff'),('08:00','BepiColombo images'),('15:05','Dragon departs ISS')]
    for i,(t,l) in enumerate(events):
        x=38+i*158; a += [tx(x,239,t,11,RED,700),tx(x,258,l,10,INK,700),rect(x+30,277,100,2,'#b9c7cc')]
    a += [tx(38,310,'THE THREE BIG MOVES',12,NAVY,700)]
    heroes=[(38,325,300,'01 / ASIA ROUT','NIKKEI −4.5%','Asia stocks suffered their worst week since 2020 as AI shares reversed.','REPORTED · Reuters / investinglive','#e5edf0','↓'),(356,325,300,'02 / WALL STREET','SELL THE AI DREAM?','S&P 500 −2.02%; Nasdaq swung from +2% to −2%.','REPORTED · Reuters','#f3e5dc','$'),(674,325,312,'03 / ANTHROPIC IPO','ANTHROPIC +17%','Debut near $97 versus $83 IPO price; $81.3B raised.','REPORTED · AFP / NYT / Reuters','#efe2d1','✦')]
    for x,y,w,tag,title,body,src,bg,icon in heroes:
        a += [rect(x,y,w,174,bg,NAVY,1,8),tx(x+16,y+24,tag,11,RED,700),rect(x+w-54,y+9,38,32,NAVY,'none',0,7),tx(x+w-35,y+32,icon,19,GOLD,700,'middle'),tx(x+16,y+61,title,22,NAVY,700,family='Georgia'),''.join(tx(x+16,y+91+j*15,b,11,INK,700,panel=(x,y,w,174)) for j,b in enumerate(([body.split(' as AI')[0],'as AI shares reversed.'] if tag.startswith('01') else [body]))),tx(x+16,y+153,src,9,NAVY,700)]
    a += [tx(38,518,'WHAT ELSE MOVED · NUMBERED STORIES',12,NAVY,700),tx(682,518,'THE WORLD AT A GLANCE',12,NAVY,700)]
    cards=[('DIPLOMACY','KUSHNER: ARTICLE 5','Russia comfortable with guarantees.'),('DIPLOMACY','TAKAICHI HOLDS LINE','Japan Taiwan stance unchanged.'),('CONFLICT','GROUNDED IN GAZA','Ground operation forces displacement.'),('SECURITY','HOUTHI WARNING','Investors told to leave Saudi Arabia.'),('ECONOMY','$1T EXPORT MILESTONE','South Korea exports top $1T.'),('ECONOMY','CITI MISBOOKED TRADES','European risk understated by $35B.'),('US','IOWA DELAYED','68 barrels cleanup postponed.'),('US','PETE ROSE PARDONED',"Trump's posthumous pardon announced Thu Nov 19."),('SCIENCE','MERCURY IN VIEW','BepiColombo takes first images.'),('SCIENCE','HOMO ERECTUS IN CHINA','Guangxi teeth reveal rainforest mastery.')]
    for i,(tag,title,body) in enumerate(cards): a.append(card(38+(i%2)*316,528+(i//2)*42,i+4,tag,title,body,[RED,RED,RED,RED,GOLD,GOLD,BLUE,BLUE,BLUE,GOLD][i]))
    # map and markets, both fully within their panels
    a += [rect(682,528,304,174,'#dce8e8',NAVY,1,6),tx(698,549,'PINS · STORY LOCATIONS',11,NAVY,700)]
    # Hand-drawn continent silhouettes; no external map assets or build inputs.
    continents={
        'NORTH AMERICA':[(701,568),(715,560),(741,560),(752,568),(746,578),(739,581),(735,592),(728,599),(727,608),(718,600),(714,588),(704,585)],
        'SOUTH AMERICA':[(728,608),(741,609),(750,619),(747,633),(740,644),(735,662),(729,650),(726,633),(721,619)],
        'EUROPE':[(797,576),(804,565),(817,561),(821,568),(836,570),(838,581),(828,588),(819,591),(814,585),(805,589),(800,584)],
        'AFRICA':[(798,594),(815,590),(830,596),(840,607),(834,620),(824,637),(815,645),(805,631),(803,615),(794,606)],
        'ASIA':[(839,570),(857,559),(882,560),(898,564),(918,560),(945,569),(962,580),(948,587),(940,600),(924,603),(926,617),(913,620),(903,605),(891,607),(884,620),(873,610),(864,598),(852,602),(836,591)],
        'OCEANIA':[(922,638),(938,630),(954,633),(962,645),(957,655),(938,656),(925,650)],
    }
    for polygon in continents.values():
        a.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in polygon)+'" fill="#b5c9c8" stroke="#789494" stroke-width="0.8"/>')
    # Terrestrial anchors only: Mercury (12) has no continent and is not pinned.
    # Broad-region positions separate labels at this scale; they are not city coordinates.
    pins=[(934,591,'01','ASIA'),(716,575,'02','NORTH AMERICA'),
          (729,575,'03','NORTH AMERICA'),(830,578,'04','EUROPE'),
          (946,578,'05','ASIA'),(846,587,'06','ASIA'),
          (858,594,'07','ASIA'),(921,578,'08','ASIA'),
          (806,579,'09','EUROPE'),(716,589,'10','NORTH AMERICA'),
          (732,590,'11','NORTH AMERICA'),(910,595,'13','ASIA')]
    def inside(point, polygon):
        x,y=point; result=False
        for (ax,ay),(bx,by) in zip(polygon,polygon[1:]+polygon[:1]):
            if (ay>y)!=(by>y) and x < (bx-ax)*(y-ay)/(by-ay)+ax:
                result=not result
        return result
    counts={}
    for x,y,n,continent in pins:
        assert inside((x,y),continents[continent]), ('PIN_OUTSIDE',n,continent)
        counts[continent]=counts.get(continent,0)+1
        a += [f'<circle cx="{x}" cy="{y}" r="6" fill="{PAPER}" stroke="{RED}" stroke-width="0.8"/>',tx(x,y+2.5,n,7,NAVY,700,'middle')]
    assert len({n for _,_,n,_ in pins})==12
    print('MAP_PIN_CHECK: PASS',counts,'; 12 Mercury unpinned (off Earth)')
    a += [tx(698,682,'Red numbers mark stories 1–13',9,INK,700),
          tx(698,694,f'ASIA {counts.get("ASIA",0)} · EUROPE {counts.get("EUROPE",0)} · AMERICAS {counts.get("NORTH AMERICA",0)+counts.get("SOUTH AMERICA",0)} · 12 OFF EARTH',8,INK,700)]
    a += [rect(682,712,304,108,NAVY,'none',0,6),tx(698,733,'MARKETS · THE DAY IN NUMBERS',10,GOLD,700),tx(698,751,'MSCI Asia-Pacific −2.5% · SoftBank −15%',9,PAPER,700),tx(698,767,'Advantest −10% · Samsung/SK Hynix −5–6%',9,PAPER,700),tx(698,783,'Oil flat · Japan CPI +0.8%',9,PAPER,700),tx(698,805,'REPORTED · story list receipts',8,'#b9d2d5',700)]
    a += [tx(38,825,'MORE BRIEFS · 14–25',12,NAVY,700)]
    briefs=[('KYIV','Projectile near Dutch embassy; minor damage','REPORTED'),('WASHINGTON','Senate rejects Iran war powers 51–48','REPORTED'),('SHENZHEN','APEC adopts Outlook on trade, data and AI','REPORTED'),('AKVAN','Cyclone landfall expected Friday','FORECAST'),('TAIPEI','Short selling limits take effect today','REPORTED'),('MOON','Potatoes grown in simulated moon soil, safe to eat','REPORTED'),('TOKYO','Consumer prices rise 0.8% in October','REPORTED'),('HORMUZ','Tanker disruptions offset oversupply','REPORTED'),('PORT-AU-PRINCE','Police say 34 gang members killed','REPORTED'),('CINCINNATI',"Fiona the hippo dies after eating a child's hat",'REPORTED'),('CERN','Collider taken apart to fit new magnets','REPORTED'),('ISS','Dragon departs at 15:05 UTC','FORECAST')]
    for i,(city,d,tag) in enumerate(briefs): a.append(brief(38+(i%2)*474,835+(i//2)*16,i+14,city,d,tag))
    a += [rect(38,932,948,2,NAVY),tx(38,956,'DATE CHECK · 20 NOV 2026 · six receipts: Nikkei · Riyadh · Anthropic · Mercury · Dragon · exports',9,NAVY,700),tx(986,978,'SOURCES: Reuters · AFP · NYT · AP · NASA · ESA-JAXA · Guardian · Al Jazeera · BBC',8,NAVY,700,'end')]
    # Isolate every text node through the SAME SVG/WeasyPrint/Poppler path.
    # 4x raster ink bounds account for real glyphs, anchors and font fallback;
    # isolation prevents later boxes or text from hiding overflow in the check.
    with tempfile.TemporaryDirectory() as scratch:
        pages=[]
        for t in texts:
            node=t['svg'].replace(f'y="{t["y"]}"', 'y="60"', 1)
            pages.append('<div><svg xmlns="http://www.w3.org/2000/svg" width="2048" height="80">'+node+'</svg></div>')
        doc='<style>@page{size:2048px 80px;margin:0}body{margin:0}div{height:80px;break-after:page}</style>'+''.join(pages)
        HTML(string=doc).write_pdf(scratch+'/text.pdf')
        subprocess.run(['pdftoppm','-png','-r','384',scratch+'/text.pdf',scratch+'/text'],check=True)
        files=sorted(Path(scratch).glob('text-*.png'))
        assert len(files)==len(texts), (len(files),len(texts))
        for t,file in zip(texts,files):
            im=Image.open(file).convert('RGB')
            box=ImageChops.difference(im,Image.new('RGB',im.size,'white')).getbbox()
            assert box, t['s']
            l,top,r,bottom=box
            bbox=(l/4,top/4+t['y']-60,r/4,bottom/4+t['y']-60)
            t['bbox']=bbox
            px,py,pw,ph=t['panel']
            assert bbox[0]>=px+4 and bbox[1]>=py+4 and bbox[2]<=px+pw-4 and bbox[3]<=py+ph-4, ('TEXT_FIT',t['s'],bbox,t['panel'])
    brief_lines=[t for t in texts if t['panel'][2:]==(458,20)]
    for city,deck in zip(brief_lines[::2],brief_lines[1::2]):
        assert city['bbox'][2]+4<=deck['bbox'][0], ('BRIEF_GAP',city,deck)
        if True:  # Print all 12 measured brief gaps for v2e QA.
            print('MEASURED',city['s'],city['bbox'],'deck',deck['bbox'],'gap',round(deck['bbox'][0]-city['bbox'][2],2))
    for t in texts:
        if t['s'].startswith(('Asia stocks','as AI shares reversed.', 'PETE ROSE PARDONED', "Trump's posthumous pardon")): print('MEASURED HERO 1',t['s'],t['bbox'])
    print(f'TEXT_FIT_CHECK: PASS ({len(texts)} rendered ink bboxes; 4px container padding; all hero bodies; all 12 brief pairs, gaps >=4px; repaired gaps 12px)')
    print('LAYOUT_CHECK: PASS (10 cards, 12 briefs, map/markets/date panels, timeline inside page)')
    return '<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">'+''.join(a)+'</svg>'
html_doc='<!doctype html><html><head><style>@page{size:1024px 1024px;margin:0}html,body{margin:0;width:1024px;height:1024px;background:#f5f0e6}</style></head><body>'+build_svg()+'</body></html>'
Path('newspaper.html').write_text(html_doc); HTML(string=html_doc).write_pdf('render.pdf'); subprocess.run(['pdftoppm','-png','-r','96','-singlefile','render.pdf','render-hi'],check=True)
im=Image.open('render-hi.png').convert('RGB'); assert im.size==(1024,1024); im.save('entry.png',optimize=True)
