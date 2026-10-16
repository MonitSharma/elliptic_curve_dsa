# Product candidate: 761,121 T × 1,234 qubits = 939,223,314

Queue mode; not yet submitted. This targets the qubit × Toffoli product. It is
124,634 below the public record 939,347,948 (761,222 × 1,234, jackylee0424,
`85d067da`, source `4b2ec52f`; refreshed 17 Oct 2026, 07:30 Singapore).

**Unchanged benchmark.** All 9,024 shots pass; classical, phase and ancilla
failures are all zero. Total executed Toffolis 6,868,354,504; mean
761,120.844858156; rounded 761,121; peak 1,234 qubits.

**Circuit.** jackylee0424's `4b2ec52f` with one change: a 67-stage exact cache
that reuses repeated AND computations in idle wires, so peak width is unchanged.
Only `src/point_add` differs (three paths: the module call, a loader, a frozen
data table). The cache was certified equivalent to the original for every
input (universal certificate `303a75ec…`: 245,820 leases, 540,759 uses). The
native source reproduces the frozen stream byte for byte; the pre-tail of the
final stream is byte-identical to it. All protected files match the base.
Inherited approximate arithmetic of the parent is unchanged and disclosed.

**Failure rate (fresh inputs, declared before running).** Label
`product67-frozen-20261016`, 32,768 batches (2,097,152 shots) per source, paired
on identical inputs with the record's exact stream (`2a522394…`).

| | Record `4b2ec52f` | This candidate |
|---|---:|---:|
| Value-failing shots | 3,622 | 3,622 |
| Failing batches | 4,168 | 4,162 |
| Failed batches per 9,024-shot packet | 17.93 | 17.91 |
| Dirty-ancilla shots | 0 | 0 |

Discordant batches: 155 newly failing, 161 newly passing; one-sided exact
McNemar p = 0.653. The candidate also meets the older "no worse than parent"
rule. A 512-batch recheck of the final stream on the same label reproduces the
gate rows exactly. Paired saving: 102.14 ± 0.44 executed Toffolis per shot.

**Nonce.** 129,023,534, ascending from 1, lowest pass. 129,245,184 nonces
screened in the operational search (221,650 above the selected one are
parallel in-flight work), plus 4,096 control nonces (1–4,096) screened
separately. The prefilter only rejected nonces with a certified wrong output
value; every lower nonce fails, and a complete JSONL audit of all rows confirms
it. No nonce was chosen by its Toffoli count; no circuit content, table or cut
was tuned to a test packet.

**Hashes.** Final stream SHA-256
`f2279f98d631113bf045f7d2c8f17cbc514d77a135e14234b983d4534057b78d`; patch
`cf417469…`; source archive `41f0b29d…`; score file `e332a939…`.

Credit: the circuit is jackylee0424's `4b2ec52f` lineage; this entry adds only
the exact cache.
