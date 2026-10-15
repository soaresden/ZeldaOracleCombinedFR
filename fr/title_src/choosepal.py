import sys, itertools
from PIL import Image
im=Image.open(sys.argv[1]).convert('RGB')
def dist(a,b): return sum((x-y)**2 for x,y in zip(a,b))
tiles=[[im.getpixel((tx*8+x,ty*8+y)) for y in range(8) for x in range(8)] for ty in range(18) for tx in range(20)]
sets=[frozenset(t) for t in tiles]
maxi=[s for s in set(sets) if not any(s<t for t in set(sets))]
def tile_err(t,pal):
    return sum(min(dist(p,c) for c in pal) for p in t)
best=None
for combo in itertools.combinations(maxi,8):
    err=0
    for t,s in zip(tiles,sets):
        if any(s<=p for p in combo): continue
        err+=min(tile_err(t,p) for p in combo)
    if best is None or err<best[0]: best=(err,combo)
err,combo=best
print('erreur',err)
out=im.copy()
changed=0
for i,(t,s) in enumerate(zip(tiles,sets)):
    if any(s<=p for p in combo): continue
    p=min(combo,key=lambda p:tile_err(t,p))
    tx,ty=i%20,i//20; changed+=1
    for k,c in enumerate(t):
        out.putpixel((tx*8+k%8,ty*8+k//8),min(p,key=lambda q:dist(q,c)))
print('tuiles retouchées',changed)
for p in combo: print(sorted(p))
out.save(sys.argv[2]); out.resize((480,432),Image.NEAREST).save(sys.argv[2].replace('.png','_x3.png'))
