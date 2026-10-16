# Cache cleanup already uses zero-Toffoli measurement erasure

All15 stages on officialb5adb653 use eight source renderer modules with
byte-identical render and cleanup bodies. Every lease end emits
`Push(valid); HMR(donor -> m); CZ(a,b) conditioned on m; Pop`, then clears the
three private classical bits. No cache cleanup CCX exists. The only CCX emitter
inside each renderer computes the product on its first active use. All eight
full source hashes, exact cleanup lines and the complete15-call order are
preserved in RESULT.json and frozen-source/.

The donor is admitted clean, and the last controls retain the same product
through the end fence. When valid1, donor=ab, so measurement adds phase m*ab;
the conditionalCZ adds exactly the same phase, cancelling it for arbitrary m.
The Push snapshots valid before HMR changes m. When valid0, both are inactive
and the donor remains zero. The cleanup has0 executedT, one additional HMR
event, and three fresh classical slots per lease (valid,temp,m), all cleared.
Its operation-stream RNG cost and scope effects are already part of the
qualified source. There is no fallback CCX erasure path hidden behind a guard.

This read is specific to the added15 cache stages. It does not assert that all
inherited arithmetic uncomputation elsewhere in point addition uses HMR.
No new census, candidate, circuit rewrite or sampling was justified. The
source was read from the existing verified wide15 archive2e568f3d; its nested
source archive hash is541ea5ee. Full raw input stream remains1d8c05ee.
