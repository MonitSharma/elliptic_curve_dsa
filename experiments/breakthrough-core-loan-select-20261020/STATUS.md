# Selected helper loans pass full-fold controls; raw circuit still noncompetitive

One complete-fold test plus 19 retained controls pass. Only enough helpers
are borrowed to leave ten carries for the ladder at the independent width
cap; skipped helpers stay live. Every selected erasure and reconstruction
uses the independently verified certificate and preserves its operand order.
The same exhaustive full-fold inputs, guards, cleanup and RNG controls pass.

The complete raw circuit has peak/touched width 1,233 and stream
`5bbda3874734205169e0542917822c78e573772eb5f77ac3e1aaf0460e8f148e`.
Raw builder expected Toffolis are 763,932.2: 79.6 below borrowing all eleven,
and 39.6 below the preceding reserve prototype. Control remains byte-exact
`13f6ffc3`. These are construction diagnostics before postpasses; there is
no executed benchmark score or established product improvement.
No final correctness gate, nonce search or submission occurred.
