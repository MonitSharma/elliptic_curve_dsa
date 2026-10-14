# V2 review addendum

V2 `midg.rs` SHA256 is
`e2a12cadd8c8d33bfdd4aea8ac426880310b5779406ac493baa36525d9aeaefc`;
its patch hash is
`61bd0d94831feea58dee9fc1c6a9cc2db10ed32e9a65f95ed5ebfe33a9a32f43`.
The exact production-source diff against reviewed V1 adds an assertion that
reserve is absent from the full32-bit head and SZ, and documents the clean
SX0 entry contract. It changes no emitted production gate operation. Thus
the V1 source-level operator/owner reasoning transfers to V2 while retaining
the old review and hashes.

The qubit researcher confirms the positive coefficient/remainder invariant
at both HT V calls: `Z=t_j`, `Y=r_j`, and
`p=rprev*t_j+r_j*tprev`, with the relevant positive Euclid terms. Consequently
`Z*Y<p`, and the unchanged current coefficient/remainder fields at both calls
give `SZ+SY<=257`. On selected SY96..103, SZ<=161 and j<=25, so the added
small-driver SZ clipping is inactive. This closes the explicit admission
question raised in V1 review; it does not extend equality to arbitrary active
SZ255/SY96 test states outside that arithmetic contract.

The source owner reports V2 native completion with groups7,5,2,1,2 and is
preparing all-measurement proof. This reviewer did not run those workloads.
The review remains source/operator/owner plus exact transfer algebra; native
and all-measurement evidence must be bound separately by that experiment's
receipts. No full-generation, official benchmark, width, executed-Toffoli or
product record is asserted. Frozen HT25-v9 and its full generation are untouched.
