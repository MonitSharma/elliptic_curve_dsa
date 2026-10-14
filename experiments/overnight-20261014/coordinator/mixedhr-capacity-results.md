# Structured mixed-HR capacity counterexamples

The N275 prototype's mixed-HR22 capacity has no demonstrated structural bound
over the original public23-bit domain. Independent structured fixtures expose
that gap in the ideal model, rather than relying on a random sample failing to
contain a large quotient.

Choose a coprime110-bit coefficient pair(tcur,tprev). Solve
`P=rprev*tcur+rcur*tprev` by choosing rcur in the congruence class
`P*inverse(tprev) modulo tcur`, near the fixed target quotient5,000,000.
Reverse the coefficient Euclidean recurrence to obtain a legitimate field
denominator. Every construction asserts the reconstructed first remainder is
exactly P and the denominator lies between zero and P. The coefficient seed,
construction and four exact fixtures are preserved in
`mixedhr23-structured-model.json` and `scripts/construct-mixedhr-capacity.py`.
No benchmark packet or nonce is modified.

The first denominator is
`2e790bb7768274fe45c4126ceeb2caaf7e77837f48e87b4a0b3c21ce3b842205`.
Its ideal delayed-HR quotient is5,000,211 at column65/Euclidean step66,
with110-bitY and124-bitZ. That quotient fits public23bits and exceeds22bits.
The public23/head24 model has no event; N275's22-bit search loses the high bit
and produces the wrong ideal accumulator. These are capacity regressions.

The model alone does not check source schedule admission, physical carries or
quantum phase. Subsequent HT25-v9 native source-envelope checks admit the
physical delayed-HR fixture and its full delayed column/payload checks pass;
see `../qubits/ht25-v9-component-receipt.json` and
`../qubits/HT25_DOMAIN_AND_OWNERS.md`. This establishes the need to retain the
23-bit capacity on an admitted source state. It does not establish a complete
public point-addition counterexample or every-input candidate correctness.
The storage repair restores mixedHR23 rather than treating absence of a large
quotient from earlier finite packets as a proof.
