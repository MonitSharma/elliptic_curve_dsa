# All43 global sites are unreachable: zero executed benefit

Every one of the43 non-Keep sites has an exact universally false **captured
scope predicate**. All have no direct per-operation condition; scope depths
range1..15. The already-computed condition form is constantfalse with no atoms
at every boundary. Thus no gate in this family executes, and the rigorous
executed-T benefit is exactly0..0. No executing q0/q1, complementary-control,
equal-control or phase/repetition cancellation opportunity is admitted.

The raw43-gate count would have a syntactic depth proxy1141/128=8.9140625 if
these known-false scopes were incorrectly treated as independent fair guards.
The correctly filtered depth proxy is0. Neither the raw count nor that raw
proxy is a Toffoli saving. `DEPTH-ACCOUNTING.json` preserves all depth counts.

This classification observes the original c262bba1 immutable prefix engine
after its ordinary global CCX decision, without changing symbolic state or
allocation. Removing its single observation hook reproduces the original
kernel exactly. All43 indexed records include original physical wire/guard
fields and complete condition/control forms. The count independently agrees
with773580-773537 from the prior unchanged complete-source scan. Prior Gaussian
cofactor zero-novel artifacts remain untouched. `PROOF-AND-ADMISSION.md`
explains prefix soundness, phase/MR preservation, reachability limits and what
a genuine later source-pass admission would require.

Native compilation and complete scan exit0; runtime24.96s,1288368KiB peak RSS,
one core under16GiB. PID436778 is terminal. No candidate, sampling, reranking,
nonce work or production edit occurred. The final-pass ordering lead stops
here: deleting unreachable gates would only alter emitted bytes/hash and
cannot improve executedT.
