# reconstruction

Memory as an operator, not a store. What "unresolved" means mathematically.

**Private working repo. Nothing here is established.**

---

## The idea in one paragraph

Standard accounts say a traumatic memory is *stored differently* — fragmented,
poorly indexed, not filed as past. But reconsolidation research shows a
recalled memory is rewritten on each retrieval. There is no stored copy being
fetched. So "filed as past" cannot mean written to a location.

This proposes: **past is a convergence property of the operator that generates
the memory.** Reconstruction is a composition of maps. If the composition
converges, the event lands and is past. If it circles, it never lands and stays
present. The multiplier |μ| decides which.

An event the operator cannot reconstruct does not just become painful. It
becomes **incomparable** — not earlier or later than anything. A total order
degrades to a partial order. That is the arrow of time failing locally.

## Status

| prediction | result |
|---|---|
| **P-B** order degrades across the event | **holds**, p = 7.8e-06, clean null |
| **P2** valence × period interaction | **fails**, p = 0.67 |
| **Wick** t → it | universal Λ = 0. Not predicted, emerged |

Read `results-what-survived.md` first.

## Files

| file | what |
|---|---|
| `results-what-survived.md` | **start here** — what was run and what happened |
| `tense-as-a-property-of-a-map.md` | the model, stated so it can fail |
| `testing-reconstruction.md` | protocol against the existing OGM literature. §3 currently withdrawn |
| `order_pb.py` | the result that holds |
| `ogm2.py` | working instrument, P2 null |
| `ogm.py` | broken instrument, kept deliberately |
| `reconstruction.py` / `reconstruction2.py` | v1 and v2 of the model |
| `wick.py` | imaginary time |
| `mirror.py` | Klein four-group, the C = 3 bifurcation |
| `duo_order.py` | ORDER in the two-agent setting |

Builds on `0x-auth/self-referential-seed`.

## Open

1. **The hunch.** Valence may not be a coordinate but a property of Λ itself. P2 failed because valence was bolted on as `x[0]`. Retry it as the multiplier along the reconstruction path.
2. Improve the ordering rule. P-B's baseline violation rate is 0.61 — a noisy floor.
3. P1 (global damping) is still assumed, not derived.
