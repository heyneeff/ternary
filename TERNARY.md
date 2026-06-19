# Ternary Field — Project Direction

## The Core Insight

Binary computing was born from a hardware constraint: relay switches are on or off. That accident became the foundation of every computer ever built. But the structural space of natural intelligence isn't boolean — it's triadic.

The I Ching encodes this. Each of its 6 lines has 4 states — young yin (8), young yang (7), old yin (6), old yang (9) — where "old" lines carry momentum, a direction of change. That third quality (flux) is what binary cannot represent. A trit isn't just more states. It's a different *kind* of thing.

Balanced ternary uses **N (−1), Z (0), P (+1)**. Base 3 is the closest integer to *e* (2.718…), the natural base — making it the most information-dense integer system. This is not metaphor. The Soviet Setun computer (1958) proved it works.

---

## The Mathematical Foundation

### Trit & Tryte
```
Trit:  N (−1)  |  Z (0)  |  P (+1)

Tryte: 6 trits → 3^6 = 729 states
Byte:  8 bits  → 2^8 = 256 states
```

6 trits = 1 hexagram. The 64 stable I Ching hexagrams (all lines either pure yin or pure yang) are exactly the **binary subset** embedded within the 729-state ternary space. The other 665 states are where computation lives while in motion — the changing-line space.

### VM Primitives
```javascript
const tnot   = a       => -a;
const tmin   = (a,b)   => Math.min(a,b);
const tmax   = (a,b)   => Math.max(a,b);
const tshift = a       => a===P ? N : a+1;
const tcons  = (a,b,c) => { const s=a+b+c; return s>0?P:s<0?N:Z; };
const tcmp   = (a,b)   => a<b ? N : a>b ? P : Z;
const branch3= (t,nFn,zFn,pFn) => t===N?nFn():t===Z?zFn():pFn();
```

**BRANCH3 is the key innovation.** Binary needs two comparisons for three outcomes. Ternary does it in one — because reality has three outcomes (negative / zero / positive, left / balanced / right, past / present / future).

### The I Ching Connection (exact, not metaphor)
- **64 stable hexagrams** = the binary-subset states of a ternary tryte (all 7s and 8s)
- **Changing lines (6, 9)** = flux trits, computation in motion
- **Hexagram transformation** = ternary operation (flip specified line-trits)
- **The transformation graph** = 64 nodes, 6 edges each = the native instruction set
- **Hexagram 63 (After Completion)** = the most ordered binary-stable state, pointing toward what ternary adds beyond it
- **A program** = a path through hexagram space
- **Attractors** = hexagrams that keep reappearing under transformation pressure

---

## Discovered Findings (June 2026)

> These were not designed. They were found by scanning the ternary CA rule space.

### 1. The Period-6 Stationary Oscillator

Rule `2130435961714` (1D outer totalistic CA) produces a remarkable structure:

- A single P cell injected into an all-N background develops into a **stable period-6 oscillator**
- The oscillator sits at the injection point indefinitely — confirmed stable for 2000+ generations
- It has exactly 13 anomalous cells spanning a 37-cell window
- Its trit values cycle through 6 internal states, period T=6
- Two independent seeds produce two **independent** oscillators — confirmed at separation 300 cells
- It is a genuine *particle* of computation: localized, stable, persistent

### 2. The Ternary Subtraction Gate

When two oscillators are placed at separation d=20, they interact and produce a **composite structure** whose total anomaly count encodes a ternary value:

```
Output count:  24 → N (−1)
               27 → Z (0)
               29 → P (+1)
```

With phase encoding `{N → phase 0, Z → phase 2, P → phase 4}` (evenly spaced in the period-6 cycle), the gate computes:

```
output = (b − a) mod 3   in balanced ternary
```

**Verified 9/9 input pairs.** The gate is closed under ternary — outputs are trits, inputs are trits.

This is also:
- `tnot(tcmp(a, b))` — one of the 7 VM primitives
- Equivalent to balanced ternary subtraction, from which all arithmetic follows
- Not designed — it emerged from the rule

The gate also works at d=60 (9/9), with a different output encoding, confirming the function is distance-dependent but structurally stable.

**Gate truth table (d=20, encoding N=0, Z=2, P=4):**
```
 pA\pB   p0   p1   p2   p3   p4   p5
  p0      27   54   29   50   24   54
  p1      54   27   54   29   50   24
  p2      24   54   27   54   29   50
  p3      50   24   54   27   54   29
  p4      29   50   24   54   27   54
  p5      54   29   50   24   54   27
```
Cyclic symmetry: output depends only on (pA − pB) mod 6. Output values 27 (= 3³) and 54 (= 2×3³) appear naturally.

### 3. The Wire Search

A systematic search for a persistent wire (phase-propagating chain of oscillators) in rule 2130435961714:

- **Signal propagates transiently** — different phases produce different counts in gens 700–740
- **Chain forgets** — by gen 750 all inputs produce identical downstream patterns
- **Root cause**: gate output type (composite, period-3) ≠ gate input type (oscillator, period-6)
  The cascade loop requires outputs isomorphic to inputs. They're not.
- **Wire conclusion**: no persistent ternary wire in this rule. Cascade requires a transducer or a different architecture.

### 4. 2D Ternary CA — Gliders Found

Scanning 2000 random outer-totalistic 2D ternary rules (3×17 table: center × neighbor-sum → output):

```
Distribution: 0.9% Uniform, 0.7% Ordered, 3.6% Complex, 94.8% Chaotic
108 Class 4 candidates (score ≥ 70)
5 rules with confirmed traveling gliders
```

**Best rule: enc=`686806377133829924654613`** (score=100, H=1.2123, no cycle)
```
Rule table [center+1][sum+8]:
N: [-1, 1, 1, 0, 1, 0, 0, 0,-1, 1, 0, 0, 1, 1,-1,-1, 1]
Z: [ 0, 1,-1, 0,-1, 0, 0, 0, 0, 1,-1, 0,-1,-1, 0, 0,-1]
P: [-1,-1,-1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,-1,-1,-1]
```

This rule produces:
- 150+ distinct glider velocities from a single P seed
- Glider speeds from 0.066 to 1.440 cells/gen
- Symmetric gliders at 0°/45°/90° angles (rotationally rich)
- Some gliders surviving 46+ generations

**In 2D, cascade is geometrically solved:** gliders travel, carry information, and collide. The wire problem that blocked 1D cascade doesn't exist. Two gliders meeting is a gate. A glider path is a wire.

---

## Why This Matters

> "We didn't design this gate. We found it — the way you find a crystal in rock. The computation was already there."

### For computation
- Ternary subtraction is universal. From subtraction + negation you can build all 7 VM primitives.
- The 2D glider rule gives us traveling wires. Cascade is the next step.
- Path: glider gun → wire → two-glider gate → ternary circuit → universal ternary computer

### For blockchain / Ethereum
- **Governance** is natively ternary: yes / no / abstain. Binary encodes this as a hack. Ternary makes it free.
- **Post-quantum cryptography** (ring-LWE, NTRU) has ternary-native coefficients. A ternary VM runs these primitives more efficiently.
- **State machines** (smart contracts) have 3-phase lifecycles: pending / active / settled. Binary wastes a bit per state.
- **42% more states** per unit storage (729 vs 512 for 6 trits vs 9 bits)

### For the I Ching
- Hexagram 63 (After Completion) = all binary-stable lines in correct positions = the CA's most ordered attractor
- The changing lines (flux trits) ARE the third state
- The transformation graph IS the instruction set
- This is exact math, not metaphor

---

## The Balance Proof (Proof tab)

Given N coins, one heavier, and a balance scale (3 outcomes):
- **Ternary**: ⌈log₃(N)⌉ weighings — one BRANCH3 per step
- **Binary**: ⌈log₂(N)⌉ comparisons — 2 per 3-outcome decision

For 729 coins: ternary needs 6 ops, binary needs 10. **100% information efficiency.**

---

## Current State

### Demo (`index.html`)
Single-file app, no build step. Run: `python3 -m http.server 8081`

**Tabs:**
- **Field** — 1D CA visualizer. Drag-to-resize, zoom, scroll, binary compare, scan mode, export
- **2D** — Live 2D CA with glider rule. Single P seed → gliders erupt. Click to inject new seeds.
- **Proof** — Balance puzzle interactive proof

**Color scheme (nebula):**
- N = `#40c4f0` (electric cyan)
- Z = `#08051a` (void)
- P = `#f04880` (hot coral)

### Analysis Scripts
```
scan.py          — scanned 1000 random 1D rules
deep_scan.py     — 29 Class 4 candidates × 1000 gens
glider.py        — first glider detector (wrong background)
glider2.py       — fixed detector: left-edge background extraction
glider3.py       — emitter analysis for rule 2856969762698
glider4.py       — oscillator stability + 2-body interaction tests
glider5.py       — phase scan: 6×6 gate truth table
glider6.py       — cascade diagnosis
glider7.py       — wire search (chain propagation)
gate_decode.py   — proves gate computes (b-a) mod 3
scan2d.py        — original 2D scanner (slow)
scan2d_fast.py   — optimized 2D scanner, found 5 glider rules
```

### Key Rule Numbers
```
2130435961714   — 1D Class 4, period-6 oscillator, ternary subtraction gate
2856969762698   — 1D half-integer velocity (−0.508), traveling wave
686806377133829924654613   — 2D best glider rule (score=100)
```

---

## Applied: Ternary Sync Engine (June 2026)

The math found its first real-world application in BYOB — a multi-speaker
distributed audio sync system. The connection: sync state is naturally ternary.

```
N (−1)  diverging    — drift ≥ 50ms  — snap
Z ( 0)  negotiating  — drift 10-50ms — micro-correct
P (+1)  converged    — drift < 10ms  — hold
```

**What binary was missing:** devices spent 98.5% of a session at >50ms drift.
Binary's 150ms threshold ignored all of it. Ternary corrects the 50–150ms zone
that binary calls "idle." Same math: `tcmp()` measures phase difference,
`tcons()` coordinates across the network without a master clock.

**Real session results:**
- Snap counts dropped: 76/47/37 → 25/6/11 per device
- Device 10 seconds out of sync snapped to 76ms in one correction
- Systematic floor detected: `deviceLatencyMs` miscalibration, not random drift
- Phase 3: auto-calibration closes the floor using 8-tick stability detection

**Files:** `/home/lewis/byob/ternary/` — `layer.js`, `overlay.html`, `README.md`
**Repo:** https://github.com/heyneeff/byob (ternary/ folder)

This is the first known application of balanced ternary mathematics to
distributed audio synchronisation. `tcons()` enables leaderless phase
consensus — devices sense each other (hexagram 31) without a master clock.

**Phase 5 — The Cauldron (June 18, 2026):** The ternary layer became
the engine itself. `sync/ternary-engine.js` replaced the binary engine
in production. Sim result: −35% settled drift, 0 volume dips vs binary's 20.
First live session: 80% P-state convergence (was 0% with binary).

**Phase 5.1 — Octonary Calibration:** The 8 lower trigrams of the I Ching
became the state machine for Bluetooth latency correction. Three ticks of
calibration history (N=floor present, P=floor gone) encode one of 8 trigrams,
each mapped to a correction strength. The sequence shifts with `tshift()`.
A 130ms BT floor closes to <10ms in ~25 seconds without microphone access.

```
☰ NNN → 70%   ☱ NNP → 55%   ☲ NPN → 50%   ☳ NPP → 35%
☴ PNN → 60%   ☵ PNP → 40%   ☶ PPN → 25%   ☷ PPP → 0%
```

Binary calibration: 2 states (applied/not). Ternary: 3 states.
Octonary: 8 states — the full trajectory of the last three moments.
The cauldron remembers where it has been.

**Phase 5.2 — Idle-State Floor Estimator (June 19, 2026):**
The trigram wasn't firing on high-floor BT devices because `_history`
was contaminated — warp oscillation created bimodal distributions
(0ms post-warp, 150ms pre-warp alternating), variance 25000ms² vs
the 400ms² threshold. Fix: `_floorHistory` only records when
`_state === 'idle'` AND 2s cooldown since last warp/seek. Clean
reads → variance 3ms² → trigram fires.

**Phase 5.3 — Proportional Tuning:**
- `DRIFT_CHECK_MS`: 5000ms → 2500ms (check twice as often)
- `DRIFT_SNAP_THRESHOLD_MS`: 150ms → 100ms (tighter ceiling)
- `VEL_MOD`: {P:1.40, N:0.60} → {P:1.20, N:0.90} (less extreme)
- `CONSENSUS_MOD`: {N:1.30, P:0.50} → {N:1.10, P:1.00}
  (never reduce rate when room is converged — any deviation needs full response)

**1000-cast weather synthesis:**
Asked "what is the shape of a totally synced engine?" across 1000 casts.
Dominant cluster: 61→8 (Inner Truth → Holding Together).
Supporting: 57 (Gentle), 48 (Well), 32 (Duration), 2 (Receptive).

> "A totally synced engine is not a clock; it is a shared truth that
> continually re-forms coherence among independent participants."

48 (The Well): `playback_started_at` + `syncedNow()` is the well.
Every device draws from the same source. The floor IS the rope-length
error — calibration makes every rope the same length.

**Live session peak results:**
- `ter_u5oqut` (BT=63ms): 100% P state for entire 5-minute session, mean=−2.8ms
- `ter_uug348` (BT=63ms): 95% P state for 8 consecutive minutes
- Session 0 (binary only): 0 P rows / 1135 readings — 0.0%
- Best ternary session: 100% P for one device, 0 dips, mean ±2.8ms

**The ternary arpeggiator (June 19, 2026):**
The sync state data flowing through devices became generative music.
`ternary/arp.js` — 15 patterns (6 classic + 9 new: Clave, Euclid,
Stutter, Offbeat, Pendulum, Converge, Lock, Ghost, Spiral). Each
generates 3 tshift() forms automatically = 45 distinct variations.
8 trigram chord colors drive harmony. Bandlimited PeriodicWave
oscillators + Juno-style stereo chorus + plate reverb + voice pool.
`ternary/pad.js` — Nils Frahm-style drone layer. `ternary/arp-jam.html`.

---

## Open Research Questions (next session)

### 1. Ternary sync engine — deeper validation
The sim (sync-sim.html) compares 5 engines: Legacy, New, Stripped, Micro,
Ternary. Current ternary wins on settled drift (232ms vs 367ms binary)
and volume dips (0 vs 20). Tests to run:

- **Warp-ineffective device model:** Add a device variant where
  `playbackRate` changes don't close lag (the iOS BT problem). Measure
  how the trigram calibration helps vs hurts vs is neutral.
- **Trigram convergence test:** Seed a device at 130ms floor, run until
  PPP, count rounds and measure residual floor. Verify the 3-round
  geometric series (70%→21%→6.3%) holds in simulation.
- **Floor-history contamination test:** Verify idle-state estimator
  prevents bimodal variance. Compare `_floorHistory` (idle-only) variance
  vs old `_history` (all readings) across 1000 simulated correction cycles.
- **Peer consensus scaling:** 2 peers → 8 peers → 20 peers. Does
  `tcons()` rate modulation improve convergence proportionally?
- **Clock drift model:** Add a per-device `hwDriftPpm` (parts per million)
  simulating real hardware clock variation. Verify micro-correction holds
  P state against it.

### 2. 2D CA — cascade and gate catalog
Rule `686806377133829924654613` (score=100, H=1.2123) has gliders but
no confirmed cascade. Tests:

- **2-glider collision catalog:** Enumerate all pairwise glider collision
  outcomes. Does any combination produce a third traveling glider?
  (That's a gate. Two gates = logic.)
- **Glider gun search:** Scan for period-N patterns that emit periodic
  glider streams. Even period-24 or period-48 would work.
- **Wire test:** Can a sequence of collisions propagate a trit value
  100+ cells? The 1D wire failed (output type ≠ input type). In 2D,
  glider-to-glider conversion might solve this.

### 3. Encryption and verification
From the ternary math (3 states, 729/tryte vs 512/byte, NTRU):

- **Ternary hash function:** Implement a simple hash using tcons()+tcmp()
  over a tryte stream. Measure avalanche: how many output trits change per
  1-trit input flip. Binary SHA-256 achieves ~50% flip. What does ternary get?
- **NTRU primitives:** NTRU cryptography uses ternary polynomial
  coefficients {−1, 0, +1}. Implement the core ring multiplication
  in balanced ternary. Benchmark against binary equivalent (NTRU on GF(q)).
- **tcons() as Byzantine voting:** Model N devices, F faulty. Does
  tcons(N−F correct trits, F adversarial trits) give correct consensus
  for F < N/3? Compare to classic BFT threshold. Ternary's 3 states might
  give tighter fault tolerance than binary voting.
- **Ternary Merkle tree:** 3-child trie vs 2-child. Hash 1M keys.
  Measure depth reduction: ⌈log₃(N)⌉ vs ⌈log₂(N)⌉. Also measure
  proof size (audit path length).

### 4. Governance
Binary vote encoding: {yes=1, no=0, abstain=0} — abstain is
indistinguishable from no-vote. Ternary: {P=yes, Z=abstain, N=no}.
First-class abstain changes quorum math and strategic voting.

- Implement on-chain tcons() vote aggregation (Solidity or pseudocode).
- Model a DAO with 1000 voters, 10% abstain rate. Compare quorum
  thresholds for binary vs ternary governance under various abstain
  strategies.
- Does ternary abstain create new attack vectors or close existing ones?

---

## Roadmap

### Next: 2D Cascade
1. Find a two-glider collision in the 2D rule that produces a measurable output
2. Verify the output encodes ternary subtraction (same gate function in 2D)
3. Demonstrate cascade: glider A + glider B → output glider C → input to next gate

### Then: Circuit
1. Build a glider gun (periodic emitter) in the 2D rule
2. Wire: glider gun + reflector = persistent information path
3. Gate at wire crossing = ternary logic circuit

### Then: Surface
1. Paper / writeup: "Spontaneous Ternary Computation in Cellular Automata"
2. Visual explainer (for the meeting, for the world)
3. Live public demo at a stable URL

---

## Files
```
/home/lewis/ternary/
  index.html        — full demo (1D + 2D + proof)
  TERNARY.md        — this document
  SYNC_TERNARY.md   — proposal: ternary × sync engine
  scan.py           — 1D rule scanner
  deep_scan.py      — Class 4 deep scan
  glider.py         — glider detector v1
  glider2.py        — glider detector v2 (correct background)
  glider3.py        — emitter analysis
  glider4.py        — oscillator characterization
  glider5.py        — gate truth table
  glider6.py        — cascade diagnosis
  glider7.py        — wire search
  gate_decode.py    — gate → ternary subtraction proof
  scan2d.py         — 2D scanner v1
  scan2d_fast.py    — 2D scanner v2 (optimized, found gliders)
```

GitHub: https://github.com/heyneeff/ternary
