# Bank-swap v2: complete local 692-qubit benchmark pass

The last candidate from the overnight cycle completed at **06:12 Singapore time
on 15 October 2026**, during the follow-up. Its source was already frozen; this
is newly collected terminal evidence, not a circuit invented during the follow-up.

| Metric | Verified local result |
|---|---:|
| Peak logical qubits | **692** |
| Rounded mean executed Toffolis | **1,481,382,858** |
| Product | **1,025,116,937,736** |
| Benchmark shots | **9,024** |
| Value / phase-batch / ancilla-batch failures | **0 / 0 / 0** |

The refreshed public minimum remains 693 qubits, so this circuit uses **one fewer
logical qubit**. It does not improve the Toffoli or product records. It has not
been submitted or officially scored by the public service. Public comparison:
[dated snapshot](../../../docs/data/latest-leaderboard.json).

The unchanged protected evaluator processed the complete frozen stream and
returned exit 0. The rounded Toffoli value agrees with the logged total
13,367,998,912,206 divided by 9,024. Its score file equals Q multiplied by rounded
mean T. Runtime was 1:56:33; maximum RSS was 135,226,668 KiB, about 129 GiB.

A read-only terminal review rehashed the 4.67 GB compressed stream, evaluator
binary, candidate patch, changed source files, protected harness files, log,
launch attestation and copied metric artifacts. It also rechecked the 17 native
component tests, 17 exact-phase tests covering 704 fixed-input all-measurement
instances, and the 462-operation serializer equivalence fixture.
[Reviewed receipt](reviewed-receipt.json).

- Base revision: `c95b9325913abacca9c86bdebad10a20633cd04e`.
- [Exact point-addition-only patch](candidate-ht25-bankswap-v2.patch), SHA256
  `61bd0d94831feea58dee9fc1c6a9cc2db10ed32e9a65f95ed5ebfe33a9a32f43`.
- Full circuit stream SHA256:
  `03cb7a3f0cc5bbb1c4d07a3cfed809e3623137425ebd7c725f158737f4a77739`.
- [Unmodified evaluator metrics](ht25-bankswap-v2-official-score.json).
- [Original terminal collector receipt](ht25-bankswap-v2-official-terminal-receipt.json).

## Scope and remaining qualification

This is a complete **local circuit-stream evaluation**. Generation used the
frozen source's streaming mode to avoid constructing the enormous operation
vector; the resulting exact stream was supplied to a pristine protected
evaluator. A separate admission check rejects the generator's empty placeholder
and binds the actual 2,472,354,640-operation stream. Ordinary submission build
packaging has not been qualified. No protected file, hash-selected packet or
identity-tail nonce was altered to obtain this result.

The finite benchmark pass is not an all-input correctness proof. The preserved
quotient-capacity and reciprocal-precision limitations still apply; see
[domain and ownership evidence](../../overnight-20261014/qubits/HT25_DOMAIN_AND_OWNERS.md)
and [bank-transfer review](../../overnight-20261014/toffoli/bankswap-independent-review-v2.md).
Those limitations should accompany any presentation of the result.

Preserve this exact circuit before attempting gate-cost reductions. The next
width-track tasks are qualifying normal submission generation and resolving the
remaining arithmetic domains. The server source and stream paths are in the
reviewed receipt. No job remains running for this evaluation.
