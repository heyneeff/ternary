"""
Decode what ternary operation the phase gate computes.

Gate facts (from glider5.py, distance=20):
  Output = f(Δ) where Δ = (pA - pB) mod 6
  f(0)=27, f(1)=54, f(2)=24, f(3)=50, f(4)=29, f(5)=54

Question: does there exist a phase assignment φ: {N,Z,P} → {0..5}
such that  f(φ(a) - φ(b) mod 6) = φ(op(a,b))  for all a,b ∈ {N,Z,P}
and some ternary operation op?

If yes: the CA physically computes that operation.
"""

from itertools import permutations, combinations

N, Z, P = -1, 0, 1
TRITS = [N, Z, P]
TNAME = {N: 'N', Z: 'Z', P: 'P'}

# Gate lookup table: f(Δ) for Δ = 0..5
F = {0: 27, 1: 54, 2: 24, 3: 50, 4: 29, 5: 54}

# All ternary operations (the 7 VM primitives + some extra)
def tnot(a):      return -a
def tmin(a, b):   return min(a, b)
def tmax(a, b):   return max(a, b)
def tcons(a, b):  s = a+b; return P if s>0 else (N if s<0 else Z)
def tcmp(a, b):   return N if a<b else (P if a>b else Z)
def tshift(a):    return N if a==P else a+1
def tadd(a, b):   # saturating addition in {N,Z,P}
    s = a+b; return max(N, min(P, s))
def txor3(a, b):  return (a+b) % 3 - 1  # cyclic XOR in Z3 — maps to {N,Z,P}

BINARY_OPS = {
    'tmin':   tmin,
    'tmax':   tmax,
    'tcons':  tcons,
    'tcmp':   tcmp,
    'tadd':   tadd,
    'txor3':  txor3,
    'a':      lambda a,b: a,   # identity projection
    'b':      lambda a,b: b,
    'neg_b':  lambda a,b: -b,
    'neg_a':  lambda a,b: -a,
}

print("="*70)
print("GATE DECODE — searching for phase encodings that implement known ops")
print("="*70)
print(f"\nGate: f(Δ) = {F}")
print(f"Outputs used: {sorted(set(F.values()))}")
print()

# We need to choose 3 phases from {0..5} and assign them to {N,Z,P}
# Total: C(6,3) * 3! = 20 * 6 = 120 assignments
# Plus: can the output value map BACK to a phase? We need φ(op(a,b)) ∈ output values

hits = []

for phases in combinations(range(6), 3):
    for perm in permutations(phases):
        phi = {N: perm[0], Z: perm[1], P: perm[2]}  # φ(trit) → phase
        phi_inv = {v: k for k, v in phi.items()}      # phase → trit (partial)

        # For each binary op, check if the gate implements it
        for op_name, op in BINARY_OPS.items():
            valid = True
            for a in TRITS:
                for b in TRITS:
                    delta = (phi[a] - phi[b]) % 6
                    gate_output = F[delta]
                    expected_trit = op(a, b)
                    expected_output = phi.get(expected_trit)
                    if expected_output is None or gate_output != expected_output:
                        valid = False
                        break
                if not valid:
                    break

            if valid:
                hits.append((op_name, phi, phases))
                print(f"★ MATCH: operation={op_name}")
                print(f"  Phase assignment: N→{phi[N]}  Z→{phi[Z]}  P→{phi[P]}")
                print(f"  Verification table:")
                print(f"  {'a':>3} {'b':>3} | {'φ(a)':>5} {'φ(b)':>5} {'Δ':>4} | "
                      f"{'f(Δ)':>6} {'φ(op)':>6} | {'op(a,b)':>8} {'match':>6}")
                print(f"  {'─'*65}")
                for a in TRITS:
                    for b in TRITS:
                        delta = (phi[a] - phi[b]) % 6
                        gate_out = F[delta]
                        expected = op(a, b)
                        exp_phase = phi.get(expected, '?')
                        match = '✓' if gate_out == exp_phase else '✗'
                        print(f"  {TNAME[a]:>3} {TNAME[b]:>3} | {phi[a]:>5} {phi[b]:>5} {delta:>4} | "
                              f"{gate_out:>6} {exp_phase:>6} | {TNAME[expected]:>8} {match:>6}")
                print()

if not hits:
    print("No exact matches found. Checking approximate / partial matches...")
    print()

    # Check partial: for each (op, phi), what fraction of cells match?
    best_matches = []
    for phases in combinations(range(6), 3):
        for perm in permutations(phases):
            phi = {N: perm[0], Z: perm[1], P: perm[2]}

            for op_name, op in BINARY_OPS.items():
                correct = 0
                total = 9
                for a in TRITS:
                    for b in TRITS:
                        delta = (phi[a] - phi[b]) % 6
                        gate_output = F[delta]
                        expected_trit = op(a, b)
                        expected_output = phi.get(expected_trit)
                        if expected_output is not None and gate_output == expected_output:
                            correct += 1
                frac = correct / total
                best_matches.append((frac, op_name, phi))

    best_matches.sort(key=lambda x: x[0], reverse=True)
    print(f"Top 10 partial matches:")
    print(f"  {'frac':>6}  {'op':>8}  assignment")
    seen = set()
    shown = 0
    for frac, op_name, phi in best_matches:
        key = (frac, op_name, tuple(sorted(phi.items())))
        if key not in seen and shown < 15:
            seen.add(key)
            print(f"  {frac:>6.3f}  {op_name:>8}  N→{phi[N]} Z→{phi[Z]} P→{phi[P]}")
            shown += 1

# ── ALTERNATIVE: what if output codes don't map to phases but to distances? ──
print()
print("="*70)
print("ALTERNATE ENCODING: output value as ordinal rank")
print("="*70)
print("Map outputs by rank: 24<27<29<50<54 → rank 0,1,2,3,4")
print("Then check if rank(f(φ(a)-φ(b))) encodes a ternary ordinal operation")
print()

RANK = {24: 0, 27: 1, 29: 2, 50: 3, 54: 4}
F_rank = {d: RANK[v] for d, v in F.items()}
print(f"f_rank(Δ): {F_rank}")
print()

# With 5 output ranks but only 3 trits (ranks 0,1,2), maybe the operation
# is on {0,1,2} and the output is rank mod 3 or something
print("Checking: does f_rank(Δ) mod 3 give a meaningful operation?")
F_mod3 = {d: v%3 for d,v in F_rank.items()}
print(f"f mod 3: {F_mod3}")

for phases in combinations(range(6), 3):
    for perm in permutations(phases):
        phi = {N: perm[0], Z: perm[1], P: perm[2]}

        for op_name, op in BINARY_OPS.items():
            valid = True
            for a in TRITS:
                for b in TRITS:
                    delta = (phi[a] - phi[b]) % 6
                    gate_rank_mod3 = F_rank[delta] % 3
                    expected_trit = op(a, b)
                    expected_rank = [0,1,2][[N,Z,P].index(expected_trit)]
                    if gate_rank_mod3 != expected_rank:
                        valid = False; break
                if not valid: break
            if valid:
                print(f"  ★ RANK-MOD3 MATCH: op={op_name}  N→{phi[N]} Z→{phi[Z]} P→{phi[P]}")

# ── SHOW THE 3x3 TABLE for key assignments ─────────────────────────────────
print()
print("="*70)
print("3×3 GATE TABLE for candidate encodings")
print("="*70)

candidates = [
    ("evenly spaced {0,2,4}", {N:0, Z:2, P:4}),
    ("evenly spaced {1,3,5}", {N:1, Z:3, P:5}),
    ("compressed {0,1,2}",    {N:0, Z:1, P:2}),
    ("compressed {0,2,1}",    {N:0, Z:2, P:1}),
    ("half-period {0,3,1}",   {N:0, Z:3, P:1}),
]

for label, phi in candidates:
    print(f"\n  {label}  (N→{phi[N]}, Z→{phi[Z]}, P→{phi[P]})")
    print(f"  {'':6}  {'N':>6}  {'Z':>6}  {'P':>6}")
    print(f"  {'─'*27}")
    for a in TRITS:
        row = []
        for b in TRITS:
            delta = (phi[a] - phi[b]) % 6
            row.append(F[delta])
        print(f"  {TNAME[a]:>6}   {'  '.join(f'{v:4}' for v in row)}")

    # Also show rank version
    print(f"  Rank version:")
    print(f"  {'':6}  {'N':>6}  {'Z':>6}  {'P':>6}")
    print(f"  {'─'*27}")
    for a in TRITS:
        row = []
        for b in TRITS:
            delta = (phi[a] - phi[b]) % 6
            row.append(RANK[F[delta]])
        trit_row = ['NZP'[r] if r<3 else str(r) for r in row]
        print(f"  {TNAME[a]:>6}   {'  '.join(f'{v:>4}' for v in trit_row)}")

print()
print("="*70)
print("INTERPRETATION")
print("="*70)
print("""
  An EXACT match means: the CA physically computes that ternary operation.
  A RANK-MOD3 match means: the CA computes it if outputs are ordinal-decoded.
  The 3×3 rank tables show what logic function each encoding computes.

  N=−1, Z=0, P=+1 in balanced ternary.
  A circulant 3×3 table (each row is a rotation of the previous) = cyclic op.
  A symmetric table (table[a][b] == table[b][a]) = commutative op.
""")
