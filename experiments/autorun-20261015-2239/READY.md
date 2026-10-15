# Submission queue — no external submissions authorized

**Explicit user authorization, 16 October 2026, 05:19 Singapore:** the
753721/Q1468 fifteen-stage entry below was submitted as
[`03be8e19`](https://api.ecdsa.fail/api/submissions/03be8e19-ab3b-45c7-9c62-9d78970c4d95)
after a fresh complete unchanged benchmark and source-hash check. Official
metrics confirm753721/Q1468 (public check05:45); rejection is solely because
Q*T does not improve. It is the independent public Toffoli minimum.
Other candidates remain in queue mode.
[Submission receipt](../wide15-record-20261016/submission-20261016/STATUS.md).

## 1. Lowest ready Toffoli count — fifteen-stage candidate

**Submitted and officially scored:**753721 executed Toffolis at Q1468; unchanged benchmark passes all9024
shots with zero value/phase/ancilla failures. Public minimum at16October05:45
Singapore is this753721/Q1468. The next strict T target is753720.
Product1106462428 does not beat939347948; four extra qubits are deliberate.

- [Submission note](../wide15-record-20261016/SUBMISSION-NOTE.md)
- [Result and prefix-audit receipt](../wide15-record-20261016/RESULT.json)
- [Status and complete evidence](../wide15-record-20261016/STATUS.md)
- Base:`5a7c390233c72133df9b591c92e43422c5892142`; patch and full point_add
  source are preserved in the experiment's evidence archive.
- Final stream:`1d8c05eeee7b43dd694506b5efe963c771461b7e690bc62f409947b2306b7d77`.
- Nonce644, lowest pass from1;731 screened, never selected by T.
- Final census1048576shots/source:670/16384 failed candidate batches
  (5.765991/packet), versus674/16384 parent(5.800415); dirty0.
- Final generation changes only the96-op identity tail; every pre-tail byte
  matches the frozen pre-search stream. All60 archived artifacts verify.
- Server evidence:`/home/hclau/ecdsa_research/wide15-record-20261016`.

## 2. Lower-width Toffoli alternative — four-stage candidate

**Complete archived alternative, superseded for the T record:**753745 executed Toffolis at Q1464; complete unchanged benchmark
passes9024 shots with zero value/phase/ancilla failures. Public minimum at
16October00:19 Singapore remains753771/Q1464. Product1103482680 does not
beat the product record939347948; target the independent Toffoli record.

- [Submission note](../wide-record-20261015/SUBMISSION-NOTE.md)
- [Result receipt](../wide-record-20261015/RESULT.json)
- [Status, protocol and evidence](../wide-record-20261015/STATUS.md)
- Base:`5a7c390233c72133df9b591c92e43422c5892142`; final patch in that
  experiment's `evidence.tar.gz`, member `evidence/final-candidate.patch`.
- Final stream:`ba9bd28402c5821e5dcb36795003f3ee5fe729bc2a071a9942567ce875ed02be`.
- Nonce92, lowest pass from1;164 screened, never selected by T.
- Final census1048576shots/source:674/16384 failed candidate batches
  (5.800415/packet) versus parent678/16384(5.834839); dirty0.
- Server evidence:`/home/hclau/ecdsa_research/wide-record-20261015`.

Refresh public records and reproduce the unchanged benchmark before an
eventual submission. This run is **queue mode**; no external submission made.

The product candidates remain research work, not queue entries. Product25
has an affordable certified search running since03:47; no passing nonce is
selected yet. Product67's proof, native tests, fresh gate and disabled complete
filter qualification pass. Repaired53 passes native/fresh checks,
but its first arithmetic-specific mask proves no usable rejection bits.
All still require a complete unchanged benchmark and final disclosed census.
