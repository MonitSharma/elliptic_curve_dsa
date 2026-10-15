# Per-input conditional-mask transfer for frozen67

Certificate SHA256: `303a75ec86a4da8c3a4008646e1b8257768fa40e198f0b7172eeafd19408c7c6`.
Original stream: `2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e`.
Candidate stream: `268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d`.

For a fixed ABI input x and scored output bit b, the audited chain establishes
G_b(x,s) = F_b(x,pi(s)) for every candidate measurement vector s. If a separate
sound certificate proves that F_b(x,r) is constant for every original
measurement vector r for this particular x and b, then G_b(x,s) = F_b(x,0)
for every s. This needs no global measurement-independence theorem.

A certified masked-bit mismatch between the exact original zero-measurement
value and the reference curve result therefore safely rejects this input.
The mask and evaluator need their own exact source-bound proofs. Matching
values, unproved bits and empty masks do not establish a full pass. Survivors
still require exact phase, scratch and complete output checks, and the final
unchanged official benchmark.

Every input must come from the final candidate's own Fiat preparation. A
nonce change additionally requires byte-identical audited pre-tail operations
and48 adjacent XX identity pairs, using that final source's inputs. This does
not transfer across a precision repair changing the original value function.
The associated JSON binds the exact67 prefix and lists all separate premises.
No source, nonce or certificate is modified by this companion.
