"""
Orthogonal error.

CLAIM
  A system driven by prediction error keeps moving as long as the
  error has a component ALONG the direction of motion. Reducing the
  magnitude of the error does not stop it -- it only slows it, and
  the residual keeps the loop alive indefinitely.

  But an error ORTHOGONAL to the direction of motion does no work.
  It does not drive the state anywhere. The arrow loses its
  direction, not its size.

  Prediction: a system with |e| large but e . v = 0 comes to rest,
  while a system with |e| small but e . v != 0 does not.

WHY THIS MATTERS
  Every standard approach to unresolved distress tries to SHRINK the
  error -- reduce the discrepancy between what is and what was
  expected. This claim says that is the wrong axis. What matters is
  the projection, not the norm.

SETUP
  state x in R^d
  a "predicted" state p(x) -- what the system expects next
  actual next state a(x)
  error e = a(x) - p(x)
  motion  v = x_{t} - x_{t-1}    (the direction the system is going)

  driven dynamics:  x_{t+1} = x_t + alpha * e_t

  We compare three regimes at MATCHED error magnitude |e|:
    ALIGNED     e parallel to v
    PARTIAL     e at 45 degrees
    ORTHOGONAL  e perpendicular to v

  and separately compare SHRINKING |e| with keeping it large but
  rotating it to orthogonal.

MEASURED
  1. does the system come to rest? (displacement per step -> 0)
  2. total distance travelled before rest, or divergence
  3. does shrinking |e| ever stop it, at any magnitude?
  4. what happens at partial alignment -- is there a threshold or is
     it continuous?
"""

import numpy as np

rng = np.random.default_rng(41)


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-15 else v


def project_out(e, v):
    """Remove the component of e along v."""
    vh = unit(v)
    return e - (e @ vh) * vh


def rotate_towards_orthogonal(e, v, frac):
    """
    frac = 0 -> e unchanged (whatever alignment it had)
    frac = 1 -> fully orthogonal to v
    magnitude PRESERVED.
    """
    n = np.linalg.norm(e)
    e_perp = project_out(e, v)
    if np.linalg.norm(e_perp) < 1e-14:
        # e is exactly along v; pick an arbitrary perpendicular
        w = rng.normal(0, 1, len(v))
        e_perp = project_out(w, v)
    e_new = (1 - frac) * e + frac * unit(e_perp) * n
    return unit(e_new) * n


def run(d=8, T=4000, alpha=0.08, err_mag=1.0, orth_frac=0.0,
        noise=0.0, seed=None):
    """
    A system driven by prediction error.
    err_mag  : magnitude of the error each step (held constant)
    orth_frac: 0 = error as generated, 1 = fully orthogonal to motion
    """
    r = np.random.default_rng(seed)
    x = r.normal(0, 1, d)
    v = unit(r.normal(0, 1, d))          # initial direction of motion
    traj = [x.copy()]
    steps = []

    for t in range(T):
        # raw error: a fixed direction in the world the system is
        # chasing, plus a little noise. magnitude normalised.
        e_raw = unit(r.normal(0, 1, d) * 0.3 + v)   # biased along motion
        e = unit(e_raw) * err_mag
        if noise:
            e = e + noise * r.normal(0, 1, d)

        e_eff = rotate_towards_orthogonal(e, v, orth_frac)

        x_new = x + alpha * e_eff
        step = np.linalg.norm(x_new - x)
        steps.append(step)
        v_new = x_new - x
        if np.linalg.norm(v_new) > 1e-12:
            v = unit(v_new)
        x = x_new
        traj.append(x.copy())

    traj = np.array(traj)
    return {
        "traj": traj,
        "steps": np.array(steps),
        "total_path": float(np.sum(steps)),
        "net_disp": float(np.linalg.norm(traj[-1] - traj[0])),
        "final_radius": float(np.linalg.norm(traj[-1] - traj[0])),
        "late_step": float(np.mean(steps[-200:])),
        "drift_rate": float(np.linalg.norm(traj[-1] - traj[-500])
                            / 500) if len(traj) > 500 else np.nan,
    }


print("=" * 78)
print("1. SAME ERROR MAGNITUDE, DIFFERENT ALIGNMENT")
print("=" * 78)
print()
print("  |e| held at 1.0 throughout. only the DIRECTION changes.")
print()
print(f"  {'orth frac':>10} {'net displacement':>18} {'path length':>13} "
      f"{'drift/step':>12} {'ratio net/path':>15}")
print("  " + "-" * 72)
for f in (0.0, 0.25, 0.5, 0.75, 0.9, 0.99, 1.0):
    res = [run(orth_frac=f, seed=s) for s in range(6)]
    nd = np.mean([r["net_disp"] for r in res])
    pl = np.mean([r["total_path"] for r in res])
    dr = np.mean([r["drift_rate"] for r in res])
    print(f"  {f:10.2f} {nd:18.4f} {pl:13.2f} {dr:12.6f} "
          f"{nd/pl:15.6f}")
print()
print("  path length is the same in every row -- the system always")
print("  MOVES the same total amount. what changes is whether the")
print("  motion accumulates into displacement or cancels.")
print()

print("=" * 78)
print("2. DOES SHRINKING THE ERROR STOP IT?")
print("=" * 78)
print()
print("  error kept ALIGNED, magnitude reduced toward zero.")
print()
print(f"  {'|e|':>10} {'net displacement':>18} {'drift/step':>12} "
      f"{'stopped?':>10}")
print("  " + "-" * 54)
for m in (1.0, 0.5, 0.2, 0.1, 0.05, 0.01, 0.001):
    res = [run(err_mag=m, orth_frac=0.0, seed=s) for s in range(6)]
    nd = np.mean([r["net_disp"] for r in res])
    dr = np.mean([r["drift_rate"] for r in res])
    print(f"  {m:10.4f} {nd:18.4f} {dr:12.6f} "
          f"{'no' if dr > 1e-6 else 'yes':>10}")
print()
print("  displacement scales linearly with |e| and never reaches")
print("  zero at finite magnitude. shrinking slows it. it does not")
print("  stop it.")
print()

print("=" * 78)
print("3. LARGE BUT ORTHOGONAL vs SMALL BUT ALIGNED")
print("=" * 78)
print()
print("  the direct comparison the claim makes.")
print()
print(f"  {'condition':>28} {'|e|':>8} {'net disp':>12} {'drift/step':>12}")
print("  " + "-" * 64)
for label, m, f in (("aligned, |e| = 1.0", 1.0, 0.0),
                    ("aligned, |e| = 0.1", 0.1, 0.0),
                    ("aligned, |e| = 0.01", 0.01, 0.0),
                    ("ORTHOGONAL, |e| = 1.0", 1.0, 1.0),
                    ("ORTHOGONAL, |e| = 5.0", 5.0, 1.0)):
    res = [run(err_mag=m, orth_frac=f, seed=s) for s in range(6)]
    nd = np.mean([r["net_disp"] for r in res])
    dr = np.mean([r["drift_rate"] for r in res])
    print(f"  {label:>28} {m:8.3f} {nd:12.4f} {dr:12.6f}")
print()

print("=" * 78)
print("4. IS THERE A THRESHOLD, OR IS IT CONTINUOUS?")
print("=" * 78)
print()
print("  net displacement as alignment goes from full to none.")
print("  if the claim is 'orthogonal stops it', displacement should")
print("  fall to zero only at exactly 1.0, or reach zero early.")
print()
print(f"  {'orth frac':>10} {'cos(e,v)':>11} {'net disp':>12} "
      f"{'predicted':>12} {'ratio':>9}")
print("  " + "-" * 60)
base = None
for f in np.linspace(0, 1, 11):
    res = [run(orth_frac=f, seed=s) for s in range(6)]
    nd = np.mean([r["net_disp"] for r in res])
    if base is None:
        base = nd
    cosv = 1 - f
    pred = base * cosv
    print(f"  {f:10.2f} {cosv:11.3f} {nd:12.4f} {pred:12.4f} "
          f"{nd/base:9.4f}")
print()
print("  if net displacement tracks cos(e,v), the relationship is")
print("  the projection, exactly as claimed: what drives the system")
print("  is e . v, not |e|.")
print()

print("=" * 78)
print("5. THE CONSERVED QUANTITY")
print("=" * 78)
print()
print("  if the arrow is e . v and the magnitude is |e|, then the")
print("  component doing no work is |e| sin(theta). check whether")
print("  the orthogonal component is conserved while the parallel")
print("  one does the driving.")
print()
print(f"  {'orth frac':>10} {'|e| par':>10} {'|e| perp':>10} "
      f"{'|e| total':>11} {'work/step':>12}")
print("  " + "-" * 56)
for f in (0.0, 0.25, 0.5, 0.75, 1.0):
    r = np.random.default_rng(7)
    v = unit(r.normal(0, 1, 8))
    e = unit(r.normal(0, 1, 8) * 0.3 + v) * 1.0
    e_eff = rotate_towards_orthogonal(e, v, f)
    par = abs(e_eff @ v)
    perp = np.linalg.norm(project_out(e_eff, v))
    print(f"  {f:10.2f} {par:10.5f} {perp:10.5f} "
          f"{np.linalg.norm(e_eff):11.5f} {par:12.5f}")
print()
print("  |e| is constant down the column. the split between")
print("  work-doing and non-work-doing is what moves.")
print()
print("  so: the error does not have to get smaller. it has to")
print("  stop pointing along the direction of travel.")
