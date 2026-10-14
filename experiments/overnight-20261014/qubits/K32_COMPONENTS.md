# Wider reciprocal and size-donor component checkpoint

All results here are isolated component evidence. QB23 and the nonce are
unchanged. No complete point-addition record or Q692 peak is claimed.

| Experiment | Status | Evidence scope |
|---|---|---|
| K32 initial integration | Compile failed101 | Generator borrowed a Vec instead of owning it; source/patch/log retained |
| K32 v2 partition | Passed0 | All256 SY words; active1–128, inactive aliases; dirty highQ; all-wire inverse and phase |
| K32 v2 column35 | Passed0 | Exact shot1170 state,64 lanes,259 dirty passengers, native arithmetic/inverse/phase; no payload |
| SZ donor/care helper | Passed0 | 512 cases with boundary and inactive sizes, arbitrary parked SZ6/7 data; care mapping and all-wire inverse/phase |
| Twelve-column diagnostic | Failed101 | Symbolic checker lacks PushCondition support; first Dq native forward result passed before the checker stopped |

The V-only and donor helpers use zero independent measurement coefficients.
The twelve-column diagnostic was intended to extend phase checks to the
complete column; its current symbolic checker limitation prevents that claim.
Its failed source, generated ideal-state fixtures and log are preserved.

K32 v2's patch SHA256 is
`4f90cafe019d3e9e35080b4b426b564f49febb64ac23f40b969748c1c4342364`.
The passing size-donor component patch SHA256 is
`4a4206c29aa5d618b19573ef606c5567e01ae8064bef9d204fc8dd0f22b7b758`.
Each accompanying manifest identifies the three source hashes and confirms
that all candidate changes are inside `src/point_add`.

The source-linked loan argument is in `K32_LOAN_PROOF.md`. The two SZ donors
require the source schedule's admitted lower bound101. For ideal large-SY
states, `Z*Y<p<2^256` implies `SZ+SY<=257`, giving SZ<=158 at SY>=99.
The tested101–159 interval is conservative and has an injective low-six-bit
encoding. Low-six values37–63 describe64+low, and0–31 describe128+low.
Excluded inactive low-six endpoints32 and36 were explicitly tested; the
unitary inverse argument restores arbitrary inactive values throughout.

The coordinator's source-bound model identifies shot3713 as a separate
crossing-parking failure: division1, Euclidstep60, direct crossing, Y119bits
and quotient375614 (19bits). It requires reserve9, whereas the existing
cycle provides7. K32 and an eventual QB24 repair do not alone fix that
ownership deficit. Native integrated reserve9 confirmation remains pending.

Completed logs are preserved under ignored
`research-output/overnight-20261014/qubits/`; these manifests and patches
are the tracked reproducibility record. The original compact submission is
unchanged.
