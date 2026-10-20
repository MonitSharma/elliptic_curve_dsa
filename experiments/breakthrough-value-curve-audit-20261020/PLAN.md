# Valid curve fixtures for the exact failure-filter audit

Earlier fullsource tests use arbitrary registered bit patterns. Zero knownoutput
bits on those fixtures is not evidence that valid-curve filters cannot work.
Preserve those results. Add32fixed-label validcurve batches of64 shots, generated
using the protected secp256k1 reference and same register ABI/exclusions as scorer.
Compare three concrete RNG patterns in full protected simulator; independently
verify exact IR outputs and any certifiedwrong subset versus reference P+A.
Retain20 native controls and add curve-reference/generator/order/doubling test.
Freeze tool before21 native tests, require exact locally reproduced oldstream6192.
No input from a challenge packet, nonce rejection/search, gate/census verdict,
quantumresource claim or submission. All previous gate verdicts remain final.
