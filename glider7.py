"""
Wire search for rule 2130435961714.

A wire would allow cascade: a chain of oscillators where a phase perturbation
at position 1 propagates to positions 2, 3, 4... so that:
  gate(1,2) output types → gate(2,3) input → gate(3,4) input → etc.

Strategy: place a chain of oscillators spaced at d=60 (the known good gate distance).
Perturb the LEFTMOST oscillator's phase by injecting it N gens late.
Check if oscillators 2, 3, 4 show a measurable phase shift vs. unperturbed chain.

If phase propagates: wire found.
If not: try different spacings (d=20, d=30, d=40) or probe the composite's right edge.
"""

N, Z, P = -1, 0, 1
TV = [N, Z, P]
TNAME = {N:'N', Z:'Z', P:'P'}
PHI = {N:0, Z:2, P:4}

def enc(l,c,r): return (l+1)*9+(c+1)*3+(r+1)
def decode_rule(n):
    rule=[]; x=n
    for _ in range(27): rule.append(TV[x%3]); x//=3
    return rule

RULE = 2130435961714
rule_arr = decode_rule(RULE)

def step(cells, rule):
    L=len(cells)
    return [rule[enc(cells[(i-1)%L],cells[i],cells[(i+1)%L])] for i in range(L)]

def run_chain(seed_positions, phase_offsets, W=900, GENS=1000):
    """
    seed_positions: [x0, x1, x2, ...]
    phase_offsets:  [t0, t1, t2, ...] — gen at which each seed is injected
    """
    cells = [N]*W
    seed_map = {}
    for x, t in zip(seed_positions, phase_offsets):
        seed_map.setdefault(t, []).append(x)
    for x in seed_map.get(0, []): cells[x] = P
    history = [cells[:]]
    for g in range(1, GENS+1):
        cells = step(cells, rule_arr)
        for x in seed_map.get(g, []): cells[x] = P
        history.append(cells[:])
    bg_rows = [row[:30] for row in history]
    return history, bg_rows

def local_count(history, bg_rows, cx, half_w=25, g_start=600, g_range=100):
    counts = []
    for g in range(g_start, min(g_start+g_range, len(history))):
        row = history[g]; bg = bg_rows[g]
        counts.append(sum(1 for x in range(max(0,cx-half_w), min(len(row),cx+half_w))
                         if row[x] != bg[x%30]))
    return round(sum(counts)/len(counts), 1) if counts else 0.0

def local_period(history, bg_rows, cx, half_w=25, g_start=700, bg_W=30):
    """Find period of oscillation near cx."""
    x0=max(0,cx-half_w); x1=min(len(history[0]),cx+half_w)
    snaps=[]
    for g in range(g_start, min(g_start+20, len(history))):
        row=history[g]; bg=bg_rows[g]
        snaps.append(tuple(row[x]-bg[x%bg_W] for x in range(x0,x1)))
    for T in range(1,10):
        if all(snaps[i]==snaps[i+T] for i in range(len(snaps)-T)):
            return T
    return None

# ═══════════════════════════════════════════════════════════════
# WIRE TEST 1: chain of 4 oscillators, vary first seed's phase
# ═══════════════════════════════════════════════════════════════
print("="*70)
print("WIRE TEST 1: 4-oscillator chain at spacing d=60")
print("  Perturb leftmost seed phase. Does it propagate rightward?")
print("="*70)

SPACING = 60
NSEEDS  = 4
x0_chain = 200
xs = [x0_chain + i*SPACING for i in range(NSEEDS)]

print(f"\n  Positions: {xs}")
print(f"  Measuring phase at each oscillator position for perturbation offsets 0..5")
print()
print(f"  {'offset':>7}  " + "  ".join(f"x={x:4d}" for x in xs))
print(f"  {'─'*65}")

chain_results = {}
for offset in range(6):
    # Perturb only FIRST seed by 'offset' gens
    phase_offsets = [offset] + [0]*(NSEEDS-1)
    h, bg = run_chain(xs, phase_offsets, W=900, GENS=1000)
    counts = [local_count(h, bg, x, half_w=25, g_start=700, g_range=100) for x in xs]
    periods= [local_period(h, bg, x, half_w=25, g_start=750) for x in xs]
    chain_results[offset] = counts
    per_str = "  ".join(f"T={p if p else '?'}" for p in periods)
    print(f"  {offset:7}  " + "  ".join(f"{c:6.1f}" for c in counts) +
          f"    periods: {per_str}")

print()
# Check if counts at positions 1,2,3 vary with offset
print("  Variation at each position (max-min across offsets 0..5):")
for i, x in enumerate(xs):
    vals = [chain_results[o][i] for o in range(6)]
    span = max(vals) - min(vals)
    print(f"    x={x}: min={min(vals):.1f}  max={max(vals):.1f}  span={span:.1f}  "
          f"{'PROPAGATES' if span > 2 else 'no signal'}")

# ═══════════════════════════════════════════════════════════════
# WIRE TEST 2: tighter spacing — try d=20, d=30, d=40
# Check if tighter chains propagate phase
# ═══════════════════════════════════════════════════════════════
print()
print("="*70)
print("WIRE TEST 2: scan spacings d=20,30,40,50 for phase propagation")
print("  4-seed chain, perturb seed 0 by 0 vs 2 gens, measure seeds 1,2,3")
print("="*70)

for spacing in [20, 30, 40, 50]:
    xs2 = [200 + i*spacing for i in range(4)]
    # unperturbed baseline
    h0, bg0 = run_chain(xs2, [0,0,0,0], W=700, GENS=900)
    c0 = [local_count(h0, bg0, x, half_w=15, g_start=650, g_range=100) for x in xs2]
    # perturbed (offset=2 on seed 0)
    h2, bg2 = run_chain(xs2, [2,0,0,0], W=700, GENS=900)
    c2 = [local_count(h2, bg2, x, half_w=15, g_start=650, g_range=100) for x in xs2]
    diffs = [round(c2[i]-c0[i],1) for i in range(4)]
    propagates = any(abs(d)>1 for d in diffs[1:])
    print(f"  d={spacing:2}  xs={xs2}  Δcounts={diffs}  {'SIGNAL PROPAGATES' if propagates else 'no propagation'}")

# ═══════════════════════════════════════════════════════════════
# WIRE TEST 3: RIGHT-EDGE RELAY
# Instead of a chain, use the composite's RIGHT EDGE as the relay.
# Gate1 output composite (at d=60) has right edge at xB+~44.
# Place seed C exactly at that right edge and measure.
# ═══════════════════════════════════════════════════════════════
print()
print("="*70)
print("WIRE TEST 3: right-edge relay")
print("  Composite right edge found at xA+106 (d=60 anatomy).")
print("  Place C at xA+106, measuring if C sees different things for N/Z/P composites.")
print("="*70)

xA3 = 200
for tA, tB in [(N,N),(N,Z),(N,P),(Z,Z),(P,P)]:
    offset = (PHI[tA]-PHI[tB])%6
    seeds = {0:[(xA3,P)]}
    if offset==0: seeds[0].append((xA3+60,P))
    else:         seeds.setdefault(offset,[]).append((xA3+60,P))

    h,bg = run_chain([xA3,xA3+60], [PHI[tA]//2, PHI[tB]//2],
                     W=700, GENS=800)

    # Actually run properly
    cells=[N]*700; cells[xA3]=P
    hist=[cells[:]]
    bg_rows2=[cells[:30]]
    rule_local=rule_arr
    xB3=xA3+60
    for g in range(1,801):
        cells=step(cells,rule_local)
        if g==offset: cells[xB3]=P
        hist.append(cells[:])
        bg_rows2.append(cells[:30] if g==0 else hist[0][:30])
    bg_rows2=[hist[0][:30] for _ in hist]  # use gen-0 as reference bg

    # Composite right edge is around x=xA3+106 from anatomy
    right_edge = xA3 + 106
    # measure anomaly near right edge at gen 600
    row600=hist[600]; bg600=bg_rows2[600]
    cnt=sum(1 for x in range(right_edge-10,right_edge+20) if row600[x]!=bg600[x%30])

    def sub3(x,y):
        r=x-y
        if r>1: r-=3
        if r<-1: r+=3
        return r
    expected_out=sub3(tB,tA)
    print(f"  ({TNAME[tA]},{TNAME[tB]}) → expected {TNAME[expected_out]:2}  "
          f"right-edge count at gen 600: {cnt}")

# ═══════════════════════════════════════════════════════════════
# WIRE TEST 4: SCAN for any spacing where a 3-seed chain
# gives 3 distinct outputs (indicating natural cascade)
# ═══════════════════════════════════════════════════════════════
print()
print("="*70)
print("WIRE TEST 4: brute-force cascade search over spacings")
print("  3 seeds: A(phase 0), B(phase 0,2,4), C(phase 0)")
print("  Vary spacing d=20..120. Look for: 3 distinct outputs at C position.")
print("  That would mean: B's phase is relayed through the A-B composite to C.")
print("="*70)

for spacing in range(20, 130, 10):
    xA4=150; xB4=xA4+spacing; xC4=xB4+spacing
    if xC4+50>850: break

    outputs=[]
    for pB_offset in [0,2,4]:  # B encoding N, Z, P
        cells=[N]*850; cells[xA4]=P
        hist=[cells[:]]; bgr=[cells[:30]]
        for g in range(1,800):
            cells=step(cells,rule_arr)
            if g==pB_offset: cells[xB4]=P
            if g==0:         cells[xC4]=P  # C always at gen 0 same as A
            hist.append(cells[:])
        bg_fixed=hist[0][:30]
        # Measure at C position after settling
        tot=0
        for g in range(650,750):
            row=hist[g]
            tot+=sum(1 for x in range(xC4-20,xC4+50) if row[x]!=bg_fixed[x%30])
        outputs.append(round(tot/100,1))

    distinct=len(set(outputs))
    flag='★ CASCADE CANDIDATE' if distinct>=3 else ''
    print(f"  d={spacing:3}  C outputs for B=N/Z/P: {outputs}  ({distinct} distinct) {flag}")

print()
print("="*70)
print("INTERPRETATION")
print("="*70)
print("""
  Wire found = any position where phase perturbation causes measurable change
  Cascade found = 3 distinct C outputs for 3 distinct B phase inputs

  If none found in this rule: cascade requires either
    (a) a different connecting rule (hybrid architecture)
    (b) 2D ternary CA where structures travel
    (c) timed injection protocol (manual cascade)
""")
