# Per-input conditional-mask transfer for frozen95

Certificate SHA256: `f3af2e4d3275f9b39fa34ad61d8a000f166935eb4f7236ac28a5cd2032dc27ad`.
Original stream: `2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e`.
Candidate stream: `ba87b9ceb0691ccfe8c509539cfc38e774ee02134363c19e3541c6e942723e84`.

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
The associated JSON binds the exact95 prefix and lists all separate premises.
No source, nonce or certificate is modified by this companion.
