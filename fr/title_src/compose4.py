import sys
from PIL import Image
A=Image.open('ages_bg.png').convert('RGB'); S=Image.open('seas_bg.png').convert('RGB')
W,H=160,144
bgA={(240,104,0),(248,128,24),(248,160,72),(248,200,128)}
bgS={(80,144,248),(128,176,248),(176,208,248),(240,240,248)}
SOLID_A=(240,104,0); SOLID_S=(80,144,248)
# couleurs quasi identiques fusionnées
MERGE={(232,248,248):(224,240,248),(248,248,232):(224,240,248),(112,104,32):(112,96,32),(184,96,0):(192,112,0)}
def right_t(tx,ty): return (tx*8+4) + (ty*8+4-72)*0.6 > 80
BAN=(37,85,124,106)          # bandeau seul (sans les tiges)
AG=(13,85); SE=(69,109)
bg=Image.new('RGB',(W,H)); draw={}
for y in range(H):
    for x in range(W):
        r=right_t(x//8,y//8); src,bset,solid=(S,bgS,SOLID_S) if r else (A,bgA,SOLID_A)
        p=src.getpixel((x,y))
        bg.putpixel((x,y), p if p in bset and not (30<=x<130 and 76<=y<112) else solid)
for y in range(85):            # logo d'Ages (avec la tige du haut)
    for x in range(W):
        p=A.getpixel((x,y))
        if p not in bgA: draw[(x,y)]=p
for (src,bset),(ox,oy) in (((A,bgA),AG),((S,bgS),SE)):
    for y in range(BAN[1],BAN[3]):
        for x in range(BAN[0],BAN[2]):
            p=src.getpixel((x,y))
            if p not in bset: draw[(x-BAN[0]+ox,y-BAN[1]+oy)]=p
for y in range(128,136):       # copyright descendu d'une rangée
    for x in range(W):
        r=right_t(x//8,(y+8)//8); src,bset=(S,bgS) if r else (A,bgA)
        p=src.getpixel((x,y))
        if p not in bset: draw[(x,y+8)]=p
out=Image.new('RGB',(W,H))
for ty in range(18):
    for tx in range(20):
        has=any((tx*8+x,ty*8+y) in draw for y in range(8) for x in range(8))
        solid=SOLID_S if right_t(tx,ty) else SOLID_A
        for y in range(ty*8,ty*8+8):
            for x in range(tx*8,tx*8+8):
                p=draw.get((x,y)) or (solid if has else bg.getpixel((x,y)))
                out.putpixel((x,y),MERGE.get(p,p))
out.save('title_v4.png'); out.resize((480,432),Image.NEAREST).save('title_v4_x3.png')
