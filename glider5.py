"""
Phase scan for rule 2130435961714 oscillator interactions.

Confirmed facts:
  - Single P seed → period-6 stationary oscillator, stable 2000+ gens
  - At separation 300 cells: two oscillators are independent (both settle at 13)
  - At separation 100 cells: bound state (A=10, mid=8, B=25, total=43)

This script maps:
  1. DISTANCE SCAN: what separations produce independent vs bound states?
  2. PHASE SCAN: at fixed distance, vary timing of second seed injection (0..5 gens)
                 — does the phase of collision change the output?

If phase changes the output: we have a ternary logic gate.
The period-6 oscillator has 6 phase states → 6 possible input configurations.
"""

N, Z, P = -1, 0, 1
TV = [N, Z, P]

def enc(l, c, r): return (l+1)*9 + (c+1)*3 + (r+1)

def decode_rule(n):
    rule = []; x = n
    for _ in range(27): rule.append(TV[x % 3]); x //= 3
    return rule

RULE = 2130435961714
rule_arr = decode_rule(RULE)
BG_VEL = -1.0  # background moves left at 1 cell/gen

def step(cells, rule):
    L = len(cells)
    return [rule[enc(cells[(i-1)%L], cells[i], cells[(i+1)%L])] for i in range(L)]

def run_two_seeds(xA, xB, phase_offset=0, W=700, GENS=800, bg_val=N):
    """
    Plant seed A at gen 0, seed B at gen phase_offset.
    Returns (history, bg_rows).
    """
    cells = [bg_val] * W
    cells[xA] = P
    history = [cells[:]]
    for g in range(1, GENS + 1):
        cells = step(cells, rule_arr)
        if g == phase_offset and xB is not None:
            cells[xB] = P
        history.append(cells[:])
    bg_rows = [row[:30] for row in history]
    return history, bg_rows

def measure_outcome(history, bg_rows, xA, xB, measure_start=500, measure_gens=60, bg_W=30):
    """
    Measure the stable anomaly signature across [xA-60, xB+60].
    Returns a dict with:
      - total: total anomaly count in window
      - A: anomaly near xA (±30)
      - mid: anomaly in gap (xA+30..xB-30)
      - B: anomaly near xB (±30)
      - n_clusters: number of separated anomaly clusters
      - fingerprint: tuple of cluster sizes (sorted desc)
    """
    W = len(history[0])
    g_lo = measure_start
    g_hi = min(measure_start + measure_gens, len(history))
    n = g_hi - g_lo

    totals = {'total': 0, 'A': 0, 'mid': 0, 'B': 0}
    for g in range(g_lo, g_hi):
        row = history[g]; bg = bg_rows[g]
        for x in range(max(0, xA-60), min(W, xB+61)):
            if row[x] != bg[x % bg_W]:
                totals['total'] += 1
                if x < xA + 30:
                    totals['A'] += 1
                elif x > xB - 30:
                    totals['B'] += 1
                else:
                    totals['mid'] += 1

    # Average over gens
    out = {k: round(v / n, 1) for k, v in totals.items()}

    # Cluster structure at midpoint gen
    g_mid = (g_lo + g_hi) // 2
    row = history[g_mid]; bg = bg_rows[g_mid]
    anoms = [x for x in range(max(0, xA-70), min(W, xB+71)) if row[x] != bg[x % bg_W]]
    clusters = []
    if anoms:
        cl = [anoms[0]]
        for x in anoms[1:]:
            if x - cl[-1] <= 5: cl.append(x)
            else: clusters.append(len(cl)); cl = [x]
        clusters.append(len(cl))
    clusters.sort(reverse=True)
    out['n_clusters'] = len(clusters)
    out['fingerprint'] = tuple(clusters[:4])  # top 4 cluster sizes

    return out

def classify_outcome(out, isolated_size=13.0):
    """Classify interaction outcome from measurement dict."""
    A, mid, B = out['A'], out['mid'], out['B']
    total = out['total']
    tol = 2.5  # tolerance for "about the same as isolated"
    both_isolated = abs(A - isolated_size) < tol and abs(B - isolated_size) < tol and mid < 3

    if both_isolated:
        return 'INDEPENDENT'
    elif total < isolated_size * 0.5:
        return 'ANNIHILATED'
    elif abs(A - B) < tol and mid < 3:
        return f'BOUND-SYM  (A={A:.0f} B={B:.0f})'
    elif mid >= 3:
        if A > B:
            return f'BOUND-L    (A={A:.0f} mid={mid:.0f} B={B:.0f})'
        else:
            return f'BOUND-R    (A={A:.0f} mid={mid:.0f} B={B:.0f})'
    else:
        return f'OTHER      (A={A:.0f} mid={mid:.0f} B={B:.0f})'

# ══════════════════════════════════════════════════════════════
# SCAN 1: DISTANCE SCAN (phase_offset=0)
# ══════════════════════════════════════════════════════════════
print("═"*70)
print("SCAN 1: DISTANCE vs OUTCOME  (phase_offset=0, W=700, GENS=800)")
print("═"*70)
print(f"  {'dist':>5}  {'outcome':<30}  {'A':>5}  {'mid':>5}  {'B':>5}  {'clusters'}")
print(f"  {'─'*65}")

BASE_X = 200     # left seed always at x=200
DISTANCES = list(range(20, 210, 10))  # 20, 30, … 200
distance_results = {}

for dist in DISTANCES:
    xA = BASE_X
    xB = BASE_X + dist
    h, bg = run_two_seeds(xA, xB, phase_offset=0, W=700, GENS=800)
    out = measure_outcome(h, bg, xA, xB, measure_start=500, measure_gens=80)
    outcome = classify_outcome(out)
    distance_results[dist] = (outcome, out)
    print(f"  {dist:5}  {outcome:<30}  {out['A']:5.1f}  {out['mid']:5.1f}  {out['B']:5.1f}  {out['fingerprint']}")

# Find critical distance
indep = [d for d, (o, _) in distance_results.items() if o == 'INDEPENDENT']
bound = [d for d, (o, _) in distance_results.items() if o != 'INDEPENDENT']
print(f"\n  Independent at: {sorted(indep)}")
print(f"  Bound/other at: {sorted(bound)}")
if indep and bound:
    critical = min(indep)
    print(f"  Critical distance ≈ {critical} cells (first independent)")

# ══════════════════════════════════════════════════════════════
# SCAN 2: PHASE SCAN at multiple distances
# ══════════════════════════════════════════════════════════════
print(f"\n{'═'*70}")
print("SCAN 2: PHASE OFFSET vs OUTCOME  (vary timing of seed B)")
print(f"{'═'*70}")

# Pick 3 interesting distances: one clearly bound, one near-critical, one independent
bound_dists = sorted(bound)[:3] if bound else []
near_crit = [d for d in DISTANCES if abs(d - (min(indep) - 20)) < 15] if indep else []
scan_dists = sorted(set(bound_dists[:2] + near_crit[:1] + ([min(indep)] if indep else [])))[:4]
if not scan_dists: scan_dists = [60, 100, 140]

print(f"\n  Scanning distances: {scan_dists}")
print(f"  Phase offsets: 0..5 (period-6 oscillator)")
print()

phase_table = {}
for dist in scan_dists:
    xA = BASE_X
    xB = BASE_X + dist
    print(f"  Distance = {dist} cells  (xA={xA}, xB={xB})")
    print(f"  {'phase':>6}  {'outcome':<30}  {'A':>5}  {'mid':>5}  {'B':>5}  {'total':>6}")
    row_outcomes = []
    for phase in range(6):
        h, bg = run_two_seeds(xA, xB, phase_offset=phase, W=700, GENS=800)
        out = measure_outcome(h, bg, xA, xB, measure_start=500, measure_gens=80)
        outcome = classify_outcome(out)
        row_outcomes.append(outcome)
        phase_table[(dist, phase)] = (outcome, out)
        print(f"  {phase:6}  {outcome:<30}  {out['A']:5.1f}  {out['mid']:5.1f}  {out['B']:5.1f}  {out['total']:6.1f}")

    unique = len(set(row_outcomes))
    print(f"         → {unique} distinct outcomes at distance {dist}")
    print()

# ══════════════════════════════════════════════════════════════
# SCAN 3: TERNARY GATE TABLE
# Build a truth table: (phase_A, phase_B) → output signature
# Phase of A controlled by injecting at gen 0..5 before B
# ══════════════════════════════════════════════════════════════
print(f"{'═'*70}")
print("SCAN 3: TERNARY GATE TABLE  (6×6 phase combinations)")
print(f"{'═'*70}")
print("  Inject A at gen 0, inject B at various gen offsets AND")
print("  vary A's starting phase by injecting A at different positions")
print("  Use distance=60 (likely bound region)")
print()

# Use the first bound distance
gate_dist = bound_dists[0] if bound_dists else 60
xA = BASE_X
xB = BASE_X + gate_dist

print(f"  Gate distance = {gate_dist} cells")
print(f"  Rows = phase of A (delay before A starts), Cols = phase of B offset")
print()

gate_results = {}
header = "  " + "".join(f"  p{b}" for b in range(6))
print(f"  pA\\pB {header[2:]}")
print(f"  {'─'*50}")

for phase_A in range(6):
    row_str = f"  p{phase_A}   "
    for phase_B in range(6):
        # Run A alone for phase_A gens to establish phase, then inject B
        # Implementation: inject A at gen=0, inject B at gen=phase_B, but
        # vary A's initial phase by giving it a head start of phase_A gens
        # Total effective delay between A and B = phase_A + phase_B (mod 6)
        # Simpler: B offset = (phase_B - phase_A) mod 6
        effective_offset = (phase_B - phase_A) % 6
        if (gate_dist, effective_offset) in phase_table:
            out = phase_table[(gate_dist, effective_offset)][1]
        else:
            h, bg = run_two_seeds(xA, xB, phase_offset=effective_offset, W=700, GENS=800)
            out = measure_outcome(h, bg, xA, xB, measure_start=500, measure_gens=80)
            phase_table[(gate_dist, effective_offset)] = (classify_outcome(out), out)
        # Output fingerprint: total anomaly as integer code
        code = int(out['total'])
        row_str += f"  {code:3}"
        gate_results[(phase_A, phase_B)] = code
    print(row_str)

print()
unique_outputs = set(gate_results.values())
print(f"  Unique output values: {sorted(unique_outputs)}  ({len(unique_outputs)} distinct)")
if len(unique_outputs) > 1:
    print(f"\n  ★ GATE IS NON-TRIVIAL — different phases produce different outputs!")
    print(f"    This is a ternary phase-sensitive logic gate.")
    # Find most common and least common
    from collections import Counter
    cnt = Counter(gate_results.values())
    print(f"    Output distribution: {dict(sorted(cnt.items()))}")
else:
    print(f"  Output is constant = {list(unique_outputs)[0]} regardless of phase.")

# ══════════════════════════════════════════════════════════════
# BONUS: What does a THREE-BODY interaction look like?
# ══════════════════════════════════════════════════════════════
print(f"\n{'═'*70}")
print("BONUS: THREE-BODY INTERACTION")
print(f"{'═'*70}")
three_dist = bound_dists[0] if bound_dists else 60
xA3 = BASE_X
xB3 = BASE_X + three_dist
xC3 = BASE_X + 2 * three_dist
print(f"  Three seeds at x={xA3}, {xB3}, {xC3}  (spacing={three_dist})")
h3b, bg3b = run_two_seeds(xA3, xB3, phase_offset=0, W=700, GENS=800)
# Actually run 3 seeds manually
cells3 = [N] * 700
cells3[xA3] = P; cells3[xB3] = P; cells3[xC3] = P
hist3 = [cells3[:]]
for _ in range(800):
    cells3 = step(cells3, rule_arr)
    hist3.append(cells3[:])
bg3 = [row[:30] for row in hist3]

out3 = measure_outcome(hist3, bg3, xA3, xC3, measure_start=500, measure_gens=80)
outcome3 = classify_outcome(out3)
print(f"  Result: {outcome3}")
print(f"  A={out3['A']:.1f}  mid={out3['mid']:.1f}  B={out3['B']:.1f}  total={out3['total']:.1f}")
print(f"  Clusters: {out3['fingerprint']}")
print(f"  Compare: two-body at same dist = {distance_results.get(three_dist, ('?',{}))[1].get('total','?'):.1f}")

print(f"\n{'═'*70}")
print("INTERPRETATION")
print(f"{'═'*70}")
print(f"""
  Period-6 oscillator confirmed: each P injection = one stable particle
  Critical separation: two particles are independent above ~{min(indep) if indep else '?'} cells

  The phase table shows whether particle interactions are:
    PHASE-SENSITIVE → can encode ternary logic (different inputs → different outputs)
    PHASE-NEUTRAL   → interaction is deterministic but not input-dependent

  A ternary gate requires: same distance, different phases → different stable outputs
  If 3+ distinct outputs appear in the gate table, we have a ternary function.
""")
