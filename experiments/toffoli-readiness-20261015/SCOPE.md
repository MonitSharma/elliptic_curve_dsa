# Low-Toffoli submission work

The user reaffirmed three independent objectives: minimum qubits, minimum
Toffolis, and minimum product. This chat prioritizes a lower-Toffoli submission;
the other chat owns Q692 readiness. A Toffoli record need not improve product.

Acceptance requires a complete unchanged benchmark pass, a rounded executed
Toffoli count below the refreshed public minimum, preserved source/evidence,
and a working normal build within the official runner constraints. Component
or paired savings on a failing circuit do not satisfy those requirements.

The first candidate ports the tested exact lazy-cache pass to the B3 public
low-Toffoli baseline. This changes only point-addition source, keeps arithmetic
and the identity tail fixed, and performs one final evaluation. No nonce or
packet selection. Known inherited arithmetic failures remain a qualification
risk. Any failed evaluation is preserved; it is not a submission-ready record.

All writes and jobs for this cycle belong to this directory and the matching
`/home/hclau/ecdsa_research/toffoli-readiness-20261015/` directory. Existing
track checkouts and Q692 files/jobs are left alone.
