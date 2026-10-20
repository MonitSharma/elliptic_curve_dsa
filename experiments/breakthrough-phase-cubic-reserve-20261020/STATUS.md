# Complete raw width prototype: 1,233 qubits, not a scored improvement

All 19 focused native tests pass. The unchanged 1,234-cap control reproduces
raw stream `13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b`.
The independent 1,233 cap generates a complete raw circuit with both peak
and touched width 1,233, stream
`8447753aaf3b0f157ecc2e351225adc69dc48c4ebf9c05ace471773e91db0113`.

Builder expected Toffolis are 763,971.8 versus raw control 762,230.8. These
are construction diagnostics before postpasses, not executed benchmark
scores. The added cost is too large to establish a product improvement.
No full correctness census, final gate, nonce search or submission occurred.

The phase-only adapter removes a temporary allocated at live width 523 but
retained through a later peak. An immediate-allocation-only check missed it.
The original CRLF launcher failed before preparing a worktree; the corrected
controller and all failed logs remain in the sealed evidence.
