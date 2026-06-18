"""
Focused glider detector for rule 2130435961714 and 2856969762698.

Key fixes over glider.py:
  1. Wide field (W=600) to avoid periodic-boundary artifacts
  2. Background extracted from LEFT EDGE of the spacetime diagram
     (cells the initial perturbation hasn't reached yet)
  3. Co-moving frame: subtract background velocity so background is static,
     gliders appear as isolated moving structures
  4. Perturbation-boundary tracking: find edge velocities left and right,
     anything faster/slower is a candidate glider escaping the main mass
"""

import math

N, Z, P = -1, 0, 1
TV  = [N, Z, P]
TCH = {N:'.', Z:'·', P:'#'}

def enc(l,c,r): return (l+1)*9+(c+1)*3+(r+1)

def decode_rule(n):
    rule=[]; x=n
    for _ in range(27): rule.append(TV[x%3]); x//=3
    return rule

def step(cells, rule):
    L=len(cells)
    return [rule[enc(cells[(i-1)%L],cells[i],cells[(i+1)%L])] for i in range(L)]

def run_wide(rule_num, W=600, GENS=800):
    """Start from single P in all-N, wide field, no wrap artifacts early on."""
    rule_arr=decode_rule(rule_num)
    cells=[N]*W; cells[W//2]=P
    history=[cells[:]]
    for _ in range(GENS):
        cells=step(cells,rule_arr); history.append(cells[:])
    return history

# ── BACKGROUND FROM LEFT EDGE ─────────────────────────────────
def extract_bg(history, left_w=30):
    """Left edge rows (perturbation hasn't reached here yet)."""
    return [row[:left_w] for row in history]

def bg_temporal_period(bg_rows, search_start=80, max_p=60):
    ref=bg_rows[search_start]
    for t in range(1,max_p+1):
        if len(bg_rows)>search_start+t and bg_rows[search_start+t]==ref:
            return t
    return None

def bg_velocity(bg_rows, period, W=30):
    """Find spatial drift of background per period."""
    if not period: return 0,0
    best_s,best_sc=0,0
    for s in range(-period,period+1):
        m=tot=0
        for g in range(100,len(bg_rows)-period,period):
            for x in range(W):
                xs=(x+s)%W
                if bg_rows[g][x]==bg_rows[g+period][xs]: m+=1
                tot+=1
        sc=m/tot if tot else 0
        if sc>best_sc: best_sc=sc; best_s=s
    return best_s,best_sc

# ── PERTURBATION BOUNDARY ─────────────────────────────────────
def perturb_extent(history, bg_rows, bg_W=30):
    """
    At each gen, find leftmost and rightmost cells that differ from
    what the background would predict (using left-edge as reference).
    Returns (left_edge_x, right_edge_x) per generation.
    """
    W=len(history[0]); cx=W//2
    extents=[]
    for g,row in enumerate(history):
        bg=bg_rows[g]
        # Left boundary
        lx=cx
        for x in range(cx,0,-1):
            bg_x=bg[x%bg_W] if x<bg_W else bg[x%bg_W]
            if row[x]!=bg_x: lx=x; break
        # Right boundary
        rx=cx
        for x in range(cx,W):
            bg_x=bg[x%bg_W]
            if row[x]!=bg_x: rx=x; break
        extents.append((lx,rx))
    return extents

# ── CO-MOVING FRAME ───────────────────────────────────────────
def comoving_history(history, bg_rows, bg_W=30, bg_vel_per_period=0, period=1):
    """
    Transform history to background rest frame.
    Shift each row by -round(bg_vel_per_period/period * g) so background
    becomes stationary. Anomalies will appear as isolated moving structures.
    """
    if not period or bg_vel_per_period==0:
        return history  # already stationary
    W=len(history[0])
    result=[]
    for g,row in enumerate(history):
        shift=round(bg_vel_per_period/period * g)
        shifted=[row[(x+shift)%W] for x in range(W)]
        result.append(shifted)
    return result

# ── ANOMALY MAP ───────────────────────────────────────────────
def anomaly_row(row, bg_row, bg_W):
    """Return list of (x, cell_value) where cell differs from expected bg."""
    return [(x,row[x]) for x in range(len(row)) if row[x]!=bg_row[x%bg_W]]

# ── ASCII SPACETIME ───────────────────────────────────────────
BLOCK='█'; DIMB='░'

def ascii_full(history, bg_rows, bg_W=30,
               x_start=None, x_end=None,
               step_g=1, max_rows=150, label=''):
    W=len(history[0]); cx=W//2
    if x_start is None: x_start=max(0,cx-60)
    if x_end   is None: x_end  =min(W,cx+60)
    if label: print(f"\n  {label}")
    print(f"  {'gen':>4}  {'─'*(x_end-x_start)}")
    shown=0
    for g in range(0,len(history),step_g):
        if shown>=max_rows: break
        row=history[g]; bg=bg_rows[g]
        line=''
        for x in range(x_start,x_end):
            c=row[x]; b=bg[x%bg_W]
            line+=BLOCK if c!=b else TCH.get(c,'?')
        print(f"  {g:4}  {line}")
        shown+=1
    print(f"  {'─'*(x_end-x_start+6)}")

# ── ISOLATED STRUCTURE FINDER ─────────────────────────────────
def find_isolated(history, bg_rows, bg_W=30,
                  skip=60, gap=6, min_life=20, max_vel=8):
    """
    In each row, find anomaly clusters. Track clusters that remain
    isolated (separated from the main wavefront by at least 'gap' cells).
    """
    W=len(history[0]); cx=W//2
    tracks={}; next_id=0; finished=[]

    for g in range(skip,len(history)):
        row=history[g]; bg=bg_rows[g]
        anoms=[x for x in range(W) if row[x]!=bg[x%bg_W]]
        if not anoms: tracks={}; continue

        # Find clusters
        clusters=[]
        cl=[anoms[0]]
        for x in anoms[1:]:
            if x-cl[-1]<=gap: cl.append(x)
            else: clusters.append(cl); cl=[x]
        clusters.append(cl)

        # Main mass = largest cluster or cluster nearest cx
        main_cl=max(clusters,key=len)
        main_cx=sum(main_cl)//len(main_cl)
        main_left=min(main_cl); main_right=max(main_cl)

        # Isolated = clusters separated from main by >gap
        isolated=[cl for cl in clusters
                  if cl is not main_cl and
                  (min(cl)>main_right+gap or max(cl)<main_left-gap)]

        # Match isolated clusters to existing tracks
        matched=set()
        new_tracks={}
        for tid,trk in tracks.items():
            prev_cx=trk[-1]['cx']
            best=None; bd=999
            for ic in isolated:
                icx=sum(ic)//len(ic)
                d=abs(icx-prev_cx)
                if d<=max_vel and d<bd:
                    bd=d; best=ic
            if best and id(best) not in matched:
                matched.add(id(best))
                icx=sum(best)//len(best)
                new_tracks[tid]=trk+[{'gen':g,'cx':icx,'size':len(best),
                                       'cells':best[:]}]
            else:
                if len(trk)>=min_life: finished.append(trk)

        for ic in isolated:
            if id(ic) not in matched:
                icx=sum(ic)//len(ic)
                new_tracks[next_id]=[{'gen':g,'cx':icx,'size':len(ic),
                                       'cells':ic[:]}]
                next_id+=1
        tracks=new_tracks

    for trk in tracks.values():
        if len(trk)>=min_life: finished.append(trk)

    return finished

def analyse_track(trk):
    gens=[t['gen'] for t in trk]; cxs=[t['cx'] for t in trk]
    n=len(trk)
    gm=sum(gens)/n; cm=sum(cxs)/n
    num=sum((gens[i]-gm)*(cxs[i]-cm) for i in range(n))
    den=sum((gens[i]-gm)**2 for i in range(n))
    vel=num/den if den>0 else 0
    resid=[cxs[i]-(cm+vel*(gens[i]-gm)) for i in range(n)]
    rvar=sum(r**2 for r in resid)/n
    sizes=[t['size'] for t in trk]
    return {'vel':round(vel,3),'life':n,
            'g0':gens[0],'g1':gens[-1],
            'cx0':cxs[0],'cx1':cxs[-1],
            'sz':round(sum(sizes)/n,1),
            'rvar':round(rvar,3),
            'glider': rvar<3.0 and abs(vel)>0.05}

# ── VELOCITY SCAN (focused on perturbation center) ────────────
def vel_scan(history, bg_rows, bg_W=30,
             cx_range=80, skip=80, max_T=20, max_S=12):
    W=len(history[0]); cx=W//2
    x0=max(0,cx-cx_range); x1=min(W,cx+cx_range)
    GENS=len(history)
    scores={}
    for T in range(1,max_T+1):
        for S in range(-max_S,max_S+1):
            m=tot=0
            for g in range(skip,GENS-T):
                bg=bg_rows[g]; bgT=bg_rows[g+T]
                for x in range(x0,x1):
                    c=history[g][x]; b=bg[x%bg_W]
                    cT=history[g+T][(x+S)%W]; bT=bgT[(x+S)%bg_W]
                    # Only score anomalous cells (differ from bg)
                    if c!=b or cT!=bT:
                        if c==cT: m+=1  # anomaly persists with shift
                        tot+=1
            scores[(T,S)]=m/tot if tot>0 else 0
    # Baseline: S=0
    base={T:scores.get((T,0),0) for T in range(1,max_T+1)}
    peaks=[]
    for (T,S),sc in scores.items():
        if S!=0 and tot>0:
            exc=sc-base.get(T,0)
            if exc>0.05:
                peaks.append((exc,T,S,sc,base.get(T,0)))
    peaks.sort(reverse=True)
    return peaks[:12],base

# ── RUN ──────────────────────────────────────────────────────
TARGETS=[
    (2130435961714, 'bg period=6, multiple velocities — most complex'),
    (2856969762698, 'vel=+0.5 (half-integer) — ternary-native signature'),
]

for rule_num,desc in TARGETS:
    print(f"\n{'█'*72}")
    print(f"RULE {rule_num}")
    print(f"  {desc}")
    print(f"{'█'*72}")

    W=600; GENS=700
    print(f"\n  Running W={W} × {GENS} gens...")
    history=run_wide(rule_num,W,GENS)
    bg_rows=extract_bg(history,left_w=30)

    # Background characterisation
    tp=bg_temporal_period(bg_rows,search_start=80,max_p=60)
    bv_shift,bv_score=bg_velocity(bg_rows,tp or 1,W=30)
    bg_vel_frac=bv_shift/(tp or 1)

    print(f"\n  Background (left-edge rows):")
    print(f"    Temporal period : {tp or 'not found in 60 gens'}")
    print(f"    Drift per period: {bv_shift:+d} cells  (score={bv_score:.4f})")
    print(f"    Velocity        : {bg_vel_frac:+.4f} cells/gen")

    # ASCII spacetime — raw anomalies, full width
    ascii_full(history,bg_rows,bg_W=30,
               x_start=W//2-55,x_end=W//2+55,
               step_g=2,max_rows=110,
               label='SPACETIME █=anomaly vs left-edge background (step 2 gens, 110 rows)')

    # Co-moving frame if background is moving
    print(f"\n  CO-MOVING FRAME (background velocity subtracted):")
    if tp and abs(bv_shift)>0:
        cm_hist=comoving_history(history,bg_rows,30,bv_shift,tp)
        ascii_full(cm_hist,bg_rows,bg_W=30,
                   x_start=W//2-55,x_end=W//2+55,
                   step_g=2,max_rows=80,
                   label='Co-moving spacetime (background should be static here)')
    else:
        print("    Background stationary — no frame shift needed.")
        cm_hist=history

    # Isolated structure tracking
    print(f"\n  ISOLATED STRUCTURE TRACKING:")
    tracks=find_isolated(cm_hist,bg_rows,bg_W=30,
                         skip=60,gap=5,min_life=20,max_vel=6)
    if not tracks:
        print("    No isolated persistent structures found.")
    else:
        for trk in tracks:
            a=analyse_track(trk)
            flag='★ GLIDER' if a['glider'] else '  drift '
            vel,life,sz=a['vel'],a['life'],a['sz']
            g0,g1,cx0,cx1,rvar=a['g0'],a['g1'],a['cx0'],a['cx1'],a['rvar']
            print(f"    {flag}  vel={vel:+.3f}  life={life}gens  "
                  f"sz≈{sz}  g{g0}→{g1}  x:{cx0}→{cx1}  rvar={rvar}")
            if a['glider']:
                sample=trk[len(trk)//2]
                sg,sc=sample['gen'],sample['cells']
                print(f"           Pattern at g{sg}: cells {sc[:20]}")

    # Velocity scan on anomaly cells only
    print(f"\n  ANOMALY VELOCITY SCAN (only counts anomalous cells):")
    peaks,base=vel_scan(cm_hist,bg_rows,bg_W=30,
                        cx_range=70,skip=80,max_T=18,max_S=10)
    if not peaks:
        print("    No significant velocity peaks.")
    else:
        prev_vel=None
        for exc,T,S,sc,bl in peaks:
            vel=S/T
            note=' ← consistent!' if prev_vel and abs(vel-prev_vel)<0.05 else ''
            print(f"    T={T:2}  S={S:+3}  vel={vel:+.4f}  "
                  f"excess={exc:.4f}  (score={sc:.4f} vs base={bl:.4f}){note}")
            prev_vel=vel

    # Perturbation boundary velocities
    print(f"\n  PERTURBATION BOUNDARY VELOCITIES:")
    ext=perturb_extent(history,bg_rows,bg_W=30)
    cx=W//2
    # Sample at gens 100,200,300,400,500
    prev_l=prev_r=cx; prev_g=0
    for g in [50,100,150,200,300,400,500,600]:
        if g>=len(ext): break
        lx,rx=ext[g]
        if g>0 and g-prev_g>0:
            lv=(lx-prev_l)/(g-prev_g)
            rv=(rx-prev_r)/(g-prev_g)
        else: lv=rv=0
        print(f"    gen {g:4}: left_edge={lx:4}  right_edge={rx:4}  "
              f"vel_left={lv:+.3f}  vel_right={rv:+.3f}")
        prev_l=lx; prev_r=rx; prev_g=g

    print()

print("\n" + "═"*72)
print("KEY: ★ GLIDER = isolated cluster, consistent velocity, low residual variance")
print("     Consistent velocity across multiple (T,S) pairs = strongest signal")
print("     Boundary vel asymmetry = faster/slower structures escaping main wave")
