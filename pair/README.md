# pair — two systems that were one

A geometric model of separation and repair. Built 20–21 September 2026.

Everything is vectors and spans. The psychological readings in the
comments are interpretations, not results — that a pair of vectors
behaves this way is a fact; that people do is an assumption.

## The primitives

    state x      where a system is
    heading v    the one direction it can act along
    memory m     its grip on the shared past
    gap g        x_B − x_A, belongs to neither, only to the pair

A system moves only along directions it holds. The pair spans at most
four. The **residue** is the component of the gap outside that span —
not hard to close, *unreachable*: no available action has any component
along it. Exactly conserved.

## What the runs establish

**A split pair has no residue.** Zero to machine precision (2.3e-13) at
every divergence angle from 2.9° to 90°. Two things that were one can
close any gap made of their own divergence, however wide, because the
gap lies entirely in the plane their headings span. Distance is free.

**Residue is created by drift, and accrues per unit of time apart.**
Not distance. With the gap frozen — nobody moving — the residue still
grows: 1.72 → 2.17 → 2.28 → 3.55. A drift of 0.001 per step locks 2.9%
permanently; 0.03 locks 79%.

**A break costs more when both are depleted at once.** Residue 1.28
(neither) → 1.82 (one) → 3.34 (both) → 3.81 (both severe). And the gap
*shrinks* as depletion rises while the residue grows: they end up closer
together and less able to reach each other.

**The shared past is a two-body quantity.** One party preserving while
the other suppresses gives overlap 0.041 — *lower* than both suppressing
(0.135) — while the preserver's own grip stays at 0.994, untouched. Two
who both let go drift toward a common nothing; one holding and one
pushing maximizes the angle. One person cannot hold it alone.

**Joint action beats contact beats shared noise.** 85.2% / 82.8% / 79.9%.
Modelling co-living as correlated noise makes it *worse* than periodic
meeting, because identical rotation forces headings parallel and two
parallel headings span a line, not a plane. What works is generating a
direction neither had alone — and it works best when that direction is
mostly (≈0.8) novel rather than a blend of what each already brought.

**Contact frequency has an optimum.** Every 25 steps closes 80%; every 5
closes 68%; once only closes 73%. Too-frequent transfer keeps overwriting
the acquired heading with the other's newest one, which is itself
drifting — chasing rather than holding.

## Files

| file | what it does |
|---|---|
| `pair_model.py` | the full sequence, five claims, self-contained, fixes documented in the header |
| `two_systems.py` | the residue is exactly conserved; effort is irrelevant, dimension count decides |
| `split_self.py` | split pairs have no between; drift is the entire cost |
| `coliving2.py` | joint action vs contact vs shared noise; the novelty optimum |
| `orthogonal_error.py` | what drives is e·v, not \|e\|; shrinking never terminates |
| `constrained.py` | orthogonality alone circles; orthogonality + held heading stops |
| `nulls/collapse_null.py` | kept: it killed a result already announced |

## Nulls not included

Four constructions failed before this model worked — smooth conflict,
confined conflict, discrete conflict, competing accounts. All failed the
same way: the event never mattered, because they asked property questions
of a relational structure. `collapse_null.py` is kept because it
disconfirmed a finding that had already been stated.
