# Exact sparse linear witnesses over current qubit values

Prepared source method, not a gate/nonce/benchmark result. Generalize exact
one/two-wire products to a bounded sparse linear span of current ANF values.
Every row has explicit physical-wire provenance and a constant. On a wire
write, remove ALL rows depending on it before inserting its new value.
Never infer a zero from a missing pivot, size limit or dropped row. Limits:
1024 terms/32 wires per row/query, fixed before whole-source observation.
No allocated abstract atoms/cuts in row reductions or queries. A successful
query emits CNOTs and optional X under each original classical condition;
exclude target and original control wires. Original abstract execution stays
unchanged, so future Boolean/phase operations retain the same values.
No new width, reset or measurement. Existing22 and8 new independent tests;
complete disabled-mode report/hash control and512 protected transcript shots
on changed source. Universal source-bound proofs/native reproduction/own gate
remain required for any positive result. One local CPU/12GiB, serial jobs.
