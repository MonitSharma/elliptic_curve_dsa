# Operand-borrowed ripple carries

## Final outcome: negative, 19 October 2026, 14:31 Singapore

Twelve exact width configurations kept the conservative peak at Q1234; none
improves the full product budget. A separate exact commuting-inverse pass
found zero cancellable Toffolis on the public parent. All jobs exited 0.
There is no active successor, submission candidate, declared census gate,
nonce search or upload from this experiment. No new resource record is claimed.

Thirty-one distinct tool tests passed: eleven carry tests, four conservative
recoloring tests, six exact recomputation tests, three lifetime-profiler tests
and seven commuting-inverse tests. The recolorer was tested but not used to
produce a submission because every complete lifetime bound stayed Q1234.
These are component/tool tests, not a passing official point-add benchmark.

The first bottleneck moved from the restored-input carry chain at op1444984
to a small AND network, then to compact ripple carries, then to fast-cleanup
carries with an explicit reset. Covering those forms still leaves a shared-
mask carry chain at op2257874 in `last-carry-1232.ops.bin`. Its mask wire660
is repeatedly transformed by a long parity of other live wires between
carry cells; the operand-borrowing proof correctly rejects these accesses.
The next arithmetic experiment should redesign this shared-mask carry
construction and select changes at actual simultaneous peaks. Extending
blind high-wire thresholds adds too many Toffolis before reducing Q.

Exact per-site rewrite certificates, source versions, tool tests, conservative
profiles, launcher PID/exit records and stream hashes are archived in
`evidence.tar.gz`, verified against `EVIDENCE-MANIFEST.json` and
`EVIDENCE.sha256`. Large diagnostic streams remain in the matching server
directory. `FINAL-CARRY-RESULT.json` gives complete predicted cost deltas;
`commute-parent.json` records the separate zero-saving screen. Generated
counts and budgeted products are diagnostic, never scored results.

Started at 14:14 Singapore, following the completed negative cache-removal screen.

Fresh public product parent: 9dc3798c-93e0-4da4-a6a9-37586737c4af,
revision 0c3a0751ab66bd9144358d67563bcb79201cf636, Q1234/T761096,
product 939192464. Public API snapshot and hashes are archived here.

Hypothesis: replace selected clean-ancilla ripple-carry cells with reversible
MAJ/UMA cells borrowing the source operand. The source and incoming carry are
restored; the target receives the identical sum. One extra unconditional
Toffoli per replaced cell may lower peak width. No approximation is introduced.

The first peak is operation 1444984. Its highest carries are long ripple
chains, unlike the previously removed repeated-AND caches. Screen thresholds
1233, 1232, 1230, 1220 and 1200; measure the complete conservative width and
the full extra-Toffoli budget. Stop unprofitable branches. Only an improved
whole product justifies native source binding and subsequent qualification.

Proof restrictions: exact 6-op constructor and 9-op measurement cleanup;
initial carry is provably zero; no interior access to the borrowed operand,
target operand or incoming carry; carry is read-only in the interior;
unconditional boundaries; removed measurement bit has no further use before
an unconditional overwrite; scopes must be nested or disjoint. Exhaustive
truth/measurement-phase tests and rejection tests precede the real stream.

Protected challenge code and all prior experiments remain unchanged. Research
tools live outside submission trees. No statistical gate, nonce search or
upload is declared by this diagnostic experiment.

## First screen complete; complementary peak identified, 14:20

All ten v1 tests passed (seven carry tests and three profiler tests). The
five thresholds converted 7, 55, 170, 670 and 1,666 carry cells respectively;
each retained conservative peak Q1234. These are negative standalone screens.
Launcher exit was 0; source hashes, stream hashes and per-site certificates
are preserved. The archived v1 source is `borrow-v1.rs`.

At threshold 1232, the original ripple peak disappears and the first peak
moves to operation 1449165: a small multi-read AND network. This supplies a
specific new hypothesis: combine operand borrowing with selective, exact
cache recomputation at high wire IDs. The earlier standalone cache-removal
negative result remains valid. Neither method alone removes both bottlenecks.

The combined screen launched detached as PID 546667 at 14:20 Singapore, with
64 GiB address-space limit, four build threads and one scanner/library thread.
It checks thresholds 1232, 1230 and 1220, limiting recomputation to donors at
or above the threshold. Two further tests check nested carry composition and
reject a mutated carry. No statistical gate, nonce search or upload is enabled.
