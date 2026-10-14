# Actual square producer identities

The [source/binary/packet receipt](producer-identity-receipt.json) binds native
observations to a new clean-base checkout and dedicated build targets. The
[observation patch](producer-observation.patch) adds no operations to the tested
full-width unbound arithmetic. Its raw operation stream is byte-identical to
the earlier full-width stream:
`c2c6987b7b97b3175cbd7947699c651c7b324f4c9412d439e7a9b4658a4ac272`.
Native replay completed exit 0. The [later complete builder failure](producer-builder-failed-receipt.json)
remains exit 101 at its inherited fixed `linear_restore` fingerprint; no full
pipeline or record is claimed.

Before any top-level loan or fold, all 18 literal-zero slope shots already
violate each square producer's intended field identity `input²+offset`.
All 14 physical-p zero slopes and 32 `P=-2A` slopes satisfy that field identity
for A, B and C. The literal-zero producer words are identical in all 18 shots:

| Producer | Actual word / field residue |
|---|---|
| A and B | `0xffffffffffffffff00000006fffffffffffffffc0000000300000003fffffffe` |
| C | `0x30000000200000000fffffffcffc000000000000300000003fffffffe` |

A and B exactly match the independent unsigned, full-assembly integer model.
C's model word is
`0x30000000200000000fffffffd000000000000000300000003fffffffe`:
its actual word is exactly **2^118 smaller**. C has field fold weight 2^128,
which exactly accounts for the remaining **-2^246 mod p** discrepancy in the
full-width square result. The extra error therefore occurs inside the odd
129-bit C producer, before external loans, folds or seed handoff.

Each observed producer word remains unchanged across loan and actual fold
boundaries. All three inverse stages clean the product and restore their
original input on every shot. The intermediate Karatsuba input mutations are
expected and are not classified as defects.

Phase is measured relative to each producer's entry, including its actual
folds and inverse. All ordinary and physical-p cases return with zero phase
change for each complete A/C/B producer-consumer pair. Literal-zero cases
change phase on 9/18 A pairs, 11/18 C pairs and 11/18 B pairs. Their XOR, rather
than the sum of these counts, contributes to the final phase. Some ordinary
and physical-p C **forward** producers temporarily change phase; those
changes cancel by the inverse and are not defects. This distinction preserves
the production deferred phase-cleanup contract.

A coherent repair hypothesis uses uniform **+2** bias at every producer,
making each product `x²+2` and every retained cross exactly `2ab`. Since
integer squares have bit 1 clear, `x²+2=x² XOR 2` and all higher zero-bit bounds
of an unbiased square remain valid. Keeping b²'s bit 1 cleared through node
assembly and restoring it before b's inverse avoids the negative-offset
unsigned wrap. The initial prototype will preserve the old leaf forward/inverse
by adding 4 after its forward and subtracting 4 before its inverse, followed
by exhaustive native leaf/node checks. Old cross-bit-2 offset assumptions need
an explicit audit. Division's zero-slope phase failures remain a separate issue.

No literal-zero normalization, nonce search, sampled control-based deletion,
full benchmark rerun or scored resource claim was used.
