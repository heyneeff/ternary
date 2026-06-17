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
const tnot   = a       => -a;                              // negate
const tmin   = (a,b)   => Math.min(a,b);                  // AND
const tmax   = (a,b)   => Math.max(a,b);                  // OR
const tshift = a       => a===P ? N : a+1;                // N→Z→P→N (cycle)
const tcons  = (a,b,c) => { s=a+b+c; return s>0?P:s<0?N:Z; }; // majority
const tcmp   = (a,b)   => a<b ? N : a>b ? P : Z;         // compare → trit
const branch3= (t,nFn,zFn,pFn) => t===N?nFn():t===Z?zFn():pFn();
```

**BRANCH3 is the key innovation.** Binary needs two comparisons for three outcomes. Ternary does it in one operation — because reality has three outcomes (negative / zero / positive, left / balanced / right, past / present / future).

### The I Ching Connection (exact, not metaphor)
- **64 stable hexagrams** = the binary-subset states of a ternary tryte (all 7s and 8s)
- **Changing lines (6, 9)** = flux trits, computation in motion
- **Hexagram transformation** = ternary operation (flip specified line-trits)
- **The transformation graph** = 64 nodes, 6 edges each (one per line-flip) = the native instruction set
- **A program** = a path through hexagram space
- **Attractors** = hexagrams that keep reappearing under transformation pressure — computable, emergent, meaningful

The King Wen sequence (1–64 numbering) is one human-imposed ordering on this graph. The mathematical relationships between hexagrams (21.1.4.6 = 2, etc.) are structural identities that exist independently of any sequence.

---

## The Demo: Ternary Field (`index.html`)

A 1D ternary cellular automaton running in real time. Each cell has 3 states (N/Z/P). Each generation applies a rule to every cell based on its left neighbor, itself, and right neighbor — 27 possible input combinations, each mapping to an output trit.

**Rule space: 3^27 = 7,625,597,484,987 possible rules** (vs 256 for binary CA).

### Preset Rules
| Name | Formula | Character |
|------|---------|-----------|
| **Sum** | `(l+c+r) mod 3` | Sierpinski-like self-similarity |
| **Outer** | `(l+r) mod 3` | Rule-90 ternary analog, triangle patterns |
| **Consensus** | majority of (l,c,r) | Domain walls, crystallization |
| **Modular** | `(l×c + r) mod 3` | Nonlinear, unpredictable complexity |

### Controls
- **Rule input**: enter any decimal number 0 → 7,625,597,484,987 to select a rule
- **Random**: instant random rule
- **Hunt**: auto-searches rules, stops when it finds one that produces complex patterns
- **Rule table**: 27 clickable cells — each click cycles that cell's output trit (N→Z→P→N), letting you mutate the rule live
- **Drag handle**: grab the bar between canvas and controls to resize the panel
- **init: center / random**: single P cell in a sea of N, or random noise start

### The Balance Proof (Proof tab)
The canonical demonstration that ternary is superior for a specific class of problems:

Given N coins, one heavier, and a balance scale (3 outcomes: left heavy / balanced / right heavy):
- **Ternary**: ⌈log₃(N)⌉ weighings — each is a single BRANCH3 operation
- **Binary**: ⌈log₂(N)⌉ comparisons — needs 2 per 3-outcome decision

For 729 coins: ternary needs 6 ops, binary needs 10. The ternary approach matches the structure of the problem exactly — **100% information efficiency**.

---

## Direction: What This Becomes

### Phase 1 (current): Proof of concept
- ✅ Ternary VM (7 primitives)
- ✅ 1D ternary CA with 7.6T rule space
- ✅ Visual explorer (Field tab)
- ✅ Balance puzzle proof (Proof tab)

### Phase 2: Richer computation
- **Attractor detection**: run the CA and identify which states it returns to most — these are the stable configurations of the rule's "physics"
- **2D ternary CA**: the field becomes a grid, enabling richer spatial patterns
- **Hexagram space navigator**: agent that learns optimal paths between any two of the 64 stable states

### Phase 3: The computation model
- **Ternary type system**: values carry flux-direction as part of their type (not just undetermined, but ascending or descending)
- **Ternary VM interpreter**: write small programs as sequences of ternary operations
- **Comparison benchmark**: same algorithm in binary vs ternary, count operations, measure convergence speed

### Phase 4: Generative systems
- **Ternary neural network**: weights are trits, activation has 3 states — train on simple tasks and compare against binary NN
- **Ternary grammar**: generative language where sentence structure uses 3-way branching throughout

---

## The Deeper Vision

The flux machine (`reader.html`, separate project) already demonstrates that this ternary structure maps onto real-world field dynamics — streams of hexagram casts show statistical deviation from noise when intention is present. That's the territory.

Ternary Field is the map — a computable system that encodes the same underlying structure. The goal is a computation model that is *more true* to how the universe actually processes information: not discrete bits toggling between states, but trits that carry momentum, direction, and the potential to be in flux.

Binary computes correctly. Ternary computes *naturally*.

---

## Files
```
/home/lewis/ternary/
  index.html    — the demo (single file, no build step)
  TERNARY.md    — this document
```

**Run locally:** `python3 -m http.server 8081` from `/home/lewis/ternary/`
