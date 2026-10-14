# Failed first body-boundary mapping

The source-attested native replay exited 101 before evaluating any points. Its emission-time `divide-seamed` prefix hash did not equal the same-index prefix of the finalized raw circuit. The first coordinate-subtraction boundary matched.

Source audit identifies `Builder.y33_clears()` before `finalize_records()` as the retroactive operation mutation. It replaces a run's first write with HMR plus a phase twin, rewrites later writes as phase twins and removes the eventual reset. A pending run shifts prefix operation indices and makes its physical target zero before its original logical release. Whole-body length is unchanged. `finalize_records()` changes no operations, as its before/after hashes independently show.

This is a failed verification assumption, not an arithmetic counterexample. No old arithmetic flag or phase is interpreted. V2 preserves the failed source/binary/log and adds both pre-cleanup and final hash domains, exact copied-source whole-vector transformation equality, exact event boundary remapping and logical pending-target reconstruction.

No qualified score. The protected circuit, simulator, scorer and reference remain unchanged.
