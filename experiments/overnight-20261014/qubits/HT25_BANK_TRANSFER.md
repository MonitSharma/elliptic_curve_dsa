# Reversible reciprocal-bank transfer: component evidence

The separate `candidate-ht25-bankswap-v2` prototype passed 17 native tests and
17 independently selected exact measurement-phase tests (704 fixed-lane audit
instances). It has not generated a full stream or passed the official benchmark.
The frozen HT25-v9 generation source remains unchanged.

Production `midg.rs` SHA256 is
`e2a12cadd8c8d33bfdd4aea8ac426880310b5779406ac493baa36525d9aeaefc`;
the seven-file candidate patch is
`61bd0d94831feea58dee9fc1c6a9cc2db10ed32e9a65f95ed5ebfe33a9a32f43`.
The exact phase kernel remains
`72ab93a2fa1fd20bb3aad370aca9f6016ea9069013eaaa34d6b02d911d859622`.
Receipts bind source, private fixture copies, native/proof logs and selected tests.

The operator exchanges Q120..127 with the eight returned reserve wires before
and after the reciprocal driver. Its selector uses actual stored ACT and
SY0..6, never the borrowed PH or SY7. SX0 enters clean, holds the temporary
selector, and is erased before reciprocal operations. Source assertions exclude
the reserve from the entire 32-bit Z head, SZ, chain, reciprocal accumulator,
flags and work registers. The HT-only 32-bit path extends to SY103; the original
HR partition retains its existing boundary.

Equivalence is conditional on the positive admitted Euclidean state. At both
HT reciprocal call sites, Z=t_j and Y=r_j before coefficient update. The
determinant identity p=r_(j-1)*t_j+r_j*t_(j-1) gives Z*Y<p, hence SZ+SY<=257.
For SY96..103, SZ<=161, so the new small-path size clip cannot remove any term
(j<26 gives SZ+j<=186). This is an admission argument, not an all-curve proof.
Active HR source bounds exclude high-bit aliases; inactive arbitrary bank words
are swapped and restored. Final HT PH normalization remains outside the entire
reciprocal/swap inverse. Full-SY dirty-bank, boundary quotient, fixed2379 payload,
crossing payload, inherited owner, map and derived-done fixtures passed forward,
inverse, full-wire restoration and phase checks.

Version 1 did not compile because its added fixture lacked one closing brace.
Its source, patch and failed log are preserved; no simulation result is attributed
to that version. Version 2 fixes that fixture and strengthens disjointness
assertions. The exact phase result covers all independent measurement outcomes
for the tested fixed lane values; it does not prove every curve input.
