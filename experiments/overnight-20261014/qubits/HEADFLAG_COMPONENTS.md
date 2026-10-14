# Returned reciprocal flag aggregation

Status: native components and independent all-MR component proof pass. A
full generation and bounded metadata scan also pass. A full passing benchmark
remains a separate requirement. The running N275-v2
official evaluation uses its earlier frozen source and stream.

`candidate-headflag-v1.patch` has SHA256
`1792f88c69567b403aaf84e1bd9122f179d06c4e6db29de0c17440bef226b243`.
Its six changed files remain inside `src/point_add/`; source hashes are in
`candidate-headflag-v1-manifest.json`. Geometry, nonce34/control5, guarded
small-SZ branch, harness and toolchain are inherited unchanged from N275-v2.

The unguarded reciprocal window previously emitted a controlled increment
for each disjoint positive SY cube. It now computes their XOR into returned
SX0, increments once under act/r0/SX0, and erases the predicate. XOR equals
OR because the low-seven-bit cubes are disjoint. Active SY is admitted1..128;
the separate act control excludes inactive high-bit aliases, which are
covered by the full eight-bit fixture. The window does not change SY. Predicate scratch returns before the
next restoring decision and before later reads of SX0.

## Source-linked zero-flag argument

Both production calls are in `midg.rs` after the compact `S1` construction.
The source explicitly sets `p_gt=[sx[0]]`, asserts its owner, sets `f=sx[0]`,
and constructs the R32 driver by cloning this `S1`. Thus `g0=f=SX0` in both
modified calls. R includes SX1..5 and excludes SX0, selector bits and act;
the existing source disjointness assertions cover these owners. No arbitrary
alternative `S1` driver is claimed.

Assume f=0 on entry to a restoring iteration, as required by the existing
driver. Saving R's old high bit into f and rotating that high bit into r0
then applying CX(f,r0) sets r0=0 for arbitrary R. The conditional comparator
restores its incoming carry c0=r0 regardless of its target, source or out
values. In its low MAJ/UMA pair, the first two carry/source transformations
are undone around the conditional target update; higher pairs never touch
c0. In the virtual-high-one one-bit case the temporary carry complement is
applied twice. These identities do not require R<D or an active shot.

Write A=r0 and B=f immediately after the comparator. The four gates
X(r0), CX(f,r0), CX(r0,f), X(f) map f to A. Since A=0, f is zero again on
every iteration. The new predicate and its inverse therefore preserve this
induction, including inactive dirty remainder words. The odd normalized
divisor/domain assumptions still determine arithmetic correctness, but the
scratch-zero argument itself is independent of those values. The guarded
small-SZ route still computes and erases its existing size predicate before
the next iteration.

The earlier preserved `qubit-create-dirty-k32.py` also checks f=0 explicitly
after a restoring step for every arbitrary R word and odd normalized divisor
at widths2..8 (21844 cases). This is supporting finite component evidence;
the source-linked carry-restoration identity above supplies the width-independent
argument for production widths24 and32.

## Native evidence

Wrapper PID2550054 completed exit0 at2026-10-14 15:12:03 UTC, under16GiB
virtual memory, four build threads and one runtime/library thread. Dedicated
target directory prevents variant reuse. Native binary SHA256 is
`223ad08fd8efe15229b846aa81e467ed273c77a2dfa7e3944573e5ae385a49e9`;
log SHA256 is
`ba5c4b09a018cf15f8d87b872967abfe147ec3e9ca23703bfc5f4bd0c1eccbfa`.
Invocation and hash checks are in `qubit-headflag-v1-components.sh`.

All13 selected tests passed: three new flag tests; five N275 tests; two PH
owner tests; the8048 payload test; and two reserve9 tests. The flag audit
covers all256 SY words, active1..128, inactive high aliases, arbitrary dirty
passengers, both reciprocal calls and all26 decisions per call. Its52
diagnostic probe wires make the fixture744 wires. Production fixtures remain
692. Two deliberately injected faults respectively corrupt an iteration's
zero flag probe and the increment selector; both fail the expected oracle.

The inherited18 full columns cover both crossing modes, wide first column,
SY96/97/98/99/128 boundaries and the original arithmetic counterexamples.
Three payload fixtures cover3713,8048 and independent structured q22,
256 lanes each, using exact pre/post payload oracles and full inverse wire
checks. Full-column native phase checks sample measurements; they do not
prove all measurement outcomes. The V-only audit has no measurement gates
and checks its phase exactly. The coordinator owns the independent all-MR
decision-diagram proof on the frozen source.

The coordinator's corrected external proof v2 completed exit0, PID2564807,
all9 selected tests passed in72.28s (116 exact phase instances, peak917528KiB).
Its log SHA256 is
`336f916231b8d9a0f7ed4451f32830947346984e4c7b555cc693c8bb9f6731b0`.
`coordinator-qubit-decision-headflag-v2/crate/complete-source-binding.json`
binds the proof to the frozen patch above. This proves phase for every
independent measurement outcome on the fixed fixture lanes; it does not
prove the whole curve-input domain. External v1 stopped during compilation
because its renamed canonical fixture left the newly added self-fault
test's function reference unresolved. No simulation occurred in v1; both
wrapper versions are preserved by the coordinator. Candidate source was
unchanged between these proof attempts.

## Emitted-operation diagnostics

External profile PID2555030 completed exit0. `qubit-create-headflag-profile.py`
includes each frozen source under an external crate, embeds hashes of all
point-add files, and uses distinct binary names and Cargo targets. No
submission or protected evaluator is edited. `headflag-profile-receipt.json`
preserves all eight profiles per variant and log hashes.

| Window component | Baseline Ops | New Ops | Baseline CCX | New CCX |
|---|---:|---:|---:|---:|
| R24, all four SZ intervals |120391|22057|116896|19032|
| R32, SZ101..160 or101..230 |151227|23923|146536|19748|
| R32, SZ65..256 or231..256 |165205|165233|160056|160074|

Forward and inverse counts agree. The large guarded small-SZ route is
unchanged and dominates the last row. These are emitted component counts,
not executed Toffolis, point-addition totals or scored results. The profile
launcher mistakenly redirected its overall stdout to `/dev/null`; separate
per-variant logs, source/binary hashes and its absolute exit0 marker were
preserved. This bookkeeping limitation does not alter the profiled inputs
or candidate source.

## Full generation

The coordinator authorized the frozen builder after the component gates.
Wrapper2568695/native2568934 completed generation and bounded scan exit0
at15:46:15UTC. The inherited serializer test first passed462 physical Ops
with every field byte-equal to the unchanged protected writer. Generation
took20:05.99, peak1135052KiB; bounded scan took1:18.16, peak6912KiB.

The full stream has3500369588 Ops,692 referenced qubits and2390621 bits.
Its SHA256 is
`6b0046e2470cabf150fa6d2892e0b8206a683d3975b5d268cd7b80ed2cfdc902`;
compressed size4843920498 bytes. At protected sizeof(Op)=56, its Op vector
requires182.5585GiB, or198.5585GiB with the chosen16GiB margin. This remains
too large for a192GiB evaluation cap. Actual loader capacity still needs a
separate reserve receipt under an authorized allocation. No second giant
evaluation has been launched alongside the running original N275-v2 test.

The coordinator authorized preparing a fresh protected harness. Its build
PID2597932 completed exit0 at15:55:33UTC; all protected sources, Cargo and
toolchain remain byte-identical to c95b9325. Sparse checkout excludes only
fresh output paths and preserves historical files in the other checkouts.
The new protected binary SHA256 is
`8333555d82603e07c735e56db12cf8ce9c6355c92f2afa2ce7670ec3b8578a18`.
Prepared sequential queue and allocation guards wait for the original native
exit marker, check no other large ECDSA process, verify fresh available memory,
source/stream/binary hashes and actual loader capacity, then use an explicit
full-stream symlink and fresh outputs. Queue launch remains subject to the
coordinator's wrapper review. After review, the coordinator authorized the
queue, launched at16:12:28UTC as PID2612039. It is waiting for the original
native2534382 exit marker; no headflag Op vector or benchmark has started
at this receipt. The expected negative-marker guard refused allocation and
is preserved in `headflag-negative-gate-receipt.json`. No headflag evaluation
result is claimed here.

`headflag-generation-receipt.json` and `headflag-stream-metadata.json`
preserve these generated diagnostics. The builder's ordinary protected
`ops.bin` is the inherited25-byte empty placeholder; the full external stream
is `evidence/headflag-v1-ops.bin`. A future fresh protected evaluator must
resolve its input explicitly to the full stream. Neither these N/Q counts
nor static2555860466 CCX counts are a scored result.
