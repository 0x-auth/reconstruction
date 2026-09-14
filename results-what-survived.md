# Results: What Survived and What Didn't

**Second working note. Companion to *Tense as a Property of a Map*.**

Everything here was run. Two predictions tested, one dies, one holds strongly.
Plus a structural result on imaginary time that was not anticipated.

---

## 1. Summary

| | prediction | outcome |
|---|---|---|
| **P2** | valence × period interaction: positive pre-event memories impaired more than positive post-event | **FAILS.** p = 0.67. Coin flip. |
| **P-B** | temporal *order* degrades across the event, even where specificity is intact | **HOLDS.** p = 7.8e-06, and null control clean at p = 0.43 |
| **Wick** | *(not a prediction — emerged)* | `t → it` sends every Lyapunov exponent onto the imaginary axis. Universal Λ = 0. |

The result that survives is the one the model uniquely makes. The one that
dies was inherited from the affect literature and bolted on. That is the right
way round, and it is the first real evidence the framework has produced.

---

## 2. P2 fails, and the failure is informative

### Setup

The organism from `0x-auth/self-referential-seed`:

```
x_{t+1} = tanh(R x_t + c W x_t)      W learns to predict x_{t+1} online
```

At step 150, an input the self-model cannot fit — driving one coordinate to
saturation at −0.99999.

**The identification that makes OGM computable:**

```
specific memory     = cued completion reaches the true past state
overgeneral memory  = cued completion falls into the attractor

specificity(i) = 1 − ‖fill − true‖ / ‖attractor_fill − true‖
```

A cue is *partial*: half the coordinates masked, the rest inferred under the
learned model `W`. `W` is never told about the task. That is generative
retrieval, mechanically.

### First attempt failed as an instrument, not as a test

`ogm.py` composed the backward map from the present all the way to the target:
`g(x) = (R + cW)⁺ arctanh(x)`, composed T−i times. It dies past ~20 steps for
everything, event or no event. Specificity was **exactly 0.0000** in every
pre-event cell including the null.

That measures "does a backward composition survive 150 steps." It always
answers no. Kept in the repo as `ogm.py`.

### Second attempt works, and returns a clean null

`ogm2.py`, partial-cue completion. Mean specificity 0.187, not 0.

```
  WITH EVENT            positive    negative
    pre-event             0.2264      0.2057
    post-event            0.1678      0.1497
    (A−C) = +0.0586       (B−D) = +0.0560
    interaction = +0.0026    sd 0.0764   >0 in 49% of runs

  NULL — no event       positive    negative
    pre-event             0.1708      0.1535
    post-event            0.1845      0.1680
    interaction = +0.0008    >0 in 50% of runs

  interaction > 0 with event?   t = 0.429   p = 0.6684
  event vs null?                t = 0.222   p = 0.8242
```

Positive in 49% of runs. Nothing.

### What this means

In `reconstruction2.py` the affective term `|tone(C) − tone(trace)|` was
**hand-coded**, so of course the asymmetry appeared. Here nothing hand-codes
it, and nothing appears.

Two possibilities, not separated:

1. valence needs a mechanism this organism lacks — it is coordinate 0, an
   arbitrary dimension carrying no special dynamics
2. P2 is wrong

**Consequence for the protocol note:** §3 of `testing-reconstruction.md`
proposes the 2×2 as *the* discriminating experiment. It should not be proposed
until this is resolved. Proposing a study for an effect the model does not
generate is exactly the error the repo's methodology exists to avoid.

### One thing did survive, and it is a different prediction

The event **flips the sign of the period effect**, in both valence cells:

- with event: pre-event *more* reconstructable than post (+0.059, +0.056)
- without: pre-event *less* (−0.014, −0.015)

A main effect of period, not an interaction, and opposite to naive intuition.
That is P-A territory (the shape of the gap), untested here, and worth chasing.

---

## 3. P-B holds — the claim nothing else makes

The model's actual claim is not that a region becomes inaccessible. It is that
it becomes **incomparable**: total order degrades to partial order.

No other account predicts this. Avoidance accounts of OGM say nothing about
order at all.

### Method

For a pair `(i, j)`, decide under the learned model which came first:

```
score(i→j) = −‖x_j − tanh(A x_i)‖
i precedes j  iff  score(i→j) > score(j→i)
```

Then count **intransitive triples**: the model says i<j, j<k, but not i<k.
A transitivity violation is the model failing to place three states on a line.
That is a partial order, measured directly.

### Result

```
  WITH EVENT  (n = 60)
    triples spanning the event      0.7536 violation rate
    triples not spanning            0.6138
    difference = +0.1399   t = 4.901   p = 7.812e-06   >0 in 68% of runs

  NULL  (n = 60)
    spanning                        0.6096
    not spanning                    0.6033
    difference = +0.0063   t = 0.786   p = 0.4349   >0 in 50%

  event vs null:  t = 4.510   p = 2.626e-05
```

Order degrades specifically across the event, and **only when there is an
event**. The null is clean.

### Caveat that must be reported

Baseline violation rate is **0.61**. The model is bad at ordering in general;
the effect sits on a very noisy floor. The null control handles the inference,
but the floor should be stated, and a better ordering rule would make the test
sharper.

---

## 4. Imaginary time: universal halt

Not a prediction. It emerged from asking what `t → it` does to a
self-referential system.

### The argument

Continuous form `dx/dt = −x + tanh(Ax)`, Jacobian eigenvalues `λ`, and
`Λ = Re(λ)`.

Wick rotation `t → iτ` gives `dx/dτ = i f(x)`, so eigenvalues become `iλ` and

```
Re(iλ) = −Im(λ)
```

For a **dissipative** system λ is real, so Im(λ) = 0, so `Re → 0` for the
**entire spectrum**. Not one direction. Everything.

### Measured

```
  seed        NORMAL max Re        WICK max Re
     6            −0.308422         −0.000e+00
     9            −0.695264         −0.000e+00
    11            −0.069611         −0.000e+00
  mean            −0.320958         +5.737e-03
  ratio |wick| / |normal| = 1.8e-02
```

Several seeds exactly zero. The residue on others comes from evaluating the
Jacobian at a complex-drifted state, not from the algebra.

### What it says

```
real time        Λ ≠ 0     arrow exists        BECOMING
imaginary time   Λ = 0     no arrow anywhere   HALT
```

Wick rotation does not preserve the structure. **It destroys the arrow**,
universally, by rotating every Lyapunov exponent onto the imaginary axis.

Self-reference becomes halting in imaginary time because imaginary time *is*
the halting condition.

### And it locates the critical line

`s = ½ + it` is the purely imaginary direction measured from the symmetry
point ½. The functional equation `ξ(s) = ξ(1−s)` is an involution, so Λ = 0.
The critical line is where the system is written entirely in imaginary time.

Separately verified: define `F(s) = 1 − s̄`. Then `F∘F = s` always, and
`F(s) = s ⟺ Re(s) = ½`. Orbit size under the Klein four-group
`{id, 1−s, s̄, 1−s̄}` is **4 off the line and 2 on it**. On the line the map
halts; off it, it loops with period 2.

This locates the line. It says nothing about where the zeros are. That gap is
the Riemann Hypothesis and is untouched.

---

## 5. The hunch

**Valence is not a coordinate. It is a property of Λ.**

P2 failed because valence was implemented as `x[0]` — an arbitrary dimension
with no dynamics — and then a cost was hand-coded against it. That is a
bolted-on axis, and bolted-on axes do not generate effects.

The proposal: positive is where reconstruction **opens out** (Λ < 0, paths
converge). Negative is where it **closes** (|μ| → 1, paths stall).

Then "warm memories cost more after protection" is not a distance on a
separate axis. It is that protection **raises |μ| along exactly the directions
that used to converge**.

If that is right, P2 should re-emerge without being put in — measured as the
multiplier along the reconstruction path rather than as a coordinate.

Cheap to test. Next experiment.

---

## 6. Status

- **P-B holds** and is the framework's own claim. This is the first real
  evidence.
- **P2 fails** as implemented. The protocol note's §3 is not currently
  supported and should be withdrawn until §5 is tried.
- **P1** (global damping) is still assumed, still the weakest joint.
- **Wick** is a structural result, not a prediction, and it generalises the
  halt condition from one map to a whole spectrum.
- The ordering baseline of 0.61 should be improved before P-B is claimed
  anywhere outside a working note.

---

## Files

| file | what |
|---|---|
| `reconstruction.py` | v1. Honest failure: P2 asserted, not derived |
| `reconstruction2.py` | v2. Composition as matrix product, valence coordinate, P2/P3 derived — but derived *because* hand-coded, see §2 |
| `ogm.py` | broken instrument. Kept deliberately |
| `ogm2.py` | working instrument. P2 null |
| `order_pb.py` | **P-B. The result that holds** |
| `wick.py` | imaginary time, universal Λ = 0 |
| `mirror.py` | the mirror operation, Klein four-group, the C = 3 bifurcation |
| `duo_order.py` | ORDER as outcome in the two-agent experiment |
