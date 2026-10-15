# Per-input, per-bit conditional-mask transfer

This companion does not modify the completed cache certificate. It references
`CACHE_EQUIVALENCE_CERTIFICATE.json`, SHA256
`4857f8255c6aa85f0c6cb84720c6d5690aaca060f2758a8c517bd43fc5e2f04e`.
That source-bound audit covers all25 exact cache stages from original4b stream
`2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e`
to product25 stream
`180af069679ffa33b099b200d3337d6fc6c20a451a72508a40dea6617150dc64`.
Its trusted Boolean kernels and HMR/CZ gadget theorem remain explicit; this
companion adds no proof-assistant claim or measurement-independence premise.

Let `F_b(x,r)` be bit `b` of the original circuit's audited output projection
for a fixed ABI input `x` and arbitrary original measurement assignment `r`.
Let `G_b(x,s)` be the same original output bit in the audited candidate for
arbitrary candidate measurement assignment `s`, including every added private
cache measurement. Let `pi(s)` select the preserved original measurement
events under the audited mapping. The completed certificate establishes

`for every x and s: G_b(x,s) = F_b(x,pi(s))`.

For any fixed `x` and bit `b`, suppose a separate sound conditional-mask proof
establishes `F_b(x,r)` is constant for **every** original assignment `r`. Then

`for every s: G_b(x,s) = F_b(x,0)`.

The proof substitutes `r = pi(s)` into that per-input constant-bit premise;
its constant also equals the all-zero original measurement assignment. No
global independence theorem is required. Different bits and inputs may have
different certified masks. A sampled equality, a small dependency cone or a
heuristic mask is insufficient to establish the premise.

For a value prefilter, apply this only to original scored coordinate bits in
the audited projection. Compute the candidate's own Fiat inputs from its
final source/stream. On those inputs, compare the original zero-MR output
with the expected curve result **only where the mask is certified**. A
disagreement on any certified bit proves the candidate wrong for every
candidate MR assignment, so rejecting it is safe. Matching masked bits or an
empty mask supplies no full-pass conclusion; survivors still require the
unchanged full simulator/benchmark, including phase and dirty-qubit checks.

A new nonce additionally requires byte-identical audited pre-tail operations
and exactly48 adjacent XX identity pairs in the96-op tail, on the authorized
qubits. The frozen product25 pre-tail has14142533 operations and SHA3_256
`24027e53f377f24195d290b5d343c519156cfa3ae45f64529def428a901f8480`.
These identity pairs preserve the function for every input, so the result
applies to the new candidate's own Fiat inputs. This does not reuse an old
packet or waive the fresh-census/nonce/unchanged-benchmark requirements.

The conditional mask and zero-MR evaluator must both be independently sound
and bound to the original frozen function. This companion proves transfer
under that premise; it does not certify any particular exported mask/model.
