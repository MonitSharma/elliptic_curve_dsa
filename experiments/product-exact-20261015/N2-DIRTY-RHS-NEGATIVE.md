# Complete N2 dirty-loan RHS feasibility: bounded negative

Both source-defined loan calls and all16 candidate dirty bits were queried on
the unchanged original4b stream SHA256
`2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e`.
The family binding SHA256 is
`d9549e40e9e87d108fb5fd78e007b1b76f03a50bd5a62f780a4a748d08ab96d5`.
Queries occur AFTER the complete eight-CX out operation, at4051851 and7480333.
This covers both rails, bits1..4, in both divide and multiply. No14-case
selection, simulator inputs, failure sample, candidate or rewrite was used.

The private immutable engine is copied exactly from the attribution study:
`donor-support-original.rs`, SHA256
`c262bba163fe91a6f2bd72e21fd387de84b426838b1bba113f017b18ed9cfa71`.
It uses512-atom affine expressions over immutable nonlinear function atoms,
200,000 remembered product definitions, and conservative fresh symbols on
overflow. Equalities it derives are exact; inability to express a function is
not a proof that no mathematical relation exists. This is the fast opaque
product engine, without the richer retained distributive ANF expansion.

The first fixed query tests dirty RHS equality/complement with one of the650
qubits untouched throughout the FULL out-before through in-after interval,
indexed XORs of two such qubits, their complete affine span, and their span
with all CURRENT classical values. It then inspects existing product-node
inverse definitions whose IDs actually occur in the dirty expressions; no
Cartesian quantum-pair enumeration occurs. Factor forms must map to physical
stable controls. Candidate bounds are4096 per site and8 representatives per
equal factor form; neither bound was reached.

Four highest dirty bits are already exactly zero in this source prefix:
divide q211/q553 and multiply q211/q612. The12 other dirty bits have no
one-qubit/complement, two-qubit XOR, stable-quantum affine, or stable-quantum
plus-current-classical affine witness in this representation. There are636
relevant existing product nodes in divide and670 in multiply, but none has
both factors matching physical stable quantum controls. The run takes17.40s
with1.13GiB peak RSS; both exact-XOR/Gaussian tests pass.

The second fixed query is stronger: express each factor itself through the
classical-first Gaussian span of all current classical values and the650
untouched quantum controls. It permits affine quantum factors, mixed q/C
factors and pure classical factors. Such a positive would still need safe
classical snapshots, reversible Clifford host conjugations and a complete
repair theorem; it would not authorize a circuit.

Divide has525 relevant nodes with neither factor expressible and111 with just
one; multiply has530 with neither and140 with just one. **No node has both
factors expressible**, so there are no product generators to combine with the
affine span. The12 nonconstant dirty targets remain unresolved. This second
run takes17.14s with1.13GiB peak RSS and both tests pass. It uses no pair search
or simulated data. Current classical values cannot be reused at return without
proving stability or preserving explicit fresh classical snapshots.

A separate independent literal decoder checks all16 new return destinations.
It counts both Swap endpoints and every possible conditional value write.
Only divide q1233 (last depth-zero unconditional HMR4225380) and multiply q862
(last depth-zero unconditional R7605905) meet the strict last-write zero rule.
The other14 last writes are depth-one resets: divide4225544..4225550 and
multiply7605882..7605888. Their values are UNKNOWN under this structural rule,
not proved nonzero. Their conditional branch invariant would need a stronger
proof on any proposed repaired source. This audit proves no phase property.

The route stops here for lack of a credible cheap expression from the bounded
inverse forms. No generator, source change, larger-cap retry, pair explosion,
failure census or nonce search follows. Read-only/value-stable qubit supersets,
richer retained ANF identities, and general higher-degree factorization were
not tested and are not ruled out. Existing production search is unchanged.

Reproduction sources and complete results are preserved in
`loan-normal-forms-tool`, `loan-normal-forms-20261016`,
`loan-affine-factors-tool`, and `loan-affine-factors-20261016`, plus the
preparation/launch scripts and raw templates. `STRUCTURAL_RETURN_ZERO_AUDIT.json`
retains every last-write index and condition/depth with source hashes.
