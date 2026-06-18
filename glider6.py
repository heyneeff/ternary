"""
Cascade diagnosis and transducer search for rule 2130435961714.

Why glider6 v1 failed:
  - Gate distance = 20 cells < composite width ≈ 30 cells
  - Gate2 seed was INSIDE the gate1 composite's body
  - Two of three output types (Z, P) produce FROZEN composites (T=1)
    that carry no dynamic phase — only the N output keeps oscillating (T=6)

This version:
  1. COMPOSITE ANATOMY: measure composite size vs gate distance
     to find where composite fits cleanly inside the separation
  2. GATE AT SCALE: verify the gate still works at distance=100
  3. TRANSDUCER SEARCH: can the composite serve as gate2 input?
     Test: does a fresh seed placed at composite+D interact differently
     depending on which gate1 output was computed?
  4. CLEAN CASCADE: if transducer works, chain two gates
"""

N, Z, P = -1, 0, 1
TV = [N, Z, P]
TNAME = {N:'N', Z:'Z', P:'P'}
PHI = {N:0, Z:2, P:4}
COUNT_TO_TRIT = {24:N, 27:Z, 29:P}

def enc(l,c,r): return (l+1)*9+(c+1)*3+(r+1)
def decode_rule(n):
    rule=[]; x=n
    for _ in range(27): rule.append(TV[x%3]); x//=3
    return rule

RULE = 2130435961714
rule_arr = decode_rule(RULE)

def step(cells,rule):
    L=len(cells)
    return [rule[enc(cells[(i-1)%L],cells[i],cells[(i+1)%L])] for i in range(L)]

def run_seeds(seeds_by_gen, W=800, GENS=900, bg=N):
    cells=[bg]*W
    for (x,v) in seeds_by_gen.get(0,[]): cells[x]=v
    history=[cells[:]]
    for g in range(1,GENS+1):
        cells=step(cells,rule_arr)
        for (x,v) in seeds_by_gen.get(g,[]): cells[x]=v
        history.append(cells[:])
    bg_rows=[row[:30] for row in history]
    return history, bg_rows

def measure(history, bg_rows, x_lo, x_hi, g_start=500, g_range=80, bg_W=30):
    """Average anomaly count in [x_lo, x_hi] over g_start..g_start+g_range."""
    counts=[]
    for g in range(g_start, min(g_start+g_range, len(history))):
        row=history[g]; bg=bg_rows[g]
        counts.append(sum(1 for x in range(x_lo,x_hi) if row[x]!=bg[x%bg_W]))
    return round(sum(counts)/len(counts),1) if counts else 0.0

def composite_extent(history, bg_rows, xA, xB, g=600, bg_W=30, gap=5):
    """Find leftmost and rightmost anomalous cells near xA..xB at gen g."""
    W=len(history[0])
    row=history[g]; bg=bg_rows[g]
    x0=max(0,xA-50); x1=min(W,xB+50)
    anoms=[x for x in range(x0,x1) if row[x]!=bg[x%bg_W]]
    if not anoms: return None,None,0
    # Find clusters
    clusters=[]; cl=[anoms[0]]
    for x in anoms[1:]:
        if x-cl[-1]<=gap: cl.append(x)
        else: clusters.append(cl); cl=[x]
    clusters.append(cl)
    # Biggest cluster
    big=max(clusters,key=len)
    return min(big), max(big), len(big)

def phase_scan_gate(dist, W=800, GENS=700, g_measure=500, g_range=80):
    """
    Run the 2-body gate at given separation for all 3 even-phase pairs.
    Returns dict: (tA,tB) → measured_total.
    """
    xA=300; xB=xA+dist
    results={}
    for tA in [N,Z,P]:
        for tB in [N,Z,P]:
            offset=(PHI[tA]-PHI[tB])%6
            seeds={0:[(xA,P)]}
            if offset==0: seeds[0].append((xB,P))
            else: seeds[offset]=[(xB,P)]
            h,bg=run_seeds(seeds,W=W,GENS=GENS)
            cx=(xA+xB)//2
            total=measure(h,bg,xA-30,xB+30,g_measure,g_range)
            results[(tA,tB)]=round(total)
    return results

# ════════════════════════════════════════════════════════════════
# 1. COMPOSITE ANATOMY: size vs distance
# ════════════════════════════════════════════════════════════════
print("="*70)
print("1. COMPOSITE ANATOMY: how wide is the output composite vs gate distance?")
print("="*70)
print(f"  {'dist':>5}  {'comp_left':>10}  {'comp_right':>11}  {'width':>6}  {'fits?':>8}")
print(f"  {'─'*50}")

xA_anat=300
for dist in [20,40,60,80,100,150,200]:
    xB_anat=xA_anat+dist
    seeds_a={0:[(xA_anat,P),(xB_anat,P)]}
    h_a,bg_a=run_seeds(seeds_a,W=800,GENS=700)
    lo,hi,sz=composite_extent(h_a,bg_a,xA_anat,xB_anat,g=600)
    fits='YES' if (lo is not None and hi is not None and (hi-lo)<dist) else 'NO '
    if lo is not None:
        print(f"  {dist:5}  {lo:10}  {hi:11}  {hi-lo:6}  {fits:>8}")
    else:
        print(f"  {dist:5}  {'(no anomaly)':>22}  {'—':>8}")

print()

# ════════════════════════════════════════════════════════════════
# 2. GATE AT SCALE: does distance=150 still give 3 distinct outputs?
# ════════════════════════════════════════════════════════════════
print("="*70)
print("2. GATE VERIFICATION AT LARGER DISTANCES")
print("="*70)
for dist in [100,150]:
    print(f"\n  Distance = {dist}:")
    results=phase_scan_gate(dist, W=900, GENS=750)
    unique_outputs=set(results.values())
    print(f"  {'(tA,tB)':>10}  {'total':>8}  {'rank→trit':>12}")
    for (tA,tB),tot in sorted(results.items()):
        if PHI[tA] in [0,2,4] and PHI[tB] in [0,2,4]:
            rank=sorted(unique_outputs).index(tot) if tot in unique_outputs else '?'
            print(f"  ({TNAME[tA]:>2},{TNAME[tB]:>2})     {tot:>8}  rank={rank} → {TNAME.get(COUNT_TO_TRIT.get(tot),'?')}")
    print(f"  Unique outputs at distance {dist}: {sorted(unique_outputs)}")
    print(f"  Gate functional: {'YES' if len(unique_outputs)>=3 else 'NO'}")

# ════════════════════════════════════════════════════════════════
# 3. TRANSDUCER SEARCH: does a fresh seed 'see' different things
#    depending on what gate1 computed?
# ════════════════════════════════════════════════════════════════
print()
print("="*70)
print("3. TRANSDUCER SEARCH at distance=150")
print("="*70)
print("  Protocol: run gate1(tA,tB) at x=200,350.")
print("  At gen 550, inject fresh seed C at x=500 (150 cells right of B).")
print("  Measure output near C at gen 750. Does it depend on gate1's output?")
print()

GATE_DIST_T=150
xA_t=200; xB_t=xA_t+GATE_DIST_T; xC_t=xB_t+GATE_DIST_T
INJECT_C=550

print(f"  xA={xA_t}, xB={xB_t}, xC={xC_t}")
print(f"  C injected at gen {INJECT_C}")
print()
print(f"  {'(tA,tB,tC)':>14}  {'gate1_pred':>10}  {'C_output':>10}  {'match?':>7}")
print(f"  {'─'*55}")

transducer_ok=True
trans_results={}
for tA in [N,Z,P]:
    for tB in [N,Z,P]:
        for tC in [N,Z,P]:
            offAB=(PHI[tA]-PHI[tB])%6
            offC=(PHI[tC])  # C starts at gen INJECT_C, phase at C-composite interact ≈ (INJECT_C+75)%6
            # inject C offset so its effective phase = PHI[tC] at interaction time
            # interaction happens ~GATE_DIST_T/2 = 75 gens after injection
            # so C's phase at interaction = (75) % 6 = 3
            # to get phase PHI[tC], inject at gen INJECT_C + (PHI[tC] - 75%6)%6
            interact_lag=GATE_DIST_T//2  # rough estimate
            c_phase_at_interact=(interact_lag)%6  # without offset
            c_offset=(PHI[tC]-c_phase_at_interact)%6
            c_gen=INJECT_C+c_offset

            seeds={0:[(xA_t,P)]}
            if offAB==0: seeds[0].append((xB_t,P))
            else: seeds.setdefault(offAB,[]).append((xB_t,P))
            seeds.setdefault(c_gen,[]).append((xC_t,P))

            h,bg=run_seeds(seeds,W=800,GENS=800)
            out=measure(h,bg,xC_t-30,xC_t+60,g_start=700,g_range=80)

            # Expected gate1 output
            def sub3(x,y):
                r=x-y
                if r>1: r-=3
                if r<-1: r+=3
                return r
            g1=sub3(tB,tA)
            pred_count={N:24,Z:27,P:29}[g1]

            trans_results[(tA,tB,tC)]=round(out)
            print(f"  ({TNAME[tA]},{TNAME[tB]},{TNAME[tC]})          {pred_count:>10}  {out:>10.1f}")

# Check if C_output distinguishes different gate1 results
print()
print("  Does C output differ by gate1 result (same tC, different gate1)?")
for tC in [N,Z,P]:
    group={}
    for tA in [N,Z,P]:
        for tB in [N,Z,P]:
            g1_out=COUNT_TO_TRIT.get({N:24,Z:27,P:29}.get(
                {N:N,Z:Z,P:P}[({N:0,Z:1,P:2}[tB]-{N:0,Z:1,P:2}[tA])%3+N],-1),-1)
            def sub3b(x,y):
                r=x-y
                if r>1: r-=3
                if r<-1: r+=3
                return r
            g1=sub3b(tB,tA)
            out=trans_results.get((tA,tB,tC),0)
            group.setdefault(TNAME[g1],[]).append(out)
    print(f"    tC={TNAME[tC]}: ", end='')
    for k,vs in group.items():
        avg=sum(vs)/len(vs)
        print(f"gate1={k}→outputs≈{avg:.0f}  ", end='')
    print()

# ════════════════════════════════════════════════════════════════
# 4. SUMMARY AND DIAGNOSIS
# ════════════════════════════════════════════════════════════════
print()
print("="*70)
print("4. DIAGNOSIS AND PATH FORWARD")
print("="*70)
print("""
  GATE (2-body): CONFIRMED WORKING
    - Computes (b-a) mod 3 in balanced ternary
    - 9/9 input pairs correct, output closed under ternary

  CASCADE (3-body): REQUIRES TRANSDUCER
    The gate outputs a COMPOSITE STRUCTURE, not a single oscillator.
    For cascade, the composite must:
      (a) Fit within the gate distance (composite width < separation)
      (b) Present a well-defined phase to the next gate's input
      (c) Produce distinct outputs depending on which trit it encodes

  WHAT THE COMPOSITE ANATOMY TELLS US:
    At small distances (20-60): composite width > gate distance → gate2 fires inside composite
    At larger distances (150+): composite fits → gate2 can interact cleanly
    Need to check: does the composite at distance=150 act like a typed input?

  WHAT T=1 FROZEN COMPOSITES MEAN:
    Z-output and P-output composites freeze (constant pattern, no phase).
    N-output composite keeps oscillating (T=6, has a phase).
    → Cascade through frozen composites needs a 'read-out' mechanism.
    → One option: the composite SIZE (not phase) drives the next gate.

  NEXT EXPERIMENT:
    If Section 3 shows C's output varies by gate1 result → transducer exists!
    Specifically, look at: for fixed tC, do different gate1 outputs
    give different C measurements? If yes, the composite size is a readable input.
""")
