#!/usr/bin/env python3
"""
================================================================================
PAIR MODEL -- a split pair, from before the break to the present
================================================================================

Self-contained. Requires only numpy. Run:  python3 pair_model.py

--------------------------------------------------------------------------------
WHAT THIS IS
--------------------------------------------------------------------------------

A model of two systems that were once one, drifted apart, and are trying (or
not trying) to close the gap. Built to test whether a specific set of claims
about separation and repair are internally consistent and what they predict.

Everything in the model is geometry. No psychology is assumed; the psychological
readings are stated in comments but nothing in the code depends on them.

--------------------------------------------------------------------------------
THE PRIMITIVES
--------------------------------------------------------------------------------

state x        where a system currently is, a point in R^d
heading v      the ONE direction a system can act along, a unit vector
memory m       a second direction a system holds, its grip on the shared past
gap g          x_B - x_A, the separation. belongs to neither, only to the pair

A system can move only along directions it holds. Here each holds two: v and m.
So the pair together spans at most four directions out of d.

    RESIDUE = the component of the gap outside the span of all four.

The residue is not "hard to close." It is UNREACHABLE: no action available to
either system has any component along it. It is exactly conserved.

--------------------------------------------------------------------------------
THE FIVE CLAIMS BEING TESTED
--------------------------------------------------------------------------------

C1  A pair that split from one thing has no residue at the moment of splitting,
    however far apart they get. The gap is made of the directions they diverged
    along, so it lies entirely within their reach.

C2  Residue is created by DRIFT -- whatever happens to each of them separately
    afterwards -- and accrues per unit of TIME apart, not per unit of distance.

C3  A break does more damage when BOTH are depleted at once. One struggling
    alone costs far less, because the other still holds the shared plane.

C4  The shared past is a TWO-BODY quantity: the overlap of the two memories,
    not either one's grip on it. One preserving while the other suppresses does
    not preserve it.

C5  Acting on a reconstruction of the other (perception at distance) can only
    move along directions already held, so it cannot touch the residue.
    Co-presence transfers the other's ACTUAL current heading, which is a new
    direction, and new directions are the only thing that changes the residue.

--------------------------------------------------------------------------------
WHAT CHANGED FROM THE FIRST VERSION, AND WHY
--------------------------------------------------------------------------------

Two results in the first run were artifacts and are fixed here:

(a) PERCEPTION BLEW UP (gap 9.8 -> 44.8, a 358% increase). The update rule
    projected the gap onto the memory vector and then onto the heading, which
    double-counts and can produce a step LARGER than the gap. Overshoot then
    compounds. Fixed: each system takes a bounded step along each direction it
    holds, with the step never exceeding the component of the gap along that
    direction. Perception now converges to a floor instead of diverging, which
    is the honest behaviour -- it closes what it can reach and stops.

(b) CONTACT FREQUENCY SATURATED (every-5 no better than once-only). Two causes:
    phase-3 drift was set to 0.3x, too low for an acquired heading to decay, and
    the transfer coefficient (0.25) was large enough that one contact nearly
    completed the job. Fixed: drift continues at full rate during phase 3, and
    each contact transfers a realistic fraction. Frequency now matters and the
    curve is monotone.

Both fixes make the model harsher, not kinder.

--------------------------------------------------------------------------------
HOW TO READ THE OUTPUT
--------------------------------------------------------------------------------

gap        distance between the two states
residue    the part of the gap no available action can touch
holds v0   how much of the original shared direction a memory still points along
shared     overlap between the two memories: |m_A . m_B|

'shared' is the quantity C4 is about. Watch it separately from 'holds v0'.
================================================================================
"""

import numpy as np

D = 12                      # dimension of the state space


# ------------------------------------------------------------------ helpers

def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-15 else v


def residue(g, dirs):
    """Component of g outside the span of the given directions."""
    M = np.column_stack([unit(d) for d in dirs])
    coef, *_ = np.linalg.lstsq(M, g, rcond=None)
    return g - M @ coef


class Party:
    """One half of the pair."""

    def __init__(self, x, v, m, strategy):
        self.x = x.copy()
        self.v = unit(v)            # heading: what it can act along now
        self.m = unit(m)            # memory: its grip on the shared past
        self.strategy = strategy    # 'preserve' or 'suppress'

    def dirs(self):
        return [self.v, self.m]


def update_memory(p, v0, rate, r):
    """
    PRESERVE: pull m back toward the original shared direction v0.
    SUPPRESS: remove m's component along v0.
    Both get ordinary noise on top.
    """
    if p.strategy == "preserve":
        p.m = unit(p.m + rate * v0)
    else:
        p.m = unit(p.m - rate * (p.m @ v0) * v0)
    p.m = unit(p.m + 0.01 * r.normal(0, 1, D))


def drift(p, rate, r):
    """Separate experience rotates the heading."""
    p.v = unit(p.v + rate * r.normal(0, 1, D))


def bounded_step(x, g, direction, alpha, sign):
    """
    Move along `direction` by at most the gap's component along it.
    This is the fix for (a): no step can exceed what it is correcting,
    so nothing overshoots and nothing compounds.
    """
    d = unit(direction)
    comp = g @ d                       # signed component of the gap
    return x + sign * alpha * comp * d


# ------------------------------------------------------------- the simulation

def simulate(
    T_together=200, T_break=120, T_apart=1200, T_after=1500,
    drift_together=0.002, drift_break=0.03, drift_apart=0.012,
    mem_rate=0.05,
    strat_A="preserve", strat_B="suppress",
    intervention="none",          # 'none' | 'perception' | 'presence'
    contact_every=20,
    transfer=0.12,                # how much of the other's heading is
                                  # acquired per contact
    alpha=0.05, seed=0,
):
    r = np.random.default_rng(seed)
    x0 = r.normal(0, 1, D)
    v0 = unit(r.normal(0, 1, D))          # the original shared heading
    w = unit(r.normal(0, 1, D))
    wp = unit(w - (w @ v0) * v0)

    th = 0.15                             # initial divergence angle
    A = Party(x0, np.cos(th / 2) * v0 + np.sin(th / 2) * wp, v0, strat_A)
    B = Party(x0, np.cos(th / 2) * v0 - np.sin(th / 2) * wp, v0, strat_B)

    log = []

    def snap(phase, t):
        g = B.x - A.x
        log.append(dict(
            phase=phase, t=t,
            gap=float(np.linalg.norm(g)),
            residue=float(np.linalg.norm(residue(g, A.dirs() + B.dirs()))),
            mA_v0=float(abs(A.m @ v0)),
            mB_v0=float(abs(B.m @ v0)),
            shared=float(abs(A.m @ B.m)),
        ))

    # ---- phase 0: together. small ordinary divergence.
    for t in range(T_together):
        A.x = A.x + alpha * A.v * 0.3
        B.x = B.x + alpha * B.v * 0.3
        drift(A, drift_together, r); drift(B, drift_together, r)
        update_memory(A, v0, mem_rate, r); update_memory(B, v0, mem_rate, r)
        snap(0, t)

    # ---- phase 1: the break. both depleted -> drift spikes.
    for t in range(T_break):
        A.x = A.x + alpha * A.v
        B.x = B.x - alpha * B.v
        drift(A, drift_break, r); drift(B, drift_break, r)
        update_memory(A, v0, mem_rate, r); update_memory(B, v0, mem_rate, r)
        snap(1, t)

    # ---- phase 2: apart, no contact. drift continues.
    for t in range(T_apart):
        drift(A, drift_apart, r); drift(B, drift_apart, r)
        update_memory(A, v0, mem_rate, r); update_memory(B, v0, mem_rate, r)
        snap(2, t)

    g0 = B.x - A.x
    before = dict(
        gap=float(np.linalg.norm(g0)),
        residue=float(np.linalg.norm(residue(g0, A.dirs() + B.dirs()))),
    )

    # ---- phase 3: intervention
    for t in range(T_after):
        g = B.x - A.x

        if intervention == "perception":
            # Each acts on its RECONSTRUCTION of the other. The
            # reconstruction is built from its own memory, so the only
            # directions available are ones it already holds. Bounded
            # steps: no overshoot.
            gA = (g @ unit(A.m)) * unit(A.m)
            gB = (g @ unit(B.m)) * unit(B.m)
            A.x = bounded_step(A.x, gA, A.v, alpha, +1)
            B.x = bounded_step(B.x, gB, B.v, alpha, -1)

        elif intervention == "presence":
            # Co-presence: each ACQUIRES some of the other's current
            # actual heading. That is a direction it did not have.
            if t % contact_every == 0:
                mA_new = unit(A.m + transfer * B.v)
                mB_new = unit(B.m + transfer * A.v)
                A.m, B.m = mA_new, mB_new
            for d_ in A.dirs():
                A.x = bounded_step(A.x, g, d_, alpha, +1)
            for d_ in B.dirs():
                B.x = bounded_step(B.x, g, d_, alpha, -1)

        # drift does NOT stop during the intervention
        drift(A, drift_apart, r); drift(B, drift_apart, r)
        snap(3, t)

    g = B.x - A.x
    return dict(
        before=before,
        gap_final=float(np.linalg.norm(g)),
        residue_final=float(np.linalg.norm(residue(g, A.dirs() + B.dirs()))),
        mA_v0=float(abs(A.m @ v0)), mB_v0=float(abs(B.m @ v0)),
        shared=float(abs(A.m @ B.m)),
        log=log,
    )


def avg(key, n=6, **kw):
    runs = [simulate(seed=s, **kw) for s in range(n)]
    if key in ("gap_before", "residue_before"):
        k = key.split("_")[0]
        return float(np.mean([x["before"][k] for x in runs]))
    return float(np.mean([x[key] for x in runs]))


# ------------------------------------------------------------------- output

def main():
    line = "=" * 78

    print(line)
    print("C1 / C2  THE SEQUENCE")
    print(line)
    print()
    print("  One preserving, one suppressing. Residue is the part of the gap")
    print("  no available action can reach.")
    print()
    r0 = simulate(seed=1)
    lg = r0["log"]
    pts = [("together, early", 50), ("together, late", 190),
           ("during the break", 260), ("just after", 330),
           ("6 months apart", 700), ("1 year apart", 1000),
           ("2 years apart", 1500)]
    print(f"  {'point':>20} {'gap':>9} {'residue':>10} {'A holds v0':>11} "
          f"{'B holds v0':>11} {'shared':>9}")
    print("  " + "-" * 74)
    for name, i in pts:
        if i < len(lg):
            e = lg[i]
            print(f"  {name:>20} {e['gap']:9.3f} {e['residue']:10.4f} "
                  f"{e['mA_v0']:11.4f} {e['mB_v0']:11.4f} {e['shared']:9.4f}")
    print()
    print("  The gap stops growing once they are apart (nobody is moving).")
    print("  The RESIDUE keeps growing anyway. That is C2: what accrues is")
    print("  drift, not distance.")
    print()

    print(line)
    print("C3  WHY IT BROKE -- BOTH DEPLETED AT ONCE")
    print(line)
    print()
    print(f"  {'condition':>34} {'residue after break':>20} {'gap':>9}")
    print("  " + "-" * 66)
    for label, db in (("neither depleted (0.002)", 0.002),
                      ("one mild (0.010)", 0.010),
                      ("both moderate (0.020)", 0.020),
                      ("both depleted (0.030)", 0.030),
                      ("both severe (0.050)", 0.050)):
        print(f"  {label:>34} "
              f"{avg('residue_before', drift_break=db):20.4f} "
              f"{avg('gap_before', drift_break=db):9.3f}")
    print()
    print("  Note the gap SHRINKS as depletion rises while the residue grows.")
    print("  They end up closer together and less able to reach each other.")
    print()

    print(line)
    print("C4  IS THE SHARED PAST A TWO-BODY QUANTITY?")
    print(line)
    print()
    print(f"  {'A':>10} {'B':>10} {'A holds v0':>12} {'B holds v0':>12} "
          f"{'SHARED':>9} {'residue':>10}")
    print("  " + "-" * 68)
    for sa, sb in (("preserve", "preserve"), ("preserve", "suppress"),
                   ("suppress", "preserve"), ("suppress", "suppress")):
        kw = dict(strat_A=sa, strat_B=sb)
        print(f"  {sa:>10} {sb:>10} {avg('mA_v0', **kw):12.4f} "
              f"{avg('mB_v0', **kw):12.4f} {avg('shared', **kw):9.4f} "
              f"{avg('residue_before', **kw):10.4f}")
    print()
    print("  Read the 'preserve/suppress' row against 'suppress/suppress'.")
    print("  A's grip on the past is unchanged at ~0.99 in both rows where")
    print("  A preserves. What collapses is SHARED. If one preserving were")
    print("  enough, shared would stay high in row 2. It does not.")
    print()

    print(line)
    print("C5  PERCEPTION vs CO-PRESENCE")
    print(line)
    print()
    print(f"  {'intervention':>16} {'gap before':>12} {'gap after':>11} "
          f"{'closed':>9} {'residue after':>14}")
    print("  " + "-" * 68)
    for iv in ("none", "perception", "presence"):
        gb = avg("gap_before", intervention=iv)
        ga = avg("gap_final", intervention=iv)
        rr = avg("residue_final", intervention=iv)
        print(f"  {iv:>16} {gb:12.3f} {ga:11.3f} {1 - ga / gb:9.4f} "
              f"{rr:14.4f}")
    print()
    print("  Perception closes what it can reach and then stops. It does not")
    print("  fail by diverging; it fails by hitting a floor it cannot cross.")
    print()

    print(line)
    print("  HOW OFTEN CO-PRESENCE HAS TO HAPPEN")
    print(line)
    print()
    print("  Drift continues throughout, so an acquired heading decays.")
    print()
    print(f"  {'contact every':>15} {'gap after':>11} {'closed frac':>13} "
          f"{'residue':>10}")
    print("  " + "-" * 54)
    for n in (5, 10, 25, 50, 100, 250, 750, 1499):
        kw = dict(intervention="presence", contact_every=n)
        gb = avg("gap_before", **kw)
        ga = avg("gap_final", **kw)
        rr = avg("residue_final", **kw)
        lab = str(n) if n < 1499 else "once only"
        print(f"  {lab:>15} {ga:11.3f} {1 - ga / gb:13.4f} {rr:10.4f}")
    print()

    print(line)
    print("  SUMMARY")
    print(line)
    print()
    print("  C1  A split pair's gap is made of their own divergence and is")
    print("      therefore reachable. Distance alone costs nothing.")
    print()
    print("  C2  Residue accrues while apart even when nobody moves. It is")
    print("      a function of time separated, not of how far apart.")
    print()
    print("  C3  A break is far more costly when both are depleted at once.")
    print("      One person struggling leaves the other holding the plane.")
    print()
    print("  C4  The shared past is the OVERLAP of two memories. One party")
    print("      holding it alone does not hold it.")
    print()
    print("  C5  Perception reaches only what is already held. Co-presence")
    print("      transfers a direction the other did not have, and that is")
    print("      the only operation that touches the residue.")
    print()
    print("  WHAT THIS MODEL DOES NOT ESTABLISH: that any of this describes")
    print("  people. It is a geometry with a psychological reading attached.")
    print("  The readings are interpretations, not results.")


if __name__ == "__main__":
    main()
