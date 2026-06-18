"""
Fast 2D ternary CA scanner — pure Python, optimized.
Uses flat arrays + precomputed neighbor indices to avoid
per-step modular arithmetic overhead.

Rule: outer totalistic — output = f(center, sum_of_8_neighbors)
center ∈ {-1,0,1},  sum ∈ {-8..+8}  → 3×17 = 51 params
"""

import math, random, time
from collections import Counter

N, Z, P = -1, 0, 1
TV = [N, Z, P]
random.seed(42)

# ── FAST STEP: precomputed neighbor table ──────────────────
def make_neighbor_table(H, W):
    """For each flat index i, list of 8 neighbor flat indices (with wrap)."""
    nb = []
    for y in range(H):
        for x in range(W):
            row = []
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    if dy==0 and dx==0: continue
                    row.append(((y+dy)%H)*W + (x+dx)%W)
            nb.append(row)
    return nb

def step_flat(flat, rule_flat, nb, size):
    """flat: list of size ints in {-1,0,1}. rule_flat[c+1][s+8]."""
    new = [0]*size
    for i in range(size):
        s = (flat[nb[i][0]] + flat[nb[i][1]] + flat[nb[i][2]] +
             flat[nb[i][3]] + flat[nb[i][4]] + flat[nb[i][5]] +
             flat[nb[i][6]] + flat[nb[i][7]])
        new[i] = rule_flat[flat[i]+1][s+8]
    return new

# ── RULE ENCODING ──────────────────────────────────────────
def make_rule():
    # rule[center+1][sum+8] → output
    return [[random.choice(TV) for _ in range(17)] for _ in range(3)]

def encode_rule(rule):
    n=0
    for row in rule:
        for v in row: n=n*3+(v+1)
    return n

def decode_rule_enc(n):
    rule=[[0]*17 for _ in range(3)]
    for i in range(2,-1,-1):
        for j in range(16,-1,-1):
            rule[i][j]=TV[n%3]; n//=3
    return rule

# ── INIT ───────────────────────────────────────────────────
def init_grid(H, W, density=0.15):
    return [random.choice([P,N]) if random.random()<density else Z
            for _ in range(H*W)]

def init_single(H, W):
    flat=[Z]*(H*W); flat[(H//2)*W+W//2]=P; return flat

# ── METRICS ───────────────────────────────────────────────
def entropy_flat(flat):
    n=len(flat); H=0.0
    for v in TV:
        c=flat.count(v)
        if c>0: p=c/n; H-=p*math.log2(p)
    return H

def hsh_flat(flat):
    h=2166136261
    for v in flat: h=((h^(v+1))*16777619)&0xFFFFFFFF
    return h

# ── SCAN SINGLE RULE ──────────────────────────────────────
H_SCAN=35; W_SCAN=35
NB_SCAN=make_neighbor_table(H_SCAN,W_SCAN)
SIZE_SCAN=H_SCAN*W_SCAN

def scan_rule(rule, nb=NB_SCAN, size=SIZE_SCAN, GENS=150):
    flat=init_grid(H_SCAN,W_SCAN,density=0.15)
    elog=[]; seen=set(); cycle=None
    for g in range(GENS):
        flat=step_flat(flat,rule,nb,size)
        He=round(entropy_flat(flat),4)
        elog.append(He)
        if cycle is None:
            h=hsh_flat(flat)
            if h in seen: cycle=g
            else: seen.add(h)
    tail=elog[-50:]
    tm=sum(tail)/len(tail); tv=sum((x-tm)**2 for x in tail)/len(tail)
    counts=[flat.count(v) for v in TV]
    mr=min(c/size for c in counts)
    s=0
    if 0.85<tm<1.25: s+=40
    elif 0.55<tm<1.4: s+=20
    if tv<0.005: s+=25
    elif tv<0.02: s+=15
    elif tv<0.08: s+=5
    if mr>0.12: s+=25
    elif mr>0.05: s+=12
    elif mr>0.01: s+=3
    else: s-=10
    if cycle is None: s+=10
    elif cycle>100: s+=5
    elif cycle<10: s-=20
    return {'H':round(tm,4),'var':round(tv,6),'score':max(0,s),
            'cycle':cycle,'min_ratio':round(mr,3),'elog':elog}

# ── GLIDER DETECTOR ──────────────────────────────────────
H_G=70; W_G=70
NB_G=make_neighbor_table(H_G,W_G)
SIZE_G=H_G*W_G

def find_gliders(rule, GENS=350, skip=40):
    flat=init_single(H_G,W_G)
    history=[flat[:]]
    for _ in range(GENS):
        flat=step_flat(flat,rule,NB_G,SIZE_G)
        history.append(flat[:])

    def clusters_at(g):
        flat_g=history[g]
        cells=[i for i in range(SIZE_G) if flat_g[i]!=Z]
        if not cells: return []
        parent={i:i for i in cells}
        cs=set(cells)
        def find(x):
            while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
            return x
        def union(a,b):
            a,b=find(a),find(b)
            if a!=b: parent[a]=b
        for i in cells:
            y,x=i//W_G,i%W_G
            for dy,dx in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                j=((y+dy)%H_G)*W_G+(x+dx)%W_G
                if j in cs: union(i,j)
        groups={}
        for i in cells: groups.setdefault(find(i),[]).append(i)
        return list(groups.values())

    def centroid(cl):
        ys=[i//W_G for i in cl]; xs=[i%W_G for i in cl]
        return sum(ys)/len(ys), sum(xs)/len(xs)

    tracks={}; nxt=0; finished=[]
    for g in range(skip,len(history)):
        cls=clusters_at(g)
        if not cls: tracks={}; continue
        main=max(cls,key=len)
        mcy,mcx=centroid(main)
        iso=[cl for cl in cls if cl is not main and
             math.hypot(centroid(cl)[0]-mcy,centroid(cl)[1]-mcx)>10]
        matched=set(); new={}
        for tid,trk in tracks.items():
            py,px=trk[-1]['cy'],trk[-1]['cx']
            best=None; bd=999
            for ic in iso:
                icy,icx=centroid(ic)
                d=math.hypot(icy-py,icx-px)
                if d<10 and d<bd: bd=d; best=ic
            if best and id(best) not in matched:
                matched.add(id(best))
                icy,icx=centroid(best)
                new[tid]=trk+[{'gen':g,'cy':icy,'cx':icx,'size':len(best)}]
            else:
                if len(trk)>=12: finished.append(trk)
        for ic in iso:
            if id(ic) not in matched:
                icy,icx=centroid(ic)
                new[nxt]=[{'gen':g,'cy':icy,'cx':icx,'size':len(ic)}]; nxt+=1
        tracks=new
    for trk in tracks.values():
        if len(trk)>=12: finished.append(trk)

    results=[]
    for trk in finished:
        n=len(trk)
        if n<8: continue
        gens=[t['gen'] for t in trk]; cys=[t['cy'] for t in trk]; cxs=[t['cx'] for t in trk]
        gm=sum(gens)/n; cym=sum(cys)/n; cxm=sum(cxs)/n
        dg=sum((g-gm)**2 for g in gens)
        if dg==0: continue
        vy=sum((gens[i]-gm)*(cys[i]-cym) for i in range(n))/dg
        vx=sum((gens[i]-gm)*(cxs[i]-cxm) for i in range(n))/dg
        speed=math.hypot(vy,vx)
        resid=sum(math.hypot(cys[i]-(cym+vy*(gens[i]-gm)),
                             cxs[i]-(cxm+vx*(gens[i]-gm)))**2 for i in range(n))/n
        if speed>0.05 and resid<6.0:
            results.append({'vy':round(vy,3),'vx':round(vx,3),
                            'speed':round(speed,3),'life':n,
                            'size':round(sum(t['size'] for t in trk)/n,1),
                            'resid':round(resid,2),'g0':gens[0],'g1':gens[-1]})
    return results

# ══════════════════════════════════════════════════════════
TOTAL=2000
t0=time.time()
print(f"Building neighbor tables... ", end='', flush=True)
print(f"done ({time.time()-t0:.1f}s)")
print(f"Scanning {TOTAL} rules × {H_SCAN}×{W_SCAN} × 150 gens...")

results=[]
for i in range(TOTAL):
    rule=make_rule()
    r=scan_rule(rule)
    r['rule']=rule; r['enc']=encode_rule(rule)
    results.append(r)
    if (i+1)%500==0:
        elapsed=time.time()-t0
        rate=(i+1)/elapsed
        eta=(TOTAL-i-1)/rate
        c4=sum(1 for x in results if x['score']>=70)
        print(f"  {i+1}/{TOTAL}  Class4: {c4}  {elapsed:.0f}s elapsed  ETA {eta:.0f}s")

results.sort(key=lambda r:r['score'],reverse=True)
elapsed=time.time()-t0
print(f"\nScan complete in {elapsed:.1f}s  ({TOTAL/elapsed:.0f} rules/s)")

dist=Counter()
for r in results:
    if r['H']<0.3: dist['Uniform']+=1
    elif r['H']<0.8: dist['Ordered']+=1
    elif r['H']<1.3: dist['Complex']+=1
    else: dist['Chaotic']+=1

print("\nCOMPLEXITY DISTRIBUTION")
print("─"*40)
for k in ['Uniform','Ordered','Complex','Chaotic']:
    v=dist[k]; bar='█'*(v//50)
    print(f"  {k:10} {v:5} ({v/TOTAL*100:5.1f}%)  {bar}")

class4=[r for r in results if r['score']>=70]
print(f"\nTOP RESULTS (score≥70): {len(class4)}")
print("─"*60)
for r in results[:20]:
    print(f"  score={r['score']:3}  H={r['H']:.4f}±{r['var']:.5f}  "
          f"min_r={r['min_ratio']}  cycle={str(r['cycle'] or 'none'):>6}  enc={r['enc']}")

# ── GLIDER SEARCH ─────────────────────────────────────────
top=[r for r in results if r['score']>=55][:25]
print(f"\n{'='*60}")
print(f"GLIDER SEARCH — top {len(top)} candidates (70×70 grid, 350 gens)")
print(f"{'='*60}")

glider_rules=[]
t1=time.time()
for i,r in enumerate(top):
    gliders=find_gliders(r['rule'])
    tag=f"[{i+1}/{len(top)}]"
    if gliders:
        glider_rules.append((r,gliders))
        print(f"\n{tag} ★ GLIDER — enc={r['enc']}  score={r['score']}")
        for g in gliders:
            ang=math.degrees(math.atan2(g['vy'],g['vx']))
            print(f"     vel=({g['vy']:+.3f},{g['vx']:+.3f}) spd={g['speed']:.3f} "
                  f"ang={ang:.0f}° life={g['life']}g sz≈{g['size']} res={g['resid']}")
    else:
        print(f"  {tag} enc={r['enc']}  score={r['score']} —")

print(f"\nGlider search: {time.time()-t1:.0f}s")
print(f"{'='*60}")

if glider_rules:
    print(f"\n★★★ FOUND {len(glider_rules)} RULES WITH 2D GLIDERS ★★★")
    for i,(r,gs) in enumerate(glider_rules):
        print(f"\n  [{i+1}] enc={r['enc']}  H={r['H']}  score={r['score']}")
        for g in gs:
            ang=math.degrees(math.atan2(g['vy'],g['vx']))
            print(f"       spd={g['speed']:.3f} ang={ang:.0f}° life={g['life']}g sz={g['size']}")
    print()
    best_r,best_gs=glider_rules[0]
    print("  BEST RULE TABLE (for visualizer):")
    print(f"  enc={best_r['enc']}")
    for i,row in enumerate(best_r['rule']):
        print(f"  {'NZP'[i]}: {row}")
    print()
    print("  → Add to index.html as a preset 2D rule")
    print("  → In 2D: gliders travel = wire = cascade solved geometrically")
else:
    print(f"\n  No gliders in top {len(top)}.")
    print(f"  Top 5 encodings for manual inspection:")
    for r in results[:5]:
        print(f"    enc={r['enc']}  H={r['H']}  score={r['score']}")
    print(f"\n  Next: broaden to score≥40 or increase GENS to 500")
