"""
Two systems. The error lives in the between.

ONE SYSTEM (established last run)
  error e, motion v. what drives is e.v. what stops it is not
  shrinking |e| but having the orthogonal component RECEIVED without
  it steering the heading. With the heading held and e fully
  orthogonal, displacement along v is exactly 0 while |e| stays 1.

  In 1-D there is no orthogonal, so a 1-D system can only shrink and
  never arrives. x -> 1 + 1/x is that case.

TWO SYSTEMS
  Now there are two states, xA and xB, and two headings, vA and vB.
  The error is not a property of either. It is the gap:

      g = xB - xA

  and the thing that matters is how g sits relative to EACH heading.

  Each system can only act on its own heading. So the gap decomposes
  four ways:

      g . vA     what A can do something about
      g . vB     what B can do something about
      g_perp_A   what is orthogonal to A -- A cannot reach it
      g_perp_B   same for B

  THE BETWEEN, precisely: the component of g orthogonal to BOTH
  headings. Neither system can act on it, neither can receive it,
  and it belongs to the pair.

      g_between = g - proj onto span(vA, vB)

  This is nonzero whenever d > 2, and it is exactly the direction
  the commutator lives in from the earlier SL(2,R) run.

TESTS
 1. does the between component persist when both systems act
    optimally on what they can reach?
 2. what happens when the headings are parallel (both facing the
    same way) vs crossed?
 3. can one system alone close the gap? can two? under what
    condition?
 4. what if only ONE system is acting (the other is static)?
    -- the asymmetric case
"""

import numpy as np

rng = np.random.default_rng(67)


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-15 else v


def decompose(g, vA, vB):
    """Split g into the span(vA,vB) plane and the remainder."""
    M = np.column_stack([vA, vB])
    # least squares projection onto the plane
    coef, *_ = np.linalg.lstsq(M, g, rcond=None)
    g_plane = M @ coef
    g_between = g - g_plane
    return g_plane, g_between


def run(d=8, T=3000, alpha=0.06, both_act=True,
        heading_held=True, angle=None, seed=0):
    """
    Two systems, each moving along its own heading, each acting on
    the part of the gap it can reach.

    heading_held: if True, each system's heading is fixed (the
                  'absorbed' regime that actually stops). if False,
                  headings follow motion (the 'rotated' regime).
    angle:        if given, the angle between vA and vB is set to it.
    """
    r = np.random.default_rng(seed)
    xA = r.normal(0, 1, d)
    xB = r.normal(0, 1, d) + 3.0

    vA = unit(r.normal(0, 1, d))
    if angle is None:
        vB = unit(r.normal(0, 1, d))
    else:
        w = r.normal(0, 1, d)
        w = unit(w - (w @ vA) * vA)
        vB = np.cos(angle) * vA + np.sin(angle) * w

    hist = []
    for t in range(T):
        g = xB - xA
        gp, gb = decompose(g, vA, vB)

        # each system moves along its own heading, by the amount of
        # the gap it can see along that heading
        stepA = alpha * (g @ vA) * vA
        stepB = -alpha * (g @ vB) * vB if both_act else np.zeros(d)

        xA = xA + stepA
        xB = xB + stepB

        if not heading_held:
            if np.linalg.norm(stepA) > 1e-12:
                vA = unit(stepA)
            if both_act and np.linalg.norm(stepB) > 1e-12:
                vB = unit(stepB)

        hist.append((np.linalg.norm(g), np.linalg.norm(gp),
                     np.linalg.norm(gb)))

    hist = np.array(hist)
    return {
        "gap0": hist[0, 0], "gapT": hist[-1, 0],
        "plane0": hist[0, 1], "planeT": hist[-1, 1],
        "between0": hist[0, 2], "betweenT": hist[-1, 2],
        "hist": hist,
    }


print("=" * 78)
print("1. CAN THE GAP BE CLOSED? both acting, headings held")
print("=" * 78)
print()
print(f"  {'dim':>5} {'gap start':>11} {'gap end':>10} "
      f"{'in-plane end':>14} {'BETWEEN end':>13} {'closed?':>9}")
print("  " + "-" * 68)
for d in (2, 3, 4, 6, 8, 16):
    res = [run(d=d, seed=s) for s in range(5)]
    g0 = np.mean([r["gap0"] for r in res])
    gT = np.mean([r["gapT"] for r in res])
    pT = np.mean([r["planeT"] for r in res])
    bT = np.mean([r["betweenT"] for r in res])
    print(f"  {d:5d} {g0:11.5f} {gT:10.5f} {pT:14.6f} {bT:13.6f} "
          f"{'yes' if gT < 1e-4 else 'no':>9}")
print()
print("  in d = 2 the two headings span everything, so there is no")
print("  between and the gap closes. for d > 2 a component survives")
print("  that neither system can reach, and the gap does NOT close.")
print()

print("=" * 78)
print("2. THE ANGLE BETWEEN THE TWO HEADINGS")
print("=" * 78)
print()
print("  vB set at a fixed angle from vA. d = 8.")
print()
print(f"  {'angle':>9} {'cos':>8} {'gap end':>10} {'in-plane':>11} "
      f"{'BETWEEN':>11} {'reachable frac':>15}")
print("  " + "-" * 68)
for a in (0.0, np.pi/12, np.pi/6, np.pi/4, np.pi/3, np.pi/2,
          2*np.pi/3, np.pi):
    res = [run(d=8, angle=a, seed=s) for s in range(5)]
    gT = np.mean([r["gapT"] for r in res])
    pT = np.mean([r["planeT"] for r in res])
    bT = np.mean([r["betweenT"] for r in res])
    g0 = np.mean([r["gap0"] for r in res])
    print(f"  {np.degrees(a):8.1f}° {np.cos(a):8.4f} {gT:10.5f} "
          f"{pT:11.6f} {bT:11.6f} {1 - bT/g0:15.4f}")
print()
print("  parallel headings (0°) are the WORST case: both systems can")
print("  only reach the same single direction, so the pair covers a")
print("  line instead of a plane, and more of the gap is unreachable.")
print()

print("=" * 78)
print("3. ONE ACTING vs BOTH ACTING")
print("=" * 78)
print()
print(f"  {'condition':>22} {'gap start':>11} {'gap end':>10} "
      f"{'reduction':>11} {'BETWEEN end':>13}")
print("  " + "-" * 70)
for label, kw in (("both acting", dict(both_act=True)),
                  ("only A acting", dict(both_act=False))):
    res = [run(d=8, seed=s, **kw) for s in range(5)]
    g0 = np.mean([r["gap0"] for r in res])
    gT = np.mean([r["gapT"] for r in res])
    bT = np.mean([r["betweenT"] for r in res])
    print(f"  {label:>22} {g0:11.5f} {gT:10.5f} "
          f"{1 - gT/g0:11.4f} {bT:13.6f}")
print()
print("  one system acting alone reaches only its own heading: a")
print("  single line out of d dimensions. two systems reach a plane.")
print("  the fraction each can close is a dimension count, not an")
print("  effort count.")
print()

print("=" * 78)
print("4. HEADINGS HELD vs HEADINGS FOLLOWING MOTION")
print("=" * 78)
print()
print(f"  {'mode':>28} {'gap end':>10} {'BETWEEN end':>13} "
      f"{'behaviour':>14}")
print("  " + "-" * 68)
for label, kw in (("held (absorbed)", dict(heading_held=True)),
                  ("following (rotated)", dict(heading_held=False))):
    res = [run(d=8, seed=s, **kw) for s in range(5)]
    gT = np.mean([r["gapT"] for r in res])
    bT = np.mean([r["betweenT"] for r in res])
    beh = "settles" if gT < 1e-3 else "residual holds"
    print(f"  {label:>28} {gT:10.5f} {bT:13.6f} {beh:>14}")
print()

print("=" * 78)
print("5. WHAT THE BETWEEN COMPONENT DOES OVER TIME")
print("=" * 78)
print()
r = run(d=8, seed=3)
h = r["hist"]
print(f"  {'step':>7} {'|gap|':>11} {'in-plane':>11} {'BETWEEN':>11}")
print("  " + "-" * 44)
for i in (0, 10, 50, 200, 800, 1500, 2999):
    print(f"  {i:7d} {h[i,0]:11.6f} {h[i,1]:11.6f} {h[i,2]:11.6f}")
print()
print("  the in-plane part is consumed. the between part does not")
print("  move at all -- it is exactly conserved, because nothing in")
print("  the dynamics can touch it.")
print()
print(f"  between at start: {h[0,2]:.9f}")
print(f"  between at end:   {h[-1,2]:.9f}")
print(f"  change:           {abs(h[-1,2]-h[0,2]):.3e}")
print()
print("  CONCLUSION")
print()
print("  with two systems the error is not in either one. it is the")
print("  gap. each system can act only on the projection of the gap")
print("  onto its own heading, so between them they reach a plane.")
print()
print("  everything outside that plane is conserved exactly. it is")
print("  not resistant, not slow -- it is untouched, because no")
print("  available action has a component along it.")
print()
print("  that residue is the between. it does not shrink with effort")
print("  and it does not decay with time. the only thing that changes")
print("  it is a change of HEADING -- which is exactly the move that")
print("  turns absorption back into rotation.")
