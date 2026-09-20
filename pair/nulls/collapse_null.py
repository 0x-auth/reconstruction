"""
Does the trace collapse because the accounts disagree ABOUT THE EVENT,
or would any two-account system destroy any trace?

compete.py showed: single-account keeps |<x,v>| at ~0.65 after the
event; competing collapses it to 0.007 by step 30. Factor 90.

That is only a finding if the collapse is SPECIFIC to the direction
the accounts disagree about. Three conditions, same trace v written
into the state every time:

    ALIGNED    accounts disagree along v      (the event's direction)
    SCRAMBLED  accounts disagree along u, random, independent of v
    ORTHOGONAL accounts disagree along u constructed orthogonal to v

If SCRAMBLED and ORTHOGONAL also collapse the trace, the effect is
generic averaging and the finding is withdrawn.
If only ALIGNED collapses it, the collapse is about the disagreement
being about that event.

Also swept: the angle between the conflict direction and the trace,
which turns a binary test into a curve. A real mechanism should
depend on cos(angle) -- maximal cancellation when aligned, none when
perpendicular.
"""

import numpy as np
from math import erfc, sqrt

rng = np.random.default_rng(20260919)


def make_A(d, spectral=0.92):
    A = rng.normal(0, 1, (d, d))
    return A * (spectral / np.max(np.abs(np.linalg.eigvals(A))))


def unit(d):
    v = rng.normal(0, 1, d)
    return v / np.linalg.norm(v)


def unit_at_angle(v, theta):
    """A unit vector at angle theta from v."""
    d = len(v)
    w = rng.normal(0, 1, d)
    w = w - (w @ v) * v
    w /= np.linalg.norm(w)
    return np.cos(theta) * v + np.sin(theta) * w


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -60, 60)))


def R(A, x, u, sign, s):
    return np.tanh(A @ x + sign * s * (x @ u) * u)


def run(d=16, T=60, event_step=20, strength=1.5, s=1.0, beta=4.0,
        noise=0.02, conflict_dir="aligned", angle=None,
        single=False):
    A = make_A(d)
    v = unit(d)                       # the event's trace direction

    if single:
        u = v
    elif angle is not None:
        u = unit_at_angle(v, angle)
    elif conflict_dir == "aligned":
        u = v
    elif conflict_dir == "scrambled":
        u = unit(d)
    elif conflict_dir == "orthogonal":
        u = unit_at_angle(v, np.pi / 2)
    else:
        raise ValueError(conflict_dir)

    truth = unit(d)
    belief = truth.copy()
    proj = []

    for t in range(1, T + 1):
        truth = np.tanh(A @ truth) + noise * rng.normal(0, 1, d)
        if t == event_step:
            truth = truth + strength * v

        rp = R(A, belief, u, +1, s)
        rm = R(A, belief, u, -1, s)

        if single:
            nxt = rp
        else:
            fp = -np.linalg.norm(truth - rp)
            fm = -np.linalg.norm(truth - rm)
            w = sigmoid(beta * (fp - fm))
            nxt = w * rp + (1.0 - w) * rm

        if t == event_step:
            nxt = nxt + strength * v

        proj.append(abs(nxt @ v))     # ALWAYS measured along v
        belief = nxt

    return np.array(proj), event_step


def batch(n=150, **kw):
    out = []
    for _ in range(n):
        p, e = run(**kw)
        out.append(p)
    return np.array(out), e


def welch(a, b):
    a, b = np.asarray(a), np.asarray(b)
    na, nb = len(a), len(b)
    va, vb = a.var(ddof=1), b.var(ddof=1)
    den = va / na + vb / nb
    if den == 0:
        return 0.0, 1.0
    t = (a.mean() - b.mean()) / sqrt(den)
    return t, erfc(abs(t) / sqrt(2))


def main():
    e = 20
    conds = {}
    conds["single"] = batch(single=True)[0]
    for c in ("aligned", "scrambled", "orthogonal"):
        conds[c] = batch(conflict_dir=c)[0]

    print("=" * 80)
    print("TRACE MAGNITUDE |<x,v>| AFTER THE EVENT")
    print("=" * 80)
    print()
    print(f"{'step':>6} {'single':>11} {'aligned':>11} "
          f"{'scrambled':>11} {'orthogonal':>11}")
    print("-" * 54)
    for k in [1, 2, 3, 5, 8, 12, 20, 30, 39]:
        if e + k >= conds["single"].shape[1]:
            break
        vals = [conds[c][:, e + k].mean()
                for c in ("single", "aligned", "scrambled", "orthogonal")]
        print(f"{k:>6} " + " ".join(f"{x:11.6f}" for x in vals))
    print()

    print("=" * 80)
    print("RATIO TO SINGLE-ACCOUNT, at step 30")
    print("=" * 80)
    print()
    k = 30
    base = conds["single"][:, e + k].mean()
    print(f"  single account holds: {base:.6f}")
    print()
    for c in ("aligned", "scrambled", "orthogonal"):
        m = conds[c][:, e + k].mean()
        t, p = welch(conds[c][:, e + k], conds["single"][:, e + k])
        print(f"  {c:>12}: {m:.6f}   ratio {m/base:7.4f}   "
              f"t={t:8.2f}  p={p:.3e}")
    print()
    print("  aligned vs scrambled:")
    t, p = welch(conds["aligned"][:, e + k], conds["scrambled"][:, e + k])
    print(f"    t = {t:.3f}   p = {p:.4e}")
    print("  aligned vs orthogonal:")
    t, p = welch(conds["aligned"][:, e + k], conds["orthogonal"][:, e + k])
    print(f"    t = {t:.3f}   p = {p:.4e}")
    print()
    print("  VERDICT REQUIRES: aligned collapses AND scrambled/")
    print("  orthogonal do not. if all three collapse, it is generic")
    print("  averaging and the finding is withdrawn.")
    print()

    print("=" * 80)
    print("ANGLE SWEEP -- does collapse depend on cos(angle)?")
    print("=" * 80)
    print()
    print(f"{'angle':>10} {'cos':>8} {'trace@30':>12} "
          f"{'ratio':>9} {'predicted':>11}")
    print("-" * 54)
    angles = [0, np.pi/12, np.pi/6, np.pi/4, np.pi/3,
              5*np.pi/12, np.pi/2]
    obs = []
    for a in angles:
        arr, _ = batch(n=100, angle=a)
        m = arr[:, e + 30].mean()
        obs.append((a, np.cos(a), m, m / base))
        print(f"{np.degrees(a):9.1f}° {np.cos(a):8.4f} "
              f"{m:12.6f} {m/base:9.4f} {'':>11}")
    print()
    cosv = np.array([o[1] for o in obs])
    ratv = np.array([o[3] for o in obs])
    r = np.corrcoef(cosv, ratv)[0, 1]
    print(f"  correlation(cos angle, trace ratio) = {r:+.4f}")
    print("  a cancellation mechanism predicts strong NEGATIVE")
    print("  correlation: more alignment, more destruction.")


if __name__ == "__main__":
    main()
