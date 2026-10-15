# Carry precision research, 16 October 2026

The local terminal precision theorem passes; complete source-family
qualification is in progress. No resource record, failure reduction, cache
composition, nonce search, or submission is claimed.

The clean-donor version costs one additional Toffoli, one measurement and
zero qubits. Its arbitrary-input, guard, MR and phase proof passes. The
dirty-donor version costs four additional Toffolis, zero measurements and
zero qubits, restores arbitrary borrowed state, and also passes. Both
implement one additional bit of truncated precision and explicitly frame
all higher bits.

The original public source is
`4b2ec52fc55da796aa8f5ef851290297e8706424`. The gate-inert source observer
reproduces raw stream SHA256
`ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69`
and complete native stream SHA256
`2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e`.

The source inventory has 263 Y15 folds and 252 byte-identical complete
terminal interfaces. The late forward family has 37 source sites, with
31 unchanged terminal interfaces and six inherited-overlap negatives.
Neither conservative ternary propagation nor the stronger immutable-atom
support checker proves any qubit zero at the 31 late forward or 124 matched
reverse terminal entries. This is an unresolved donor proof, not evidence
that zero wires cannot exist. The dirty fallback would cost 124 Toffolis
for the late forward 31; no Y15 candidate or census was launched.

The square observer inventories eight width128 windows, four width130
windows and four width33 windows. The complete four-window width130 family
survives all inherited passes byte-identical, and every next bit is excluded
from the entire old window. The clean donor is still unproved there. The
dirty version is a complete 16-Toffoli, zero-qubit, zero-MR precision family.
Its source, full-window contract and fixed 32768-batch paired gate are
frozen in `SQUARE4-PREDECLARATION.json` before candidate generation. Native
guard tests pass 7 positive/negative cases. Native reproduction passes at
Q1234/B45701/MR906156, adding exactly 16 CCX gates and no other operations.
The complete candidate stream SHA256 is
`f654628ae24afc839c6febbc282cb04b6861f52ea74d6ecc5853f58ef3228b8f`.
The sole fixed 32768-batch gate is terminal and passes. Each source used
2097152 fresh shots. Failed batches fell from 4175 to 4173; value failures
fell from 3595 to 3593. Exactly two shots were repaired, with zero value,
phase or dirty regressions. Phase failures stayed at 2619 and dirty failures
at zero. Expected failed batches per 9024-shot packet fell from
17.964935302734375 to 17.956329345703125. Every batch costs exactly 16 extra
Toffolis. This is a small failure improvement with no resource record claim;
no cache composition, nonce search or submission was performed.

Uncapped canonical ANF proves the local contracts. Independent integer
oracles check 174752 signed-tail cases, 20480 wide cases and 174752
square add/subtract cases. The unchanged protected simulator passes
1572864 Y15 and 1048576 direct square cases, comparing every quantum and
classical bit, phase, dirty donor and measurement draw count. Omitted
cleanup or cubic controls are detected by the negative checks.

Preserved diagnostic setup failures: a dependency-cache path missing on
the server, a local/server evidence filename mismatch, the separately
generated finite seed lacking body payload context, reversed CCX control
field expectation, and an overstrict assumption that every frozen nonce-tail
X targeted q0. Each was corrected in research tooling, with prior logs
retained. No candidate arithmetic, family or input sample was adjusted.
