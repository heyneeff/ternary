"""
Emitter hunter for rule 2856969762698.

Three vel=-0.508 gliders were found spaced 30 cells apart at gen 272.
Working backwards: emission interval ≈ 59 gens, source near x=300 (center).

Goals:
  1. Find and characterise the emitter (location, period)
  2. Extract the minimal repeating unit of the vel=-0.508 glider
  3. Confirm the vel=+0.755 glider origin
  4. Check for glider collisions (computation potential)
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

def run_wide(rule_num, W=600, GENS=800):
    rule_arr = decode_rule(rule_num)
    cells = [N]*W; cells[W//2] = P
    history = [cells[:]]
    for _ in range(GENS):
        cells = step(cells, rule_arr)
        history.append(cells[:])
    return history

def extract_bg(history, left_w=30):
    return [row[:left_w] for row in history]

def bg_temporal_period(bg_rows, search_start=80, max_p=60):
    ref = bg_rows[search_start]
    for t in range(1, max_p+1):
        if len(bg_rows) > search_start+t and bg_rows[search_start+t] == ref:
            return t
    return None

def bg_velocity(bg_rows, period, W=30):
    if not period: return 0, 0
    best_s, best_sc = 0, 0
    for s in range(-period, period+1):
        m = tot = 0
        for g in range(100, len(bg_rows)-period, period):
            for x in range(W):
                xs = (x+s) % W
                if bg_rows[g][x] == bg_rows[g+period][xs]: m += 1
                tot += 1
        sc = m/tot if tot else 0
        if sc > best_sc: best_sc = sc; best_s = s
    return best_s, best_sc

# ── ASCII FOCUSED ZOOM ────────────────────────────────────────
def ascii_zoom(history, bg_rows, bg_W,
               x_lo, x_hi, g_lo, g_hi, step_g=1, label=''):
    """Print a focused window of the spacetime diagram."""
    if label: print(f"\n  {label}")
    w = x_hi - x_lo
    print(f"  {'gen':>4}  x={x_lo}{'→':>{w//2-6}}{x_hi}")
    print(f"  {'':4}  {'─'*w}")
    for g in range(g_lo, min(g_hi, len(history)), step_g):
        row = history[g]; bg = bg_rows[g]
        line = ''
        for x in range(x_lo, x_hi):
            c = row[x]; b = bg[x % bg_W]
            line += '#' if c == P and c != b else ('.' if c == N and c != b else ('·' if c == Z and c != b else TCH.get(c,'?')))
        print(f"  {g:4}  {line}")
    print(f"  {'─'*(w+6)}")

def ascii_anomaly(history, bg_rows, bg_W,
                  x_lo, x_hi, g_lo, g_hi, step_g=1, label=''):
    """Print anomaly-only view: █ where cell differs from bg, space otherwise."""
    if label: print(f"\n  {label}")
    w = x_hi - x_lo
    print(f"  {'gen':>4}  x={x_lo}..{x_hi}")
    print(f"  {'':4}  {'─'*w}")
    for g in range(g_lo, min(g_hi, len(history)), step_g):
        row = history[g]; bg = bg_rows[g]
        line = ''.join('█' if row[x] != bg[x % bg_W] else ' ' for x in range(x_lo, x_hi))
        if line.strip():  # skip blank rows
            print(f"  {g:4}  {line}")
    print(f"  {'─'*(w+6)}")

# ── EMITTER FINDER ────────────────────────────────────────────
def find_emitter(history, bg_rows, bg_W,
                 cx, search_half=40, g_start=30, g_end=500):
    """
    Look for a region near cx that:
      1. Stays anomalous for many generations (the emitter core)
      2. Periodically sheds isolated groups leftward or rightward
    Returns: (emitter_x, emitter_size, emission_period, emission_gen_list)
    """
    # Find which cells near cx are *persistently* anomalous
    x0 = max(0, cx - search_half)
    x1 = min(len(history[0]), cx + search_half)
    persist = {}  # x → count of gens it's anomalous
    for g in range(g_start, min(g_end, len(history))):
        row = history[g]; bg = bg_rows[g]
        for x in range(x0, x1):
            if row[x] != bg[x % bg_W]:
                persist[x] = persist.get(x, 0) + 1

    if not persist: return None

    # Cluster persistent cells
    hotspots = sorted([x for x, cnt in persist.items() if cnt > (g_end-g_start)*0.3])
    if not hotspots: return None

    # Find the center of the hotspot
    emitter_cx = sum(hotspots) // len(hotspots)

    # Find emission events: moments when an isolated blob appears to the left of emitter
    # and starts drifting — i.e., anomaly appears at x < emitter_cx - 10 that wasn't there last gen
    emission_gens = []
    prev_left_anom = set()
    for g in range(g_start+1, min(g_end, len(history))):
        row = history[g]; bg = bg_rows[g]
        left_anom = {x for x in range(x0, emitter_cx-8)
                     if row[x] != bg[x % bg_W]}
        # New anomalies that weren't there last gen = freshly emitted
        fresh = left_anom - prev_left_anom
        if len(fresh) >= 2:  # cluster appeared
            emission_gens.append(g)
        prev_left_anom = left_anom

    # Consolidate close emission events (within 5 gens = one emission)
    if emission_gens:
        merged = [emission_gens[0]]
        for g in emission_gens[1:]:
            if g - merged[-1] > 8:
                merged.append(g)
        # Estimate period from gaps
        if len(merged) >= 2:
            gaps = [merged[i]-merged[i-1] for i in range(1, len(merged))]
            avg_period = sum(gaps) / len(gaps)
        else:
            avg_period = None
        return emitter_cx, len(hotspots), avg_period, merged
    return emitter_cx, len(hotspots), None, []

# ── MINIMAL PATTERN EXTRACTOR ─────────────────────────────────
def extract_glider_pattern(history, bg_rows, bg_W, x_center, gen, half_w=15):
    """Extract raw cell values of a glider at a specific spacetime location."""
    row = history[gen]; bg = bg_rows[gen]
    x0 = max(0, x_center - half_w)
    x1 = min(len(row), x_center + half_w)
    cells  = row[x0:x1]
    bkgnd  = [bg[x % bg_W] for x in range(x0, x1)]
    anom   = [(x-x0, cells[i], bkgnd[i]) for i, x in enumerate(range(x0, x1))
               if cells[i] != bkgnd[i]]
    chars  = ''.join(TCH.get(c, '?') for c in cells)
    return {'cells': cells, 'background': bkgnd, 'anomalies': anom, 'display': chars}

# ── PERIOD DETECTOR for a fixed location ─────────────────────
def measure_local_period(history, bg_rows, bg_W,
                          x_center, half_w=8, g_start=100, max_p=120):
    """
    Extract a small window around x_center at each gen.
    Find the shortest period T such that window[g] == window[g+T] for many g.
    """
    x0 = max(0, x_center - half_w)
    x1 = min(len(history[0]), x_center + half_w)
    snapshots = []
    for g in range(g_start, min(g_start+400, len(history))):
        row = history[g]; bg = bg_rows[g]
        snap = tuple(row[x] - bg[x % bg_W] for x in range(x0, x1))  # anomaly delta
        snapshots.append(snap)

    n = len(snapshots)
    for T in range(2, min(max_p, n//3)):
        matches = sum(1 for i in range(n-T) if snapshots[i] == snapshots[i+T])
        frac = matches / (n - T)
        if frac > 0.80:
            return T, frac
    return None, 0.0

# ── COLLISION REGION SEARCH ───────────────────────────────────
def find_collisions(history, bg_rows, bg_W, cx, g_start=300, g_end=700):
    """
    Look for regions where two anomaly clusters overlap / merge — potential
    glider collision. Signs: sudden size increase, value change in anomaly cluster.
    """
    W = len(history[0])
    events = []
    prev_clusters = []
    for g in range(g_start, min(g_end, len(history))):
        row = history[g]; bg = bg_rows[g]
        anoms = [x for x in range(W) if row[x] != bg[x % bg_W]]
        if not anoms: continue
        # Cluster
        clusters = []
        cl = [anoms[0]]
        for x in anoms[1:]:
            if x - cl[-1] <= 6: cl.append(x)
            else: clusters.append(cl); cl = [x]
        clusters.append(cl)
        # Check for merges: a cluster that's much larger than nearby prev clusters
        for cl in clusters:
            cl_cx = sum(cl) // len(cl)
            # Is this cluster bigger than expected?
            nearby = [pc for pc in prev_clusters
                      if abs(sum(pc)//len(pc) - cl_cx) < 20]
            if nearby:
                max_prev = max(len(pc) for pc in nearby)
                if len(cl) > max_prev * 1.8 and len(cl) > 10:
                    events.append({'gen': g, 'cx': cl_cx, 'size': len(cl),
                                   'prev_size': max_prev})
        prev_clusters = clusters
    return events

# ══════════════════════════════════════════════════════════════
RULE = 2856969762698
W, GENS = 600, 800

print(f"{'█'*72}")
print(f"EMITTER ANALYSIS — Rule {RULE}")
print(f"W={W}  GENS={GENS}")
print(f"{'█'*72}")

print(f"\n  Running simulation...")
history = run_wide(RULE, W, GENS)
bg_rows = extract_bg(history, left_w=30)
cx = W // 2  # = 300

# Background characterisation
tp = bg_temporal_period(bg_rows, search_start=80, max_p=60)
bv_shift, bv_score = bg_velocity(bg_rows, tp or 1, W=30)
bg_vel = bv_shift / (tp or 1)
print(f"\n  Background: period={tp}, drift={bv_shift:+d}/period, vel={bg_vel:+.4f}")

# ── 1. EMITTER REGION — wide view, center strip ───────────────
print()
ascii_anomaly(history, bg_rows, 30,
              x_lo=cx-60, x_hi=cx+60,
              g_lo=0, g_hi=400, step_g=1,
              label='EMITTER REGION (x=240–360, gens 0–400) █=anomaly, space=background')

# ── 2. GLIDERS IN FLIGHT — left side ─────────────────────────
print()
ascii_anomaly(history, bg_rows, 30,
              x_lo=cx-150, x_hi=cx+20,
              g_lo=100, g_hi=400, step_g=1,
              label='LEFT GLIDER FLIGHT PATH (x=150–320, gens 100–400)')

# ── 3. EMITTER FINDER ─────────────────────────────────────────
print(f"\n  EMITTER ANALYSIS:")
result = find_emitter(history, bg_rows, 30,
                       cx=cx, search_half=50, g_start=30, g_end=400)
if result:
    em_cx, em_size, em_period, em_events = result
    print(f"    Emitter center x ≈ {em_cx}")
    print(f"    Persistent hotspot width : {em_size} cells")
    print(f"    Emission events detected  : {len(em_events)}")
    if em_events:
        print(f"    First few events at gens  : {em_events[:8]}")
    if em_period:
        print(f"    Estimated emission period : {em_period:.1f} gens")
    else:
        print(f"    Could not estimate period (too few events)")

    # Measure local period at emitter
    lp, lp_frac = measure_local_period(history, bg_rows, 30,
                                        em_cx, half_w=8, g_start=80, max_p=120)
    if lp:
        print(f"    Local temporal period at x={em_cx}: T={lp} (match frac={lp_frac:.3f})")
    else:
        print(f"    No clean local period found at x={em_cx}")
else:
    print("    No persistent emitter found.")

# ── 4. GLIDER PATTERN AT KNOWN LOCATION ──────────────────────
# From glider2.py: one instance at g284, x≈172 (midpoint of g272→g296, x:179→166)
print(f"\n  GLIDER PATTERN EXTRACTION:")
# Three glider copies at g=272: x≈179, 209, 239
for label, g_samp, x_samp in [
    ("glider A (leftmost)", 272, 179),
    ("glider B (middle)",   272, 209),
    ("glider C (rightmost)",272, 239),
]:
    pat = extract_glider_pattern(history, bg_rows, 30, x_samp, g_samp, half_w=12)
    print(f"    {label} at g={g_samp}, x≈{x_samp}:")
    print(f"      display : {pat['display']}")
    print(f"      anomalies: {[(dx, TCH[v]) for dx,v,_ in pat['anomalies'][:15]]}")

# ── 5. FAST GLIDER CHARACTERISATION ──────────────────────────
# vel=+0.755 glider was in the CO-MOVING frame (background moving at -1.0)
# In lab frame: vel = -1.0 + 0.755 = -0.245? Or is the co-moving frame
# shifting things differently? Let's check the raw history around g240, x≈cx+30
print(f"\n  FAST GLIDER REGION (right side of center, gens 150-350):")
ascii_anomaly(history, bg_rows, 30,
              x_lo=cx-20, x_hi=cx+100,
              g_lo=150, g_hi=400, step_g=1,
              label='RIGHT-SIDE ANOMALIES (x=280–400, gens 150–400)')

# ── 6. COLLISION SEARCH ───────────────────────────────────────
print(f"\n  COLLISION SEARCH (gens 300–700):")
collisions = find_collisions(history, bg_rows, 30, cx, g_start=300, g_end=700)
if collisions:
    print(f"    {len(collisions)} potential collision events:")
    for ev in collisions[:10]:
        print(f"    gen={ev['gen']}  cx={ev['cx']}  size={ev['size']} (was {ev['prev_size']})")
else:
    print("    No clear collision events detected.")

# ── 7. EMITTER CLOSE-UP — very tight window ───────────────────
print()
ascii_anomaly(history, bg_rows, 30,
              x_lo=cx-25, x_hi=cx+25,
              g_lo=0, g_hi=250, step_g=1,
              label='EMITTER CLOSE-UP (x=275–325, gens 0–250) — looking for periodicity')

# ── 8. VELOCITY CONFIRMATION ─────────────────────────────────
print(f"\n  VELOCITY FINGERPRINT — checking for consistent -0.5 signal:")
print(f"  (T=2, S=-1 should match at most places if vel=-0.5 glider is periodic)")
x_left = cx - 100  # region where gliders travel
match_count = 0; total = 0
for g in range(100, min(700, len(history)-2)):
    row_g  = history[g]
    row_g2 = history[g+2]
    bg_g   = bg_rows[g]
    bg_g2  = bg_rows[g+2]
    for x in range(x_left, cx):
        c = row_g[x]; b = bg_g[x % 30]
        if c != b:  # anomalous cell
            xs = (x - 1) % W
            cT = row_g2[xs]; bT = bg_g2[xs % 30]
            if c == cT: match_count += 1
            total += 1
frac = match_count / total if total else 0
print(f"    T=2, S=-1 autocorr on left anomalies: {frac:.4f} ({match_count}/{total})")

print()
print("═"*72)
print("INTERPRETATION GUIDE:")
print("  Periodic emitter at fixed x → confirmed glider gun")
print("  Emission period T → glider spacing = T × |vel| cells")
print("  Three gliders spaced 30 cells, vel≈-0.5 → emission period ≈ 60 gens")
print("  Collision event → size spike, trit value change at merge point")
