# Source-bound scalar Boolean wrongpoint proof experiment

FIRST preserved failure scalar pair only, no input selection by solver outcome.
Same frozen source6192/protected dependencies. Exact captured-SSA values after
one liveness/cancel round. Scalar Boolean AND/XOR/ITE DAG with structural
identities only, all random bits arbitrary, original RNG slot mapping retained.
4million node budget aborts inconclusively. Native21 controls plus2DAG truth/
cancellation controls, three fullprotected finalvalue comparisons before CNF.
Export reachable DAG as exact Tseitin CNF and require ALL output bits equal
reference P+A. SAT means inconclusive; UNSAT certifies wrong point for this one
input, not a general model and not a production rejection filter. Separate
solver encoding qualification/source/hash checks and timeout required. No
nonce screened or rejected; prior statistical gate verdict unchanged.
