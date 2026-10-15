import sys, itertools
from collections import Counter
from PIL import Image
im=Image.open(sys.argv[1]).convert('RGB')
def dist(a,b): return sum((x-y)**2 for x,y in zip(a,b))
# 1) réduire à 4 couleurs les tuiles qui débordent
for ty in range(18):
    for tx in range(20):
        px=[(x,y) for y in range(ty*8,ty*8+8) for x in range(tx*8,tx*8+8)]
        cnt=Counter(im.getpixel(p) for p in px)
        while len(cnt)>4:
            rare=min(cnt,key=cnt.get)
            near=min((c for c in cnt if c!=rare),key=lambda c:dist(c,rare))
            for p in px:
                if im.getpixel(p)==rare: im.putpixel(p,near)
            cnt=Counter(im.getpixel(p) for p in px)
im.save(sys.argv[2])
sets=[frozenset(im.getpixel((tx*8+x,ty*8+y)) for y in range(8) for x in range(8)) for ty in range(18) for tx in range(20)]
maxi=[s for s in set(sets) if not any(s<t for t in set(sets))]
print('ensembles maximaux',len(maxi))
for s in sorted(maxi,key=lambda s:sorted(s)): print(sorted(s))
