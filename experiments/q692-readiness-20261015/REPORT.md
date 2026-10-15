# Q692 submission preparation

**Status: NOT SUBMISSION-READY. The cost-reduced v6 failed the normal 9,024-shot benchmark. The v9 repair fixes its three original failed inputs, but all three new independently constructed valid curve cases fail. The original overnight source also has demonstrated curve-input counterexamples. No submission has been made.**

The selected circuit still uses **692 logical qubits**. Its source-bound profile
has **67.64% fewer emitted Toffolis** and **42.82% fewer physical operations**
than the original passing overnight circuit. These are generation counts;
the reduced circuit has no qualified score because its full benchmark failed.

| Source | Physical operations | Emitted Toffolis | Qualification |
|---|---:|---:|---|
| Original frozen Q692 | 2,472,354,640 | 1,483,109,996 | Earlier complete local pass: mean T1,481,382,858 |
| v1 | 2,453,389,792 | 1,452,070,716 | Components pass; too large for normal runner build |
| v2 | 2,348,572,768 | 1,341,141,708 | Components pass; too large for normal runner build |
| v3 | 2,351,902,000 | 1,279,861,628 | Components pass; complete stream generated; no full benchmark |
| v4 | 2,351,902,000 | 1,279,861,628 | Construction cache gave no useful speedup; excluded |
| v5 | 2,270,886,400 | 1,263,685,276 | Components pass; normal Vec capacity would exceed runner limit |
| **v6 tested** | **1,413,812,844** | **479,915,092** | **Normal build succeeds; complete benchmark FAILS** |
| v7 component prototype | 1,401,041,164 | 463,955,908 | Components and phase checks pass; no new benchmark packet will be tried while v6 failures remain unresolved |

The cost changes reuse existing temporary storage. They combine increment
conditions, restore borrowed controls with exact arithmetic, and compute a
size condition once for a rotation instead of repeating it for each swap.
They preserve the original precision, size checks, quotient capacities and
nonce. [Equivalence arguments and independent checks](PROOFS.md).

The v6 source passes 17 native component tests and 16 independent phase
tests, including 700 fixed-input audit calls covering all measurement outcomes.
The increment has 582,930 exhaustive small-word checks. The division rewrite
and rotation rewrite each have 524,288 paired full-state checks, including
dirty storage and inverse restoration.

The full source is packaged on public base
`441d9ef9f5fe05107f4390e9f623caffdf77349d`. Its patch changes only 68 paths
inside `src/point_add/`. Replaying that patch in a pristine checkout reproduced
all 190 point-addition files exactly and preserved all 17 protected files.
Draft export failures, including omitted new files and binary-file deletions,
were caught and preserved before the successful clean replay.

The **normal build and independent streaming build produce identical bytes**:
SHA-256 `c45935170e604c5fe4b191a856a8017e1123e62223bb05ca8585046dd797c8d0`.
The unchanged trusted loader reports Q692 and 1,413,812,844 operations.
Its operation vector requires **73.74 GiB**. The normal test ran under a hard
128 GB virtual-memory limit with the sole-large-evaluator lock, peaked at
**74.56 GiB**, and took **47:58.34** on the older local Xeon server.
The original passing source and all other projects remain untouched.

**Remaining risks:** the existing expected-negative test demonstrates a
component failure above the 25-bit quotient capacity; general curve-input
correctness is still unqualified. The official workflow has a 45-minute limit;
actual execution on its Blacksmith runner has not been verified. Its advertised
memory is [128 GB](https://docs.blacksmith.sh/blacksmith-runners/overview).
A local benchmark pass would not erase these limitations. Do not describe this
as a universally correct or guaranteed CI-passing circuit.

Experiment evidence: [progress receipt](progress-receipt.json). The complete
source patch and failed terminal benchmark receipt are preserved. Diagnosis
will reconstruct the same failed packet and test those fixed inputs; it will
not change the nonce or seek another validation packet that happens to pass.

## Fixed-input diagnosis and repair status

The protected hash recipe reconstructed the failed v6 packet exactly, including
shot 2726's expected coordinates. A memory-bounded adapter then replayed shots
2726, 2913 and 3532 in 64 lanes through both complete serialized circuits using
the unchanged protected simulator and a fixed independent measurement seed.
All 64 lanes failed on each circuit. The v6 replay reproduced its benchmark's
first wrong output exactly. The two sources produce different wrong values;
this does not establish equivalence on inputs where arithmetic assumptions fail.
The original benchmark pass remains historical evidence, but that original
source now has demonstrated curve-input counterexamples.

The source-policy model flags insufficient reciprocal precision on 2913 and
3532. Input 2726 contains an intermediate remainder with 22 trailing zeros,
above the original limit of 21. A conservative census of all Euclidean
remainders and coefficients in the same packet also finds a 23-zero value
in shot 1213's second division. These model findings guide diagnosis; they
are not circuit-correctness proofs or new benchmark results.

An isolated repair prototype retains Q692 by borrowing a size bit and the
active flag only while a selected reciprocal computation needs them. It uses
TC27, a 25-bit head for large operands, and EMAX23. The storage primitive
passes 131,072 independently calculated cases and 4,096 audits covering all
measurement outcomes. The successor v9 passes the 17 existing native checks
and 16 independent phase checks. v8's failed old-configuration/SZ9 checks,
their logs, and its successor source are all preserved.

The exact failing-column/payload regression now passes all four columns,
1,024 cases, their entire state and inverse, and every measurement outcome.
The earlier wrapper wrongly initialized later HT columns with the first-HT
ordering and payload representation. Those failed wrappers and logs are
preserved; they are not candidate results. The final wrapper also uses the
production scratch constants. A separate map-only proof passes both orientations
of the 22-zero counterexample with an integer oracle and all-measurement audit.

The complete v9 counting diagnostic reports Q692, 1,619,702,564 physical
operations and 544,889,652 emitted Toffolis. These counts are unscored. The
profile took 12:22.09 and peaked at 953 MiB. Its complete patch on the promoted
base applies cleanly and matches all 190 source files and 17 protected files;
patch SHA-256 `0500ac6838b56a7eb29388b0ab83bc95488b2758e263cb57ca8c873b84288515`.

Complete low-memory circuit generation has finished at Q692 and matches the
counting diagnostic. It took 14:27.30 and peaked at 958 MiB; stream SHA-256
`b87f979142da9dd550139511eff15e55ed17d5967b05fa9fc43a80f787e3ea51`.
The validation sequence checked its stream hash and passed complete replay of
the same three failed points in all 64 lanes, with zero value, phase and
ancilla failures. [Compact replay evidence](fixed-replay-summary.json).
The subsequent independent curve checks failed, so the failure gate stopped
the sequence before the old full 9,024-input packet test. These diagnostics
retain the protected simulator, cap memory at 16 GiB and use one simulation
thread. They generate no new official validation packet. No v9 official
benchmark or submission qualifies. Quotient capacity and reciprocal precision
remain active correctness blockers.

A fixed independent audit of 50,000 arithmetic inputs found three further
policy failures: 26-bit HR quotients of 34,582,186 and 38,938,778, plus one HT
reciprocal precision failure with quotient 483,292 inside the capacity. No schedule-envelope or
conservative EMAX23 violation was found in that audit. Every flagged input
is retained in [the independent census](evidence/independent-policy-v9.json).
All three flagged differences were converted to valid secp256k1 point pairs.
Their coordinates satisfy the curve equation, their x coordinates differ, and
the expected point sums independently match the protected curve reference.
Complete v9 replay failed all three cases in all 64 lanes: 64 value failures,
phase word `179ed5df4b4dc51c`, and 23 ancilla wires containing garbage.
[Independent valid-curve inputs](evidence/independent-curve-packet-v9.json),
[complete replay receipt](evidence/independent-curves-v9-result.json).

The sequence exited with status 1. No large old-packet evaluator, new official
benchmark, nonce change, packet search, organizer contact or submission was
attempted. The frozen original source and unrelated work are preserved.
**Do not submit these candidates.** The next safe arithmetic work must repair
the quotient overflow and reciprocal decision errors on the preserved cases
before another source is considered for benchmark qualification.
