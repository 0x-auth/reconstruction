"""
(A) What stops it: absorbed error vs rotated error.
(B) x -> 1 + 1/x read as an error-driven system.

PART A

Last run: orthogonal error does not stop motion, it converts
translation into rotation. Path length was identical (320.00) in
every condition. The system always moves the same amount; only
whether the motion accumulates changes.

Reason: orthogonal to the CURRENT heading rotates the heading, so
next step the same error is partly aligned again. The frame turns.

So the question is what happens when the orthogonal component is
ABSORBED rather than allowed to turn the frame. Three regimes:

  FREE      heading updates from the full step       -> curves
  ROTATED   error made orthogonal each step          -> circles
  ABSORBED  heading held fixed; the orthogonal part
            is dissipated instead of steering        -> rests?

Physical reading: absorbed = the error meets something that takes
it without converting it into a change of direction. Held, not
redirected.

PART B

x -> 1 + 1/x as error dynamics:
    e(x) = f(x) - x = 1 + 1/x - x
Is the error along the motion, and what does it do at the fixed
point?
"""

import numpy as np

rng = np.random.default_rng(53)


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-15 else v


def perp(e, v):
    vh = unit(v)
    return e - (e @ vh) * vh


def run(mode, d=8, T=4000, alpha=0.08, err_mag=1.0,
        damping=1.0, seed=0):
    """
    mode: 'free'      error as generated, heading follows motion
          'rotated'   error forced orthogonal, heading follows motion
          'absorbed'  error forced orthogonal, heading HELD,
                      orthogonal part damped by `damping`
    """
    r = np.random.default_rng(seed)
    x = r.normal(0, 1, d)
    v0 = unit(r.normal(0, 1, d))
    v = v0.copy()
    traj = [x.copy()]
    steps = []

    for t in range(T):
        e = unit(r.normal(0, 1, d) * 0.3 + v) * err_mag

        if mode == "free":
            e_eff = e
        else:
            ep = perp(e, v)
            n = np.linalg.norm(ep)
            e_eff = unit(ep) * err_mag if n > 1e-14 else np.zeros(d)

        if mode == "absorbed":
            e_eff = e_eff * (1.0 - damping)

        x_new = x + alpha * e_eff
        steps.append(np.linalg.norm(x_new - x))

        if mode in ("free", "rotated"):
            dv = x_new - x
            if np.linalg.norm(dv) > 1e-12:
                v = unit(dv)
        # 'absorbed': v stays v0 -- the heading is held

        x = x_new
        traj.append(x.copy())

    traj = np.array(traj)
    late = traj[-500:]
    return {
        "net": float(np.linalg.norm(traj[-1] - traj[0])),
        "path": float(np.sum(steps)),
        "late_step": float(np.mean(steps[-200:])),
        "late_drift": float(np.linalg.norm(traj[-1] - traj[-500]) / 500),
        "spread": float(np.mean(np.std(late, axis=0))),
    }


print("=" * 78)
print("PART A -- WHAT ACTUALLY STOPS IT")
print("=" * 78)
print()
print(f"  {'mode':>28} {'net disp':>10} {'path len':>10} "
      f"{'step size':>11} {'late drift':>12}")
print("  " + "-" * 74)
for label, kw in (
    ("free (error aligned)",        dict(mode="free")),
    ("rotated (orthogonal)",        dict(mode="rotated")),
    ("absorbed, damping 0.0",       dict(mode="absorbed", damping=0.0)),
    ("absorbed, damping 0.5",       dict(mode="absorbed", damping=0.5)),
    ("absorbed, damping 0.9",       dict(mode="absorbed", damping=0.9)),
    ("absorbed, damping 1.0",       dict(mode="absorbed", damping=1.0)),
):
    res = [run(seed=s, **kw) for s in range(6)]
    print(f"  {label:>28} "
          f"{np.mean([r['net'] for r in res]):10.4f} "
          f"{np.mean([r['path'] for r in res]):10.2f} "
          f"{np.mean([r['late_step'] for r in res]):11.6f} "
          f"{np.mean([r['late_drift'] for r in res]):12.6f}")
print()
print("  'absorbed, damping 0.0' is the key row: the error is still")
print("  full size and still orthogonal, but the HEADING IS HELD, so")
print("  the orthogonal push never becomes a new direction.")
print()

print("=" * 78)
print("  held heading, error at full magnitude, varying alignment")
print("=" * 78)
print()


def run_held(orth, d=8, T=4000, alpha=0.08, err_mag=1.0, seed=0):
    r = np.random.default_rng(seed)
    x = r.normal(0, 1, d)
    v = unit(r.normal(0, 1, d))          # HELD, never updated
    traj = [x.copy()]
    for t in range(T):
        e = unit(r.normal(0, 1, d) * 0.3 + v) * err_mag
        ep = perp(e, v)
        if np.linalg.norm(ep) > 1e-14:
            e_eff = (1 - orth) * e + orth * unit(ep) * err_mag
            e_eff = unit(e_eff) * err_mag
        else:
            e_eff = e
        x = x + alpha * e_eff
        traj.append(x.copy())
    traj = np.array(traj)
    along = (traj[-1] - traj[0]) @ v
    across = np.linalg.norm(perp(traj[-1] - traj[0], v))
    return along, across


print(f"  {'orth frac':>10} {'displacement ALONG v':>22} "
      f"{'displacement ACROSS v':>23}")
print("  " + "-" * 58)
for o in (0.0, 0.25, 0.5, 0.75, 0.9, 1.0):
    a = [run_held(o, seed=s) for s in range(6)]
    print(f"  {o:10.2f} {np.mean([t[0] for t in a]):22.4f} "
          f"{np.mean([t[1] for t in a]):23.4f}")
print()
print("  with the heading held, motion ALONG the direction of travel")
print("  goes to zero as the error becomes orthogonal. the across")
print("  component is a random walk -- it wanders but does not")
print("  progress, and it does not feed back into direction.")
print()
print("  THE DISTINCTION THAT MATTERS:")
print("    rotated  -> the error steers. the system circles forever.")
print("    absorbed -> the error is taken without steering. the")
print("                system stops going anywhere.")
print()
print("  so what ends it is not making the error orthogonal. it is")
print("  having something that RECEIVES the orthogonal component")
print("  without converting it into a new direction.")
print()

print("=" * 78)
print("PART B -- x -> 1 + 1/x AS AN ERROR-DRIVEN SYSTEM")
print("=" * 78)
print()
print("  error e(x) = f(x) - x = 1 + 1/x - x")
print("  motion   v = sign of the step taken")
print()
PHI = (1 + np.sqrt(5)) / 2
print(f"  {'x':>12} {'f(x)':>12} {'e = f(x)-x':>13} "
      f"{'|e|':>10} {'dir':>6}")
print("  " + "-" * 58)
x = 1.0
for n in range(12):
    fx = 1 + 1 / x
    e = fx - x
    print(f"  {x:12.8f} {fx:12.8f} {e:13.8f} {abs(e):10.8f} "
          f"{'+' if e > 0 else '-':>6}")
    x = fx
print()
print(f"  fixed point phi = {PHI:.10f}")
print()
print("  the error ALTERNATES SIGN every step and shrinks each time.")
print("  that is what mu < 0 means: the multiplier is negative")
print(f"  (mu = -1/phi^2 = {-1/PHI**2:.9f}), so every step overshoots")
print("  and the next one corrects back.")
print()
print("  in 1-D there is no 'orthogonal'. the only directions are")
print("  along and against. so this system has no way to stop other")
print("  than shrinking the error -- and it shrinks geometrically,")
print("  by a factor of 1/phi^2 = 0.382 per step, forever, without")
print("  ever reaching zero.")
print()
print(f"  {'step':>6} {'|e|':>14} {'ratio to prev':>15}")
print("  " + "-" * 38)
x = 1.0
prev = None
for n in range(1, 14):
    fx = 1 + 1 / x
    e = abs(fx - x)
    rr = e / prev if prev else np.nan
    print(f"  {n:6d} {e:14.10f} {rr:15.9f}")
    prev = e
    x = fx
print()
print(f"  the ratio converges to 1/phi^2 = {1/PHI**2:.9f}")
print()
print("  SO: x -> 1 + 1/x is the ALIGNED case, in one dimension,")
print("  with a shrinking error. it never stops. it only gets")
print("  closer, by a fixed fraction, forever. exactly the regime")
print("  Part A says cannot terminate.")
print()
print("  and it alternates -- overshoot, correct, overshoot. the")
print("  system oscillates around the answer without settling on it,")
print("  which is what a negative multiplier does.")
print()
print("  to actually stop, it would need a second dimension for the")
print("  error to go into, and something there to absorb it.")
