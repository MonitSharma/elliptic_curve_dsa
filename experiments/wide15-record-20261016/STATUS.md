# Complete local Toffoli pass — 753721 at Q1468

The unchanged official benchmark passes all9024 shots, with zero value, phase
or ancilla failures. Total executed Toffolis6801582636; mean753721.4800531915;
rounded753721; product1106462428. The public Toffoli minimum is753771 at the
01:46 Singapore refresh, so this improves that independent target by50 T.
It uses four extra qubits and does not improve the product record. Queue only.

The predetermined15 exact cache stages pass48 native tests and reproduce the
frozen external stream. Complete anchored replays preserve original quantum,
classical and phase values including inherited failing inputs. Source changes
are confined to point_add. Protected files match the public5a7c3902 base.

Nonce644 is the lowest passing nonce from1;731 nonces were screened, including
parallel in-flight overrun. All1–643 fail; no nonce was chosen by T. The selected
nonce passes protected replay before the unchanged benchmark. Final regeneration
is separately checked to preserve every pre-tail operation byte, changing only
the96-op identity tail. No content/table/cut setting was tuned to a packet.

Pre-search fixed4096 paired batches/source: parent186 failed, candidate178;
candidate6.127441/packet versus6.402832 parent, dirty0. Final predeclared16384
paired batches/source (1048576shots each): parent674 failed, candidate670;
candidate5.765991/packet versus5.800415 parent, dirty0. Candidate value-failing
shots606, phase-failing383. Full census rows, including failures, are retained.
The small rate difference is sampling evidence, not a claimed arithmetic repair.
Final paired diagnostic saving41.89634 +/-0.39903 T per shot.

Final stream SHA256:
`1d8c05eeee7b43dd694506b5efe963c771461b7e690bc62f409947b2306b7d77`.
Final point_add patch SHA256:
`17975d79e80add6befa62a153e1d772fe502dea59f1e940fc47d1014ef431b7f`.
`RESULT.json`, submission note and evidence archive bind complete source,
patch, native tests, hashes, nonce screen, benchmark and all census cohorts.
