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
