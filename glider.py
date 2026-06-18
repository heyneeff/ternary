"""
Glider detector for confirmed Class 4 ternary CA rules.

A glider is a localized pattern that moves through the background at constant
velocity. In the spacetime diagram it appears as diagonal structure separated
from the main wavefront. We detect them three ways:

  1. ASCII spacetime diagram — visual inspection (diagonal = moving structure)
  2. Isolated cluster tracking — perturbation islands that move independently
  3. Velocity autocorrelation — score every (period T, velocity S) pair
"""

import math, random
from collections import defaultdict

N, Z, P = -1, 0, 1
TV = [N, Z, P]
TCHAR = {N: '.', Z: '·', P: '#'}

def enc(l,c,r): return (l+1)*9+(c+1)*3+(r+1)

def decode_rule(n):
    rule=[]; x=n
    for _ in range(27): rule.append(TV[x%3]); x//=3
    return rule

def step(cells, rule):
    L=len(cells)
    return [rule[enc(cells[(i-1)%L],cells[i],cells[(i+1)%L])] for i in range(L)]

def run(cells, rule, gens):
    h=[cells[:]]
    for _ in range(gens): cells=step(cells,rule); h.append(cells[:])
    return h

# ── BACKGROUND CHARACTERISATION ───────────────────────────────
def find_background(rule, W=300, warmup=400, seed=7):
    """Run from random N/Z start until settled; return last row as background."""
    random.seed(seed)
    cells=[random.choice([N,Z]) for _ in range(W)]
    rule_arr=decode_rule(rule)
    for _ in range(warmup): cells=step(cells,rule_arr)
    return cells

def bg_period(bg, rule, max_period=40):
    """Find temporal period of the background (how many gens until it repeats)."""
    rule_arr=decode_rule(rule)
    cells=bg[:]
    for t in range(1,max_period+1):
        cells=step(cells,rule_arr)
        if cells==bg: return t
    return None

def bg_spatial_period(bg, max_p=20):
    """Find spatial period of background row."""
    W=len(bg)
    for p in range(1,max_p+1):
        if all(bg[x]==bg[x%p] for x in range(W)): return p
    return None

# ── PERTURBATION EXPERIMENT ───────────────────────────────────
def run_perturb(rule, bg, W=300, GENS=800, perturb_val=P, offset=0):
    """Inject single anomalous cell at center, run, return history."""
    rule_arr=decode_rule(rule)
    cells=bg[:]
    cx=W//2+offset
    # Use whichever trit is NOT dominant in background
    bg_vals=set(bg)
    if perturb_val in bg_vals:
        # try to find a value not in bg
        for v in [P,N,Z]:
            if v not in bg_vals: perturb_val=v; break
    cells[cx]=perturb_val
    return run(cells,rule_arr,GENS)

# ── ASCII SPACETIME ───────────────────────────────────────────
def ascii_spacetime(history, bg, label='', step_every=1, width=80, max_rows=200):
    """
    Print spacetime diagram. Anomalous cells (differ from bg) shown as █.
    Background cells shown as their character. Helps visualise gliders.
    """
    W=len(bg)
    cx=W//2
    x0=max(0,cx-width//2); x1=min(W,cx+width//2)
    GENS=len(history)

    if label: print(f"\n  {label}")
    print(f"  gen  {'─'*( x1-x0)}")

    shown=0
    for g in range(0,GENS,step_every):
        if shown>=max_rows: break
        row=history[g]
        line=''
        for x in range(x0,x1):
            c=row[x]; b=bg[x]
            line+='█' if c!=b else TCHAR.get(c,'?')
        print(f"  {g:4} {line}")
        shown+=1
    print(f"  {'─'*(x1-x0+5)}")

# ── CLUSTER TRACKING ──────────────────────────────────────────
def find_clusters(row, bg, min_gap=3):
    """Find contiguous groups of anomalous cells."""
    perturbed=[x for x in range(len(row)) if row[x]!=bg[x]]
    if not perturbed: return []
    clusters=[]
    cl=[perturbed[0]]
    for x in perturbed[1:]:
        if x-cl[-1]<=min_gap: cl.append(x)
        else: clusters.append(cl); cl=[x]
    clusters.append(cl)
    return [{'cx':sum(c)//len(c),'size':len(c),'cells':c} for c in clusters]

def track_clusters(history, bg, min_gap=3):
    """
    Track cluster trajectories across generations.
    Returns list of trajectories: [{gen, cx, size}, ...]
    """
    all_clusters=[]
    for g,row in enumerate(history):
        cs=find_clusters(row,bg,min_gap)
        for c in cs: c['gen']=g
        all_clusters.append(cs)
    return all_clusters

def find_glider_trajectories(all_clusters, min_lifetime=15, max_vel=5):
    """
    Link clusters across generations to find persistent moving structures.
    Returns list of candidate glider trajectories.
    """
    trajectories=[]
    active={}  # track_id → [cluster_events]
    next_id=0

    for g,clusters in enumerate(all_clusters):
        if not clusters:
            # kill old tracks
            for tid in list(active.keys()):
                if g-active[tid][-1]['gen']>5:
                    trk=active.pop(tid)
                    if len(trk)>=min_lifetime: trajectories.append(trk)
            continue

        matched=set()
        new_active={}

        for tid,trk in active.items():
            last=trk[-1]
            best=None; best_d=999
            for c in clusters:
                d=abs(c['cx']-last['cx'])
                if d<=max_vel and d<best_d:
                    best_d=d; best=c
            if best and id(best) not in matched:
                matched.add(id(best))
                new_active[tid]=trk+[best]
            else:
                if len(trk)>=min_lifetime: trajectories.append(trk)

        # new tracks for unmatched clusters
        for c in clusters:
            if id(c) not in matched:
                new_active[next_id]=[c]; next_id+=1

        active=new_active

    for trk in active.values():
        if len(trk)>=min_lifetime: trajectories.append(trk)

    return trajectories

def analyse_trajectory(trk):
    """Compute velocity, period, stability of a trajectory."""
    if len(trk)<3: return None
    gens=[t['gen'] for t in trk]
    cxs=[t['cx'] for t in trk]
    # Linear regression for velocity
    n=len(trk)
    gm=sum(gens)/n; cm=sum(cxs)/n
    num=sum((gens[i]-gm)*(cxs[i]-cm) for i in range(n))
    den=sum((gens[i]-gm)**2 for i in range(n))
    vel=num/den if den>0 else 0
    # Residuals from linear
    resid=[cxs[i]-(cm+vel*(gens[i]-gm)) for i in range(n)]
    residvar=sum(r**2 for r in resid)/n
    sizes=[t['size'] for t in trk]
    return {
        'velocity':round(vel,3),
        'lifetime':len(trk),
        'start_gen':gens[0], 'end_gen':gens[-1],
        'start_cx':cxs[0], 'end_cx':cxs[-1],
        'mean_size':round(sum(sizes)/n,1),
        'residual_var':round(residvar,3),
        'stable': residvar<2.0,
    }

# ── VELOCITY AUTOCORRELATION ──────────────────────────────────
def velocity_autocorr(history, bg, cx, half_w=40, max_T=20, max_S=15, skip_gens=50):
    """
    For each (T, S), measure what fraction of cells in the window match
    themselves T gens later shifted by S. A glider shows up as a peak
    at its (period, velocity) that's higher than the background baseline.
    """
    W=len(bg); GENS=len(history)
    x0=max(0,cx-half_w); x1=min(W,cx+half_w)
    scores={}

    for T in range(1,max_T+1):
        for S in range(-max_S,max_S+1):
            matches=total=0
            for g in range(skip_gens, GENS-T):
                for x in range(x0,x1):
                    xs=(x+S)%W
                    if history[g][x]==history[g+T][xs]:
                        matches+=1
                    total+=1
            scores[(T,S)]=matches/total if total>0 else 0

    # Baseline: S=0 autocorrelation at each T
    baseline={T:scores[(T,0)] for T in range(1,max_T+1)}
    # Find peaks that beat the baseline
    peaks=[]
    for (T,S),sc in scores.items():
        if S!=0 and sc>baseline[T]+0.02:
            peaks.append((sc-baseline[T],T,S,sc,baseline[T]))
    peaks.sort(reverse=True)
    return peaks[:10], baseline

# ── MAIN ─────────────────────────────────────────────────────
CANDIDATES = [
    (2856969762698, 'N≈50% Z≈50% P=0  — cleanest attractor'),
    (5355161217626, 'N≈49% Z≈2%  P≈49% — binary-ish background'),
    (1251060216861, 'N≈17% Z≈67% P≈17% — symmetric, Z-dominant'),
    (2130435961714, 'N≈67% Z≈17% P≈17% — top score rule'),
    (1672907266213, 'N≈50% Z≈48% P≈2%  — very small P'),
    (5237248727992, 'N≈50% Z≈1%  P≈49% — near-binary'),
]

for rule_num,desc in CANDIDATES:
    print(f"\n{'█'*70}")
    print(f"RULE {rule_num}")
    print(f"  {desc}")
    print(f"{'█'*70}")

    rule_arr=decode_rule(rule_num)
    W=300

    # 1. Background
    bg=find_background(rule_num,W)
    bg_set=set(bg)
    sp=bg_spatial_period(bg)
    tp=bg_period(bg,rule_num)
    print(f"\n  Background: states present={[TCHAR[v] for v in sorted(bg_set)]}")
    print(f"  Spatial period: {sp}   Temporal period: {tp}")

    # 2. Determine what to inject
    inject=None
    for v in [P,N,Z]:
        if v not in bg_set: inject=v; break
    if inject is None:
        # inject least common value
        counts={v:bg.count(v) for v in [N,Z,P]}
        inject=min(counts,key=counts.get)
    print(f"  Injecting: {TCHAR[inject]} ({['N','Z','P'][inject+1]})")

    # 3. Run perturbation
    GENS=600
    history=run_perturb(rule_num,bg,W,GENS,inject)

    # 4. ASCII spacetime — first 120 gens, step every 2
    ascii_spacetime(history,bg,
        label='SPACETIME (█=anomaly, ·/./# =background, every 2nd gen, first 240)',
        step_every=2, width=70, max_rows=120)

    # 5. Cluster tracking
    print(f"\n  CLUSTER TRACKING (min 15 gens lifetime):")
    all_clusters=track_clusters(history,bg,min_gap=4)
    trajs=find_glider_trajectories(all_clusters,min_lifetime=15,max_vel=4)
    if not trajs:
        print("    No persistent isolated clusters found.")
    else:
        for trk in trajs:
            a=analyse_trajectory(trk)
            if not a: continue
            flag='★ GLIDER CANDIDATE' if a['stable'] and abs(a['velocity'])>0.1 else ('(stationary)' if abs(a['velocity'])<0.1 else '(drifting)')
            print(f"    {flag}  vel={a['velocity']:+.3f} cells/gen  "
                  f"lifetime={a['lifetime']} gens  "
                  f"size≈{a['mean_size']}  "
                  f"g{a['start_gen']}→g{a['end_gen']}  "
                  f"x: {a['start_cx']}→{a['end_cx']}  "
                  f"residvar={a['residual_var']}")

    # 6. Velocity autocorrelation
    print(f"\n  VELOCITY AUTOCORRELATION (top hits above background):")
    peaks,baseline=velocity_autocorr(history,bg,W//2,half_w=50,max_T=15,max_S=10,skip_gens=80)
    if not peaks:
        print("    No significant velocity peaks above background.")
    else:
        for excess,T,S,sc,bl in peaks[:5]:
            vel=S/T
            print(f"    Period T={T:2}  Shift S={S:+3}  vel={vel:+.3f}  "
                  f"score={sc:.4f}  baseline={bl:.4f}  excess=+{excess:.4f}")

    print()

print("\n" + "═"*70)
print("SUMMARY")
print("═"*70)
print("""
Interpreting results:
  ★ GLIDER CANDIDATE — isolated cluster moving at nonzero velocity for 15+ gens
  Velocity autocorr peak — pattern repeating with spatial offset (period T, vel S/T)
  Diagonal tracks in ASCII — visual confirmation of movement

  A confirmed glider needs:
    • Isolated from main wavefront (spatially separate)
    • Consistent velocity (low residual variance)
    • Period matching the background temporal period or a multiple of it
    • Visible as diagonal line in ASCII spacetime diagram
""")
