# Open threads

Everything unresolved as of 22 Sep 2026. Written so a reader with no memory
of the conversation can pick any one of these up.

Rule used throughout: a thread is listed as OPEN only if there is a concrete
test that would close it. Anything that cannot be falsified is in the last
section and marked as such.

---

## 1. The missing unit

**Status: open. This is the blocking problem for everything with a claimed
application.**

Λ is a ratio. Every result in this work is a ratio, and a ratio has no units
until something outside the structure supplies one.

Where it bites, in three places that look unrelated but are the same problem:

| context | shape is right | unit is missing |
|---|---|---|
| blockchain | `1 - tanh(Λ/2) -> 2e^-Λ`, matches `(q/(1-q))^k` to 1e-6 | what one unit of Λ costs an attacker |
| walker proper time | `τ = Σ|err|` converges to 1.7738775833, bounded by 2 | what one unit of τ is in seconds |
| mirror simulation | inside and outside charts agree on Δ | what one hop is in metres |

In Bitcoin the unit is hashing, which is exactly the cryptography. The claim
"a chain without cryptography" survives only if depth is expensive for some
other reason. SYMLOOP_MAX = 40 is a real non-cryptographic constraint but it
is a cap, not a price.

**Test that would close it:** exhibit any quantity internal to the construct
that is not a ratio. So far none found.

---

## 2. `shift` misclassification

**Status: open, known limitation, in `fs/darmiyan.py`.**

The three sectors are recovered from how a filesystem walk fails:

- parabolic -> self-link -> ELOOP
- rotation -> cycle -> ELOOP
- boost -> open chain -> no error, no end

`shift` (x -> x+1) is parabolic (Δ=0) but builds as an open chain, so the
walk classifies it as a boost. The classifier reads the *orbit topology*,
not the sector, and for a parabolic with its fixed point at infinity the
orbit is a chain.

**Test that would close it:** add the point at infinity as a real directory
and see whether `shift` then closes onto it. If it does, the classifier was
right and the chart was incomplete.

---

## 3. ELOOP conflates order 1 with order 2

**Status: open, may be unclosable.**

The OS returns the same errno for `a -> a` and for `a -> b -> a`. From the
walker's side a fixed point and a two-cycle are indistinguishable: both are
"undefined".

`readlink` tells them apart instantly. So the information is present and it
is the *walk* that cannot terminate.

**Open question:** is there a walker-side observable, using only hop count
and local name, that separates order 1 from order 2 before ELOOP fires? If
not, this is a genuine resolution limit and should be stated as one.

---

## 4. Residue conservation is a symmetric-pair law only

**Status: newly opened 22 Sep, in `pair/asym_pair.py`. This narrows an
earlier result.**

`pair/two_systems.py` found a conserved residue: the component of the gap
lying outside the span of available headings. Conserved to 8.9e-15.

With one side given hysteresis and the other left lossless:

```
SYMMETRIC  (both lossless)   3.413296455 -> 3.413296455   change 4.44e-16
ASYMMETRIC (B scars)         3.436265264 -> 12.208663291  change 8.77e+00
```

The conservation does not survive the asymmetry. The earlier result stands
but its scope is smaller than stated.

**Open question:** is there a modified residue that IS conserved for the
asymmetric pair? If the scar is included in the state, the pair becomes
lossless again by construction, which is trivial. The non-trivial version
asks for a quantity conserved without access to the scar.

---

## 5. CP holds exactly, T does not

**Status: result, with an open interpretive question.**

For a pair where one member is lossless and the other scars:

```
 baseline 8.123129892  diff 0.000e+00
        C 9.625739390  diff 1.503e+00
        P 9.625739390  diff 1.503e+00
       CP 8.123129892  diff 0.000e+00     <-- exact
        T 5.513863445  diff 2.609e+00
      CPT 5.513863445  diff 2.609e+00
```

CP is an exact symmetry of the pair. T is not, and CPT violation equals T
violation exactly, so C and P contribute nothing to the breakage. The whole
asymmetry localises in memory.

Note this is inverted from particle physics, where CPT holds and CP breaks.
That means the pair is not a local Lorentz-invariant theory, which is
unsurprising but should not be glossed over.

**Open question:** is the inversion meaningful or is it an artifact of C and
P being implemented as the same map here? They gave identical numbers, which
is suspicious. Needs a construction where C and P are genuinely distinct.

---

## 6. The arrow belongs to the pair

**Status: result, holds. Listed here because the generalisation is open.**

```
A alone   |x| over 40 steps:  min 2.577566  max 2.577566   monotone? False
pair      |scar|:              0.000000 -> 9.016526        monotone rising? True
pair      |a-b|:               2.299887 -> 16.227437
```

The lossless member has no monotone quantity, so no arrow of its own. The
pair has one.

**Open question:** does this need the asymmetry, or would two scarring
systems also produce an arrow that neither has alone? Not tested.

---

## 7. Four instants

**Status: result, exact. Extension open.**

A Möbius law has 3 degrees of freedom. Below four observations the solution
space crosses the parabolic locus, so the sector is undetermined. At k=3 the
Δ numerator factors exactly:

```
-(23 t0 + 40 t1)(1633 t0 - 1210 t1) / 52900
```

An earlier "percentage of samples with the right sector" table was a lattice
artifact (non-monotonic 33% / 25% / 46% = sampling noise) and has been
removed. The exact algebraic test replaced it.

**Open question:** is 4 the bound for every 3-parameter family, or specific
to `SL(2)`? Stated as a conjecture, not proven.

---

## 8. S(T) boundedness

**Status: verified numerically, open theoretically.**

`S(T) = N(T) - [θ(T)/π + 1]` stays in `[-0.965, +0.577]` while `N(T)` grows
by a factor of 22,491.

This is not new mathematics. It is the Riemann–von Mangoldt formula and the
boundedness of S(T) in the ranges computed is long known. Listed here only
because the compactification framing (infinite from inside, bounded from
outside) is the same shape as the walker's proper time, and whether that is
more than an analogy is untested.

**Bug fixed and worth recording:** the first version used
`arg(Gamma(1/4 + it/2)) - (t/2)log π`, which takes the wrong branch and
produced garbage in the thousands, which I then read out as confirming
boundedness. `mp.siegeltheta` is the continuous branch and gives the right
answer. Corrected in `riemann/st2.py`.

---

## 9. The mirror-simulation framework

**Status: designed, not built. Spec below is the whole of it.**

Central constraint: **you never write the mirror.** Write the relation once;
the mirror is the same artifact read by the other resolver. Two simulations
means the design failed.

1. **The artifact.** Not code. States as nodes, transitions as links.
   Nothing in it names the domain.
2. **Resolver I (inside).** Knows hop count, local name, own accumulated
   error. Clock is `τ = Σ|err|`. Hits ELOOP. Reports undefined at fixed
   points.
3. **Resolver O (outside).** `readlink`, full link table, never walks, never
   fails, has no proper time.
4. **The bridge invariant.** One quantity both compute independently and must
   agree on (Δ or κ here). Load-bearing: without it the construction is
   decorative.
5. **The payload is the disagreements:**
   - I reports ELOOP where O reports a fixed point (deadlock, stall, control
     lock).
   - I reports infinity where O reports an ordinary point in another chart
     (gimbal lock, coordinate singularity).

   Distinguishing those two is the thing no single-chart simulator can do.

**Open:** build it on a system whose answer is already known (the Möbius
case) before any application domain. And item 1 above still applies: the
unit is missing.

---

## 10. Computation as topology

**Status: working, in `fs/nocode.py`. Limits known.**

A DFA is four symlinks; the input is the path; the kernel's resolver runs it.
Arithmetic works by path concatenation and `succ`/`pred` cancel inside
`namei()`.

**Bug worth recording:** the first version used `os.path.realpath`, which is
pure Python and walks the links itself. That made the demonstration circular.
`O_PATH` plus `/proc/self/fd` forces kernel resolution, and only then does
the claim hold. The ELOOP ceiling then appears where it should: `succ×40`
resolves, `succ×41` gives errno 40.

**Hard limit:** one path is capped at 40 resolutions, so this machine has a
word size and it is the kernel's. Any computation needing depth > 40 must be
chunked, at which point our code is running again and the claim weakens.

**Open:** is there a construction that gets unbounded computation with
bounded path depth? Composing through directory nesting rather than symlink
chaining is the obvious candidate and is untested.

---

## 11. Not falsifiable, listed for honesty

These recur in conversation and none of them has a test attached. They are
not claims.

- "Gödel, halting, and the GR/QM bridge are the same statement." A family
  resemblance, not a theorem. No formal reduction attempted.
- "The structure IS the meaning." Slogan.
- κ as a definition of intelligence (ability to hold two incompatible
  accounts of one event without collapsing either). Suggestive, no measure
  proposed.
- The Killing form on `sl(2,R)` having signature (1+, 2-) and its light cone
  being the parabolic locus is a *fact*, verified. That the fact explains
  anything about physical spacetime is not.

---

## 12. Nulled, do not revisit without new reason

Five constructions were built and failed identically: `conflict`,
`conflict2`, `discrete`, `compete`, `collapse_null`. In every one the event
never mattered.

Root cause: property questions were being asked of a relational structure.
Δ belongs to the relation, never to the state.

`collapse_null.py` in particular killed a finding that had already been
announced: trace collapse under two accounts is generic averaging. Angle
correlation -0.077; aligned, scrambled and orthogonal are identical.
Withdrawn.

Kept in `pair/nulls/` so the failure is on the record.
