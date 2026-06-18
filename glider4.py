"""
Deep characterisation of the stationary structure in rule 2130435961714.

In glider2.py we found:
  - Background moves at -1.0 cells/gen (period=2, drift=-2/period)
  - In co-moving frame: structure vel=+1.0 → lab-frame vel = 0 (STATIONARY)
  - Stays near x=300 for 122 gens (full observation window)
  - Size ≈ 72 cells, rvar=0.137

Questions to answer:
  1. Does it survive past 2000 gens? (was it just a long transient?)
  2. Is it truly isolated — or is it the wavefront tip?
  3. What is its internal period?
  4. Two-seed: start TWO P cells — do two independent structures form?
  5. Interaction: if two structures form, do they collide when placed close enough?
"""

N, Z, P = -1, 0, 1
TV = [N, Z, P]
TCH = {N: '.', Z: '·', P: '#'}

def enc(l, c, r): return (l+1)*9 + (c+1)*3 + (r+1)

def decode_rule(n):
    rule = []; x = n
    for _ in range(27): rule.append(TV[x % 3]); x //= 3
    return rule

def step(cells, rule):
    L = len(cells)
    return [rule[enc(cells[(i-1)%L], cells[i], cells[(i+1)%L])] for i in range(L)]

RULE = 2130435961714
rule_arr = decode_rule(RULE)

# Background characterisation from glider2.py: period=2, drift=-2, vel=-1.0
BG_PERIOD = 2
BG_DRIFT  = -2        # cells per period
BG_VEL    = BG_DRIFT / BG_PERIOD  # = -1.0

def run_from_seeds(seeds, W=800, GENS=2000, bg_val=N):
    """
    seeds: list of (x, val) to inject; everything else starts as bg_val.
    Returns (history, bg_rows).
    """
    cells = [bg_val] * W
    for x, v in seeds:
        cells[x] = v
    history = [cells[:]]
    for _ in range(GENS):
        cells = step(cells, rule_arr)
        history.append(cells[:])
    bg_rows = [row[:30] for row in history]  # left-edge background
    return history, bg_rows

def comoving_shift(g, drift=BG_DRIFT, period=BG_PERIOD):
    """How many cells to shift row g to put background at rest."""
    return round(drift / period * g)

def comoving_row(row, g, W):
    s = comoving_shift(g)
    return [row[(x + s) % W] for x in range(W)]

def anomaly_density(row, bg_row, bg_W=30):
    return sum(1 for x in range(len(row)) if row[x] != bg_row[x % bg_W]) / len(row)

def anomaly_window(history, bg_rows, cx, half_w=50, g_lo=0, g_hi=None, bg_W=30):
    """Count anomalous cells in a window [cx-half_w, cx+half_w] per gen."""
    W = len(history[0])
    g_hi = g_hi or len(history)
    x0 = max(0, cx - half_w); x1 = min(W, cx + half_w)
    counts = []
    for g in range(g_lo, min(g_hi, len(history))):
        row = history[g]; bg = bg_rows[g]
        cnt = sum(1 for x in range(x0, x1) if row[x] != bg[x % bg_W])
        counts.append(cnt)
    return counts

def find_period_at(history, bg_rows, cx, half_w=40, g_start=200, max_p=60, bg_W=30):
    """
    Extract anomaly pattern in a window near cx, find its period.
    Uses the lab frame (NOT co-moving) since the structure is stationary.
    """
    W = len(history[0])
    x0 = max(0, cx - half_w); x1 = min(W, cx + half_w)
    snapshots = []
    for g in range(g_start, min(g_start+600, len(history))):
        row = history[g]; bg = bg_rows[g]
        snap = tuple(row[x] - bg[x % bg_W] for x in range(x0, x1))
        snapshots.append((g, snap))

    n = len(snapshots)
    best = (None, 0.0)
    for T in range(1, min(max_p+1, n//4)):
        hits = sum(1 for i in range(n - T) if snapshots[i][1] == snapshots[i+T][1])
        frac = hits / (n - T)
        if frac > best[1]:
            best = (T, frac)
        if frac > 0.92:
            return T, frac
    return best

def ascii_window(history, bg_rows, cx, half_w=45, g_lo=0, g_hi=200,
                 step_g=1, bg_W=30, label='', comoving=False):
    W = len(history[0])
    x0 = max(0, cx - half_w); x1 = min(W, cx + half_w)
    if label: print(f"\n  {label}")
    print(f"  {'gen':>5}  x={x0}..{x1}")
    print(f"  {'':5}  {'─'*(x1-x0)}")
    for g in range(g_lo, min(g_hi+1, len(history)), step_g):
        if comoving:
            row = comoving_row(history[g], g, W)
            bg = bg_rows[g]
        else:
            row = history[g]; bg = bg_rows[g]
        line = ''.join('█' if row[x] != bg[x % bg_W] else ' ' for x in range(x0, x1))
        if line.strip() or g % 10 == 0:
            print(f"  {g:5}  {line}")
    print(f"  {'─'*(x1-x0+7)}")

def print_structure_at(history, bg_rows, cx, gen, half_w=40, bg_W=30):
    """Print exact trit values of anomaly near cx at a specific gen."""
    W = len(history[0])
    x0 = max(0, cx - half_w); x1 = min(W, cx + half_w)
    row = history[gen]; bg = bg_rows[gen]
    anoms = [(x, row[x], bg[x % bg_W]) for x in range(x0, x1)
             if row[x] != bg[x % bg_W]]
    print(f"    gen {gen}: {len(anoms)} anomalous cells near x={cx}")
    if anoms:
        xs = [a[0] for a in anoms]
        vals = ''.join(TCH[a[1]] for a in anoms)
        print(f"    x range: {xs[0]}–{xs[-1]}  (width {xs[-1]-xs[0]+1})")
        print(f"    values : {vals}")

# ══════════════════════════════════════════════════════════════
print(f"{'█'*72}")
print(f"DEEP PROBE — Rule {RULE}")
print(f"Background vel={BG_VEL:+.1f}  (period={BG_PERIOD}, drift={BG_DRIFT}/period)")
print(f"{'█'*72}")

# ─── TEST 1: LONG-RUN STABILITY ───────────────────────────────
print(f"\n{'═'*60}")
print("TEST 1: Long-run stability (W=800, 2000 gens, single seed)")
print(f"{'═'*60}")
W1 = 800; GENS1 = 2000; cx1 = W1 // 2
print(f"  Running {W1}×{GENS1}...")
h1, bg1 = run_from_seeds([(cx1, P)], W=W1, GENS=GENS1)

# Track anomaly density near the injection point over time
print(f"\n  Anomaly count in window x=[{cx1-50},{cx1+50}] over time:")
ac = anomaly_window(h1, bg1, cx1, half_w=50, bg_W=30)
checkpoints = [100, 250, 500, 750, 1000, 1250, 1500, 1750, 2000]
for g in checkpoints:
    if g < len(ac):
        bg_density = anomaly_density(h1[g], bg1[g])
        print(f"    gen {g:5}: window_count={ac[g]:4}  global_density={bg_density:.4f}")

print(f"\n  Anomaly near center (is it still there at late gens?):")
print_structure_at(h1, bg1, cx1, 500)
print_structure_at(h1, bg1, cx1, 1000)
print_structure_at(h1, bg1, cx1, 1500)
print_structure_at(h1, bg1, cx1, 2000)

# ASCII of lab-frame anomaly near center, sampled over full run
ascii_window(h1, bg1, cx1, half_w=50, g_lo=0, g_hi=2000,
             step_g=10, label='LAB FRAME near x=400 (every 10 gens) — structure should stay fixed')

# ─── TEST 2: INTERNAL PERIOD ──────────────────────────────────
print(f"\n{'═'*60}")
print("TEST 2: Internal period of the structure")
print(f"{'═'*60}")
lp, frac = find_period_at(h1, bg1, cx1, half_w=40, g_start=300, max_p=60)
if lp:
    print(f"  Period T={lp}  (match fraction={frac:.4f})")
    # Show two snapshots T gens apart to confirm
    print_structure_at(h1, bg1, cx1, 400)
    print_structure_at(h1, bg1, cx1, 400 + lp)
else:
    print(f"  No clean period found (best frac={frac:.4f})")
    # Try longer search
    lp2, frac2 = find_period_at(h1, bg1, cx1, half_w=40, g_start=300, max_p=200)
    print(f"  Extended search: T={lp2}  frac={frac2:.4f}")

# Close-up of center region (lab frame, showing structure staying put)
ascii_window(h1, bg1, cx1, half_w=35, g_lo=150, g_hi=350,
             step_g=1, label='LAB FRAME close-up gen 150–350 (structure should be stationary blob)')

# ─── TEST 3: TWO-SEED EXPERIMENT ─────────────────────────────
print(f"\n{'═'*60}")
print("TEST 3: Two-seed experiment — independent structures?")
print(f"{'═'*60}")
W3 = 900; GENS3 = 1000
seedA = W3 // 3        # x = 300
seedB = 2 * W3 // 3    # x = 600
print(f"  Seed A at x={seedA}, Seed B at x={seedB}  (gap={seedB-seedA} cells)")
print(f"  Running {W3}×{GENS3}...")
h3, bg3 = run_from_seeds([(seedA, P), (seedB, P)], W=W3, GENS=GENS3)

print(f"\n  Anomaly near seed A (x={seedA}):")
ac_A = anomaly_window(h3, bg3, seedA, half_w=40, g_lo=0, g_hi=GENS3, bg_W=30)
print(f"\n  Anomaly near seed B (x={seedB}):")
ac_B = anomaly_window(h3, bg3, seedB, half_w=40, g_lo=0, g_hi=GENS3, bg_W=30)

for g in [100, 300, 500, 700, 900]:
    if g < GENS3:
        a = ac_A[g] if g < len(ac_A) else '?'
        b = ac_B[g] if g < len(ac_B) else '?'
        print(f"    gen {g}: A_count={a:4}  B_count={b:4}")

print_structure_at(h3, bg3, seedA, 500, half_w=30)
print_structure_at(h3, bg3, seedB, 500, half_w=30)

# Wide ASCII showing both structures
ascii_window(h3, bg3, (seedA+seedB)//2, half_w=(seedB-seedA)//2+20,
             g_lo=0, g_hi=600, step_g=5,
             label=f'TWO-SEED spacetime (every 5 gens) — two blobs should form at x={seedA} and x={seedB}')

# ─── TEST 4: COLLISION — seeds close together ─────────────────
print(f"\n{'═'*60}")
print("TEST 4: Collision test — seeds 100 cells apart")
print(f"{'═'*60}")
W4 = 600; GENS4 = 800
cA = 200; cB = 300  # close together, might interact
print(f"  Seed A at x={cA}, Seed B at x={cB}  (gap={cB-cA} cells)")
print(f"  Running {W4}×{GENS4}...")
h4, bg4 = run_from_seeds([(cA, P), (cB, P)], W=W4, GENS=GENS4)

# Compare to single-seed (check if two-seed is just superposition)
print(f"\n  Collision region (between x={cA} and x={cB}):")
ascii_window(h4, bg4, (cA+cB)//2, half_w=80,
             g_lo=0, g_hi=600, step_g=4,
             label=f'COLLISION spacetime (every 4 gens)')

ac4_A = anomaly_window(h4, bg4, cA, half_w=30, g_lo=0, g_hi=GENS4, bg_W=30)
ac4_B = anomaly_window(h4, bg4, cB, half_w=30, g_lo=0, g_hi=GENS4, bg_W=30)
ac4_mid = anomaly_window(h4, bg4, (cA+cB)//2, half_w=10, g_lo=0, g_hi=GENS4, bg_W=30)
print(f"\n  Anomaly counts (A=near x={cA}, mid=gap, B=near x={cB}):")
for g in [50, 100, 200, 300, 400, 500, 600, 700]:
    if g < GENS4:
        a = ac4_A[g]; b = ac4_B[g]; m = ac4_mid[g]
        print(f"    gen {g}: A={a:4}  mid={m:3}  B={b:4}")

# ─── SUMMARY ─────────────────────────────────────────────────
print(f"\n{'═'*72}")
print("SUMMARY CHECKLIST")
print(f"{'═'*72}")
print("""
  Test 1 — Survival:     window_count near cx should stay nonzero at gen 2000
  Test 2 — Period:       T found means it's an oscillator, not a random blob
  Test 3 — Independence: two seeds should give two separate persistent structures
  Test 4 — Collision:    mid-region anomaly spike at overlap = interaction event

  If Test 1+2+3 pass: we have a confirmed periodic particle (oscillator)
  If Test 4 also shows interaction: ternary glider computation is possible
""")
