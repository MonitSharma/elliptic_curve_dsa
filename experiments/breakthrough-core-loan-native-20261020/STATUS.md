# Native active-core compression passes

Two focused tests plus the independent original-prefix control pass.
The 31-helper prefix is converted by an invertible affine basis change into
20 required forms and 11 temporary forms. All 11 are erased by HMR and
Clifford phase repairs, then regenerated using exactly 11 AND products.
All 16,384 source assignments, mixed guards, measurement coefficients,
allocation reuse and uninterrupted replay controls pass. The storage
interval contains 20 live helpers instead of 31.

The earlier generic reconstruction uses 32 ANDs and also passes after the
fixture correction. Initial compiler and guarded observation failures are
retained. The fixture split execution across `Simulator.apply_iter` calls,
which each create a fresh condition stack; the corrected fixture restores
the outer guard and compares against a single uninterrupted execution.
No production prefix changed in this experiment.

All 67 evidence members verify locally; exact source/test bytes are bundled.
This is a component result, not a complete point-add record or final gate.
