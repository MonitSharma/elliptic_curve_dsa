# Zero-MR value evaluator — validated, rejection disabled

An exact value-only SIMD evaluator sets every measurement/reset random word
to zero and computes all quantum/classical values. It omits phase arithmetic.
**This evaluator cannot reject a nonce until a separate source-bound proof
establishes that the queried output values are independent of MR randomness.**
Wrong zero-MR values alone do not provide that proof.

On both the public product stream and frozen four-stage candidate, all quantum
and classical words match eight protected Simulators with a zero reader:
512 input shots per source. The 16-byte compact ABI supports the candidate's
91,691 classical bits without truncation.

| Source | Full zero-MR kernel | Static simplification | Per batch, simplified |
|---|---:|---:|---:|
| Public4b tip, Q1234/B45701 |33.99ms/8 batches|26.98ms/8|3.372ms|
| Frozen four-stage, Q1234/B91691 |36.44ms/8|28.24ms/8|3.530ms|

These are kernel timings, excluding curve input preparation, full packet
scheduling and any proof construction. They are not whole search speedups.

The static simplifier treats every input classical register bit as unknown,
other initial bits as zero, and propagates conservative known0/known1/unknown
values through classical operations at MR=0. It removes only phase-only
operations and operations with a proven false guard; a proven true explicit
guard is replaced by the unconditional sentinel while retaining the actual
pushed base condition. Classical writes and guard snapshots remain exact.
Both full and simplified paths agree on every tested quantum/classical word.

Library: `/home/hclau/ecdsa_research/zero-mr-20261016/libzero8.so`.
API:`zero8_run(CompactOp16*,nops,q,bits,stack,stack_capacity)` returns0 on
success. Rows have eight u64 words per physical wire. Unlike the full exact
simulator, this API has no phase/RNG outputs; it is restricted to the fixed
zero-MR value evaluation described above. The global-independence proof and
any eventual production integration must bind the exact stream hash.
