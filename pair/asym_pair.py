#!/usr/bin/env python3
"""
================================================================================
ASYM_PAIR -- a pair where one side is reversible and the other scars
================================================================================

THE QUESTION

Earlier (two_systems.py) a pair of two SYMMETRIC systems had a conserved
residue: the part of the gap lying outside the span of available headings.
Exactly conserved, 8.9e-15.

Now make the pair ASYMMETRIC in exactly one way:

    A   is lossless.  Its update is orthogonal (a rotation). Fully
        reversible. Run it backwards and you land exactly where you started.
        No hysteresis. Nothing accumulates.

    B   has hysteresis. Its update is a rotation PLUS a small retained
        component of where it has been. Run it backwards and you do not
        return. It scars.

TESTED HERE

  1. Is A actually reversible and B actually not? (to machine precision)
  2. Does the conserved residue survive the asymmetry?
  3. Does an ARROW appear for the PAIR that is absent for A alone?
  4. Under time reversal of the joint state, what is not invariant?

This is the CPT question in the only form I can actually run: flip the
roles (C), flip inside/outside (P), flip the update direction (T), and see
which flip the structure survives.

Run:  python3 asym_pair.py
================================================================================
"""

import numpy as np

rng = np.random.default_rng(515)
D = 6


def rot(theta, i=0, j=1, d=D):
    M = np.eye(d)
    c, s = np.cos(theta), np.sin(theta)
    M[i, i] = c; M[i, j] = -s
    M[j, i] = s; M[j, j] = c
    return M


R = rot(0.37) @ rot(0.21, 2, 3) @ rot(0.11, 4, 5)


def step_A(x):
    """lossless: orthogonal, invertible, no accumulation."""
    return R @ x


def step_B(x, scar, eta=0.12):
    """hysteresis: same rotation, plus retained history."""
    y = R @ x + eta * scar
    scar = 0.9 * scar + 0.1 * x
    return y, scar


def main():
    np.set_printoptions(precision=6, suppress=True)

    print("=" * 78)
    print("1. IS A REVERSIBLE AND B NOT?")
    print("=" * 78)
    print()
    x0 = rng.normal(size=D)
    x = x0.copy()
    for _ in range(50):
        x = step_A(x)
    for _ in range(50):
        x = R.T @ x
    print(f"  A: forward 50, backward 50, return error = {np.abs(x-x0).max():.3e}")

    y0 = rng.normal(size=D)
    y, scar = y0.copy(), np.zeros(D)
    traj = []
    for _ in range(50):
        traj.append((y.copy(), scar.copy()))
        y, scar = step_B(y, scar)
    # exact inverse of B requires the scar history; a walker who only has
    # the rule and the current state cannot undo it:
    yb = y.copy()
    for _ in range(50):
        yb = R.T @ yb
    print(f"  B: forward 50, backward 50, return error = {np.abs(yb-y0).max():.3e}")
    print()
    print("  B does not return. the scar is not in the state, so the state")
    print("  is not enough to run it backwards. that is what irreversible")
    print("  MEANS here: information left the state without leaving the")
    print("  system.")
    print()

    print("=" * 78)
    print("2. DOES THE RESIDUE STILL CONSERVE?")
    print("=" * 78)
    print()
    print("  residue = component of the gap (a - b) outside the span of the")
    print("  headings each system can actually move along.")
    print()

    def residue(a, b, H):
        g = a - b
        Q, _ = np.linalg.qr(H)
        return np.linalg.norm(g - Q @ (Q.T @ g))

    # symmetric control: both lossless
    a, b = rng.normal(size=D), rng.normal(size=D)
    H = np.stack([R @ a - a, R @ b - b], axis=1)
    r0 = residue(a, b, H)
    aa, bb = a.copy(), b.copy()
    for _ in range(40):
        aa, bb = step_A(aa), step_A(bb)
    H2 = np.stack([R @ aa - aa, R @ bb - bb], axis=1)
    r1 = residue(aa, bb, H2)
    print(f"  SYMMETRIC  (both lossless)   residue {r0:.9f} -> {r1:.9f}   "
          f"change {abs(r1-r0):.2e}")

    # asymmetric: A lossless, B scars
    a, b = rng.normal(size=D), rng.normal(size=D)
    sc = np.zeros(D)
    H = np.stack([R @ a - a, R @ b - b], axis=1)
    r0 = residue(a, b, H)
    aa, bb = a.copy(), b.copy()
    for _ in range(40):
        aa = step_A(aa)
        bb, sc = step_B(bb, sc)
    H2 = np.stack([R @ aa - aa, R @ bb - bb], axis=1)
    r1 = residue(aa, bb, H2)
    print(f"  ASYMMETRIC (B scars)         residue {r0:.9f} -> {r1:.9f}   "
          f"change {abs(r1-r0):.2e}")
    print()

    print("=" * 78)
    print("3. IS THERE AN ARROW FOR THE PAIR THAT A ALONE DOES NOT HAVE?")
    print("=" * 78)
    print()
    print("  test: give a referee the joint sequence with the time labels")
    print("  stripped, and ask which end is 'later'. a quantity that rises")
    print("  monotonically is an arrow. one that does not is no arrow.")
    print()

    # A alone
    x = rng.normal(size=D)
    nA = [np.linalg.norm(x)]
    for _ in range(40):
        x = step_A(x); nA.append(np.linalg.norm(x))
    dA = np.diff(nA)
    print(f"  A alone   |x| over 40 steps:  min {min(nA):.6f}  max {max(nA):.6f}")
    print(f"            monotone? {np.all(dA > 0) or np.all(dA < 0)}   "
          f"(spread {max(nA)-min(nA):.2e})")

    # the pair
    a, b = rng.normal(size=D), rng.normal(size=D)
    sc = np.zeros(D)
    gaps = [np.linalg.norm(a - b)]
    scars = [np.linalg.norm(sc)]
    for _ in range(40):
        a = step_A(a)
        b, sc = step_B(b, sc)
        gaps.append(np.linalg.norm(a - b))
        scars.append(np.linalg.norm(sc))
    dg = np.diff(gaps)
    ds = np.diff(scars)
    print(f"  pair      |a-b|:             min {min(gaps):.6f}  max {max(gaps):.6f}")
    print(f"            monotone? {bool(np.all(dg > 0) or np.all(dg < 0))}")
    print(f"  pair      |scar|:            min {min(scars):.6f}  max {max(scars):.6f}")
    print(f"            monotone rising? {bool(np.all(ds > -1e-12))}")
    print()
    print(f"  {'step':>6} {'|a|':>12} {'|a-b|':>12} {'|scar|':>12}")
    print("  " + "-" * 46)
    for i in (0, 5, 10, 20, 30, 40):
        print(f"  {i:>6} {nA[i]:12.8f} {gaps[i]:12.8f} {scars[i]:12.8f}")
    print()

    print("=" * 78)
    print("4. WHICH FLIP DOES THE PAIR SURVIVE?")
    print("=" * 78)
    print()
    a0, b0 = rng.normal(size=D), rng.normal(size=D)

    def run(a, b, n=30, swap=False, back=False):
        sc = np.zeros(D)
        M = R.T if back else R
        for _ in range(n):
            if swap:
                a, sc = (M @ a + 0.12 * sc), 0.9 * sc + 0.1 * a
                b = M @ b
            else:
                a = M @ a
                b, sc = (M @ b + 0.12 * sc), 0.9 * sc + 0.1 * b
        return np.linalg.norm(a - b)

    base = run(a0, b0)
    c_flip = run(a0, b0, swap=True)            # C: exchange the roles
    p_flip = run(b0, a0)                       # P: exchange the labels
    t_flip = run(a0, b0, back=True)            # T: run the update backwards
    cpt = run(b0, a0, swap=True, back=True)    # all three

    print(f"  {'flip':>22} {'|a-b| after 30':>18} {'= baseline?':>14}")
    print("  " + "-" * 56)
    for nm, v in [("none (baseline)", base), ("C  swap who scars", c_flip),
                  ("P  swap the labels", p_flip), ("T  run backwards", t_flip),
                  ("CPT  all three", cpt)]:
        same = "yes" if abs(v - base) < 1e-9 else f"no ({abs(v-base):.3e})"
        print(f"  {nm:>22} {v:18.9f} {same:>14}")
    print()
    print("  read the table, not me: whichever rows say 'no' are the")
    print("  symmetries this pair does not have.")


if __name__ == "__main__":
    main()
