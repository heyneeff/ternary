import math

N, Z, P = -1, 0, 1
TV = [N, Z, P]

def enc(l,c,r): return (l+1)*9+(c+1)*3+(r+1)

def decode_rule(rule_num):
    rule=[]; n=rule_num
    for _ in range(27): rule.append(TV[n%3]); n//=3
    return rule

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

def run_deep(rule_num, W=200, GENS=1000):
    rule=decode_rule(rule_num)
    cells=init(W)
    seen=set(); elog=[]; cycle=None
    # sample every 10 gens
    prog={}

    for g in range(1,GENS+1):
        cells=step(cells,rule)
        H=round(entropy(cells),5)
        elog.append(H)
        if g%50==0: prog[g]=H
        if cycle is None:
            h=hsh(cells)
            if h in seen: cycle=g
            else: seen.add(h)

    n=len(cells)
    ratios={-1:round(cells.count(N)/n,3), 0:round(cells.count(Z)/n,3), 1:round(cells.count(P)/n,3)}

    # Stability: look at last 200 gens
    tail=elog[-200:]
    tail_mean=sum(tail)/len(tail)
    tail_var=sum((h-tail_mean)**2 for h in tail)/len(tail)
    tail_min=min(tail); tail_max=max(tail)

    # Peak
    peak_h=max(elog); peak_gen=elog.index(peak_h)+1

    # When did it first enter final zone (within 0.15 of tail_mean)?
    settle_gen=None
    for g,h in enumerate(elog):
        if abs(h-tail_mean)<0.15:
            # check it stays there for 50 gens
            window=elog[g:g+50]
            if window and all(abs(x-tail_mean)<0.2 for x in window):
                settle_gen=g+1; break

    # Classification
    if cycle and cycle<100:
        verdict='PERIODIC (early)'
    elif tail_mean<0.2:
        verdict='COLLAPSED'
    elif tail_mean>1.35:
        if tail_var<0.01: verdict='CHAOTIC-STABLE'
        else: verdict='CHAOTIC-NOISY'
    elif 0.7<tail_mean<1.3 and tail_var<0.008:
        verdict='CLASS 4 ✓'
    elif 0.7<tail_mean<1.3 and tail_var<0.02:
        verdict='CLASS 4 (soft)'
    elif tail_var>0.02:
        verdict='OSCILLATING'
    else:
        verdict='ORDERED'

    return {
        'ruleNum': rule_num,
        'verdict': verdict,
        'tailMean': round(tail_mean,4),
        'tailVar': round(tail_var,6),
        'tailMin': round(tail_min,4),
        'tailMax': round(tail_max,4),
        'peakH': round(peak_h,4),
        'peakGen': peak_gen,
        'settleGen': settle_gen,
        'cycle': cycle,
        'ratios': ratios,
        'prog': prog,
        'elog': elog,
    }

# ── THE 29 CLASS 4 CANDIDATES FROM THE INITIAL SCAN ──────────
candidates = [
    (6085029223841, 90),
    (2130435961714, 90),
    (4672136208972, 87),
    (5036856449773, 87),
    (7156082947147, 80),
    (1704580786738, 78),
    (5237248727992, 78),
    (6285900448264, 78),
    (4457473814168, 78),
    (5438468921042, 78),
    (666256861928,  78),
    (1976392072281, 78),
    (187053944393,  78),
    (5260895681850, 78),
    (2856969762698, 78),
    (7297135950719, 78),
    (4373414389357, 78),
    (1381104505708, 77),
    (7227145595524, 77),
    (7538651739281, 75),
    (1672907266213, 73),
    (5355161217626, 73),
    (7190173222518, 73),
    (1183465070315, 73),
    (5136177650762, 73),
    (3213519104177, 70),
    (1269012439058, 70),
    (3613196253444, 70),
    (1251060216861, 70),
]

print(f"Deep scan: {len(candidates)} candidates × 1000 gens × 200 cells\n")
results=[]
for i,(rn,init_score) in enumerate(candidates):
    r=run_deep(rn)
    r['initScore']=init_score
    results.append(r)
    print(f"  [{i+1:2}/29] Rule {rn}  →  {r['verdict']:22}  H={r['tailMean']:.4f}±{r['tailVar']:.5f}  peak={r['peakH']:.4f}@{r['peakGen']}")

# ── SUMMARY ───────────────────────────────────────────────────
print(f"\n{'='*70}")
print("VERDICT SUMMARY")
print(f"{'='*70}")
from collections import Counter
verdicts=Counter(r['verdict'] for r in results)
for v,n in sorted(verdicts.items(),key=lambda x:-x[1]):
    print(f"  {v:25} {n}")

# ── CONFIRMED CLASS 4 ─────────────────────────────────────────
class4=[r for r in results if 'CLASS 4' in r['verdict']]
print(f"\n{'='*70}")
print(f"CONFIRMED CLASS 4 RULES ({len(class4)})")
print(f"{'='*70}")
class4.sort(key=lambda r:r['tailVar'])  # most stable first
for r in class4:
    print(f"\nRule {r['ruleNum']}")
    print(f"  Verdict    : {r['verdict']}")
    print(f"  Tail H     : {r['tailMean']} ± {r['tailVar']} (range {r['tailMin']}–{r['tailMax']})")
    print(f"  Peak       : {r['peakH']} at gen {r['peakGen']}")
    print(f"  Settled    : gen {r['settleGen'] or 'not yet'}")
    print(f"  Cycle      : {r['cycle'] or 'none detected in 1000 gens'}")
    print(f"  Ratios     : N={r['ratios'][-1]}  Z={r['ratios'][0]}  P={r['ratios'][1]}")
    pts=r['prog']
    curve=' '.join(f"g{k}:{v:.3f}" for k,v in sorted(pts.items()))
    print(f"  Entropy    : {curve}")

# ── ENTROPY CURVE PROFILES ────────────────────────────────────
print(f"\n{'='*70}")
print("ENTROPY CURVE PROFILES (all 29, every 50 gens)")
print(f"{'='*70}")
print(f"{'Rule':>15} {'Init':>4} {'Verdict':22} {'g50':>6} {'g200':>6} {'g500':>6} {'g750':>6} {'g1000':>6}")
print("-"*70)
for r in results:
    p=r['prog']
    print(f"{r['ruleNum']:>15} {r['initScore']:>4} {r['verdict']:22} "
          f"{p.get(50,'—'):>6} {p.get(200,'—'):>6} {p.get(500,'—'):>6} {p.get(750,'—'):>6} {p.get(1000,'—'):>6}")

# ── MOST INTERESTING FINDING ──────────────────────────────────
print(f"\n{'='*70}")
print("MOST INTERESTING FINDINGS")
print(f"{'='*70}")

# Rules that peaked high then settled lower (classic Class 4 shape)
peak_settle=[(r, r['peakH']-r['tailMean']) for r in results if r['settleGen'] and r['peakH']>r['tailMean']+0.15]
if peak_settle:
    peak_settle.sort(key=lambda x:-x[1])
    print(f"\nClassic peak→settle shape (entropy rises then locks in):")
    for r,drop in peak_settle[:5]:
        print(f"  Rule {r['ruleNum']}  peak={r['peakH']:.4f}@g{r['peakGen']} → settled {r['tailMean']:.4f} @ g{r['settleGen']}  (dropped {drop:.4f})")

# Longest to settle
long_settle=[r for r in results if r['settleGen'] and r['settleGen']>300]
if long_settle:
    long_settle.sort(key=lambda r:-(r['settleGen'] or 0))
    print(f"\nSlowest to settle (most complex transient):")
    for r in long_settle[:5]:
        print(f"  Rule {r['ruleNum']}  settled @ gen {r['settleGen']}  final H={r['tailMean']:.4f}")

# Check for the 'still rising' ones from initial scan
still_rising=[r for r in results if r['prog'].get(1000,0) > r['prog'].get(500,0)+0.05]
print(f"\nStill rising at gen 1000 (need even longer runs): {len(still_rising)}")
for r in still_rising:
    print(f"  Rule {r['ruleNum']}  g500={r['prog'].get(500,'?')}  g1000={r['prog'].get(1000,'?')}")
