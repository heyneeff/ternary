import random, math
from collections import defaultdict

N, Z, P = -1, 0, 1
TV = [N, Z, P]

def enc(l,c,r): return (l+1)*9+(c+1)*3+(r+1)

def make_rule(): return [random.choice(TV) for _ in range(27)]

def encode_rule(rule):
    n = 0
    for i in range(26,-1,-1): n = n*3 + (rule[i]+1)
    return n

def to_base3(n):
    if n==0: return '0'*27
    d=[]
    x=n
    while x: d.append(str(x%3)); x//=3
    return ''.join(reversed(d)).zfill(27)

def step(cells, rule):
    L=len(cells)
    return [rule[enc(cells[(i-1)%L], cells[i], cells[(i+1)%L])] for i in range(L)]

def init(w):
    c=[N]*w; c[w//2]=P; return c

def entropy(cells):
    n=len(cells); H=0
    for v in [N,Z,P]:
        c=cells.count(v)
        if c>0: p=c/n; H-=p*math.log2(p)
    return H

def hsh(cells):
    h=2166136261
    for c in cells: h=((h^(c+1))*16777619)&0xFFFFFFFF
    return h

def quick_alive(rule, w):
    c=init(w)
    for _ in range(4):
        c=step(c,rule)
        if len(set(c))>1: return True
    return False

def score(elog, ratios, cycle, cat):
    if not elog: return 0
    last=elog[-1]
    if last<0.08: return 0
    s=0
    if 0.85<last<1.25: s+=40
    elif 0.55<last<1.4: s+=20
    q=elog[len(elog)*3//4:]
    if q:
        m=sum(q)/len(q)
        v=sum((h-m)**2 for h in q)/len(q)
        s+=25 if v<0.005 else 15 if v<0.02 else 5 if v<0.08 else 0
    if ratios:
        mn=min(ratios.values())
        s+=25 if mn>0.15 else 12 if mn>0.06 else 3 if mn>0.01 else -10
    if cycle is None: s+=10
    elif cycle>150: s+=5
    elif cycle<15: s-=20
    return max(0,round(s))

def scan_rule(rule, W=150, GENS=300):
    cells=init(W)
    seen=set(); elog=[]; cycle=None
    pts={10,25,50,75,100,150,200,250,300}; prog={}

    for g in range(1,GENS+1):
        cells=step(cells,rule)
        H=entropy(cells)
        elog.append(round(H,4))
        if g in pts: prog[g]=round(H,4)
        if cycle is None:
            h=hsh(cells)
            if h in seen: cycle=g
            else: seen.add(h)

    n=len(cells)
    ratios={-1:round(cells.count(N)/n,3), 0:round(cells.count(Z)/n,3), 1:round(cells.count(P)/n,3)}
    last=elog[-1]
    cat='Uniform' if last<0.3 else 'Ordered' if last<0.8 else 'Complex' if last<1.3 else 'Chaotic'
    return {'H':round(last,4),'cat':cat,'prog':prog,'ratios':ratios,'cycle':cycle,'elog':elog,'sc':score(elog,ratios,cycle,cat)}

# ── RUN ──────────────────────────────────────────────────────
random.seed(42)
TOTAL=1000; W=150; GENS=300

print(f"Scanning {TOTAL} rules × {GENS} gens × {W} cells...")
results=[]
skipped=0
for i in range(TOTAL):
    rule=make_rule(); att=0
    while not quick_alive(rule,W) and att<12: rule=make_rule(); att+=1
    if att==12: skipped+=1; continue
    rn=encode_rule(rule)
    r=scan_rule(rule,W,GENS)
    r['rn']=rn; r['b3']=to_base3(rn); r['rule']=rule
    results.append(r)
    if (i+1)%200==0: print(f"  {i+1}/{TOTAL}  ({len([x for x in results if x['cat']=='Complex'])} Complex so far)")

results.sort(key=lambda r:r['sc'],reverse=True)
print(f"\nDone. {len(results)} valid rules ({skipped} skipped — died immediately)\n")

# ── DISTRIBUTION ──────────────────────────────────────────────
dist=defaultdict(int)
for r in results: dist[r['cat']]+=1
print("COMPLEXITY DISTRIBUTION")
print("─"*40)
total_valid=len(results)
for k in ['Uniform','Ordered','Complex','Chaotic']:
    v=dist[k]; bar='█'*(v//10)
    print(f"  {k:10} {v:4} ({v/total_valid*100:5.1f}%)  {bar}")

# ── TOP 20 ────────────────────────────────────────────────────
print("\n\nTOP 20 RULES BY INTEREST SCORE")
print("─"*60)
for i,r in enumerate(results[:20]):
    cyc=f"cycle@{r['cycle']}" if r['cycle'] else "no cycle"
    print(f"\n#{i+1:2}  score={r['sc']:3}  {r['cat']:8}  H={r['H']:.4f}  {cyc}")
    print(f"    N={r['ratios'][-1]}  Z={r['ratios'][0]}  P={r['ratios'][1]}")
    print(f"    Rule: {r['rn']}")
    pts=r['prog']
    curve=' → '.join(f"g{k}:{v}" for k,v in sorted(pts.items()))
    print(f"    Curve: {curve}")

# ── COMPLEX DEEP DIVE ─────────────────────────────────────────
complex_r=[r for r in results if r['cat']=='Complex']
print(f"\n\nCOMPLEX RULES DEEP DIVE ({len(complex_r)} total)")
print("─"*60)

# Average entropy curve shape
keys=sorted({k for r in complex_r for k in r['prog']})
print("\nMean entropy at sample points (all Complex rules):")
for k in keys:
    vals=[r['prog'][k] for r in complex_r if k in r['prog']]
    if vals: print(f"  gen {k:4}: {sum(vals)/len(vals):.4f}  (n={len(vals)})")

# How many have cycles?
cyc=[r for r in complex_r if r['cycle']]
nocyc=[r for r in complex_r if not r['cycle']]
print(f"\nCycle stats: {len(cyc)} with cycles, {len(nocyc)} without")
if cyc:
    avg_cyc=sum(r['cycle'] for r in cyc)/len(cyc)
    print(f"  Avg cycle detection gen: {avg_cyc:.1f}")
    early=[r for r in cyc if r['cycle']<50]
    late=[r for r in cyc if r['cycle']>=50]
    print(f"  Early cycles (<50): {len(early)}   Late (≥50): {len(late)}")

# Class 4 candidates: high score, no cycle, balanced
class4=[r for r in complex_r if r['sc']>=70]
print(f"\nClass 4 candidates (score ≥ 70): {len(class4)}")
for r in class4:
    print(f"  Rule {r['rn']}  score={r['sc']}  H={r['H']}  ratios N={r['ratios'][-1]} Z={r['ratios'][0]} P={r['ratios'][1]}")
    print(f"    b3: {r['b3']}")

# Entropy trajectory analysis
print("\n\nENTROPY CURVE SHAPE ANALYSIS (Complex rules)")
print("─"*60)
rising=[];falling=[];stable=[];oscillating=[]
for r in complex_r:
    prog=r['prog']
    if not prog: continue
    early=prog.get(25, prog.get(10,0))
    mid=prog.get(100,0)
    late=prog.get(300, prog.get(200,0))
    if abs(late-mid)<0.05 and abs(mid-early)<0.1: stable.append(r)
    elif late>early+0.1: rising.append(r)
    elif late<early-0.1: falling.append(r)
    else:
        # check oscillation
        vals=[r['prog'].get(k,0) for k in keys if k in r['prog']]
        if len(vals)>3:
            diffs=[abs(vals[i]-vals[i-1]) for i in range(1,len(vals))]
            if max(diffs)>0.1 and sum(diffs)/len(diffs)>0.05: oscillating.append(r)
            else: stable.append(r)
        else: stable.append(r)
print(f"  Stable (entropy holds):       {len(stable)}")
print(f"  Rising (entropy grows):       {len(rising)}")
print(f"  Falling (entropy declines):   {len(falling)}")
print(f"  Oscillating (fluctuates):     {len(oscillating)}")

if rising:
    print(f"\nTop rising Complex rules (might be still evolving — run longer):")
    for r in sorted(rising,key=lambda x:x['sc'],reverse=True)[:3]:
        print(f"  Rule {r['rn']}  H={r['H']}  score={r['sc']}")

# Ratio balance in top rules
print("\n\nRATIO BALANCE — top 10 rules")
print("─"*40)
for r in results[:10]:
    ratN,ratZ,ratP=r['ratios'][-1],r['ratios'][0],r['ratios'][1]
    balance=1-max(abs(ratN-1/3),abs(ratZ-1/3),abs(ratP-1/3))*3
    print(f"  #{results.index(r)+1:2}  N:{ratN:.3f} Z:{ratZ:.3f} P:{ratP:.3f}  balance={balance:.2f}  {r['cat']}")
