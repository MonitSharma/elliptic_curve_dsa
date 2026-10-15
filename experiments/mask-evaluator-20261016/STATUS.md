# AVX512 dependency-mask evaluator — component tests pass

The agreed MRMASK01 Boolean-DAG ABI evaluates512independent input assignments at
once. Only the1024declared P.x/P.y/A.x/A.y ports and constant/XOR/AND/OR nodes are
accepted. No fresh or opaque terminal is treated as an input. Output roots are
conservative MR-dependency upper bounds; their complement is the known-bit mask.

All154939904node/lane values match an independent Python implementation across
100random DAGs and512exhaustive assignments. Invalid port, forward child, unknown
kind, auxiliary field, root and capacity controls reject. The library is pinned
by SHA256641f8c1b6578c9878244650bd05cbbbd1fd452e9199c504bc76832cf72fd81e1.

Actual source-bound mask export validation is pending. Evaluator correctness is
separate from the circuit's symbolic coefficient proof, candidate-equivalence
transfer and full simulator qualification. No nonce rejection or search is
authorized by these component tests.
