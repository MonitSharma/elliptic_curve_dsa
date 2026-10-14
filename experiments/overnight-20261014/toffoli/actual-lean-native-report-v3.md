# Actual deferred lean cleanup: passing fin3 component

The narrowed `loan && fin==3 && ttm && lean_m && drop==0` cleanup passes native value, ownership and phase checks. It emits one fewer Toffoli and saves 0.5 executed Toffoli on average per guarded fold. The unchanged c5 source has an actual call at tick128 with this interface. This is a component result; no complete point-addition score is attached.

## Exact schedule

[The independent 16,384-row proof](actual-lean-direct-v3.json) verifies every changed phase identity and the physical operands used to erase all fourteen Y16 table helpers. Those erasures require neither the released c3/TT wires nor any original E value. The rest of this narrowed schedule retains all three E values because fin3 has no ESh producer.

Rebuild c1/c2 and TT at their original cost. Rebuild `c4=(~final3)*y3loan` instead of the old c3. The measured c6 phase uses `p=(final4+a4)*(a4+c4)` and `c5=p+c4`; thus one conditional AND replaces two. Its correction is `p*L5+c4*L5+a5*final5+a5`, with `L5=final5+a5+1`. The temporary p is itself measured and repaired under the same classical condition. The remaining prefix helpers erase using the frozen quadratic identities, followed by the ordinary low-bit writes and c2/c1 erasures. Every allocated helper is released.

The helper source hash is `95321e04f921b6143b517571ac72f4f06922ecce6b0f97d481c927bf58523db1`. [The passing point-add-only patch](actual-lean-native-v3r1.patch) retains the protected harness and source files unchanged. The experiment switch defaults false.

## Native evidence

[The v3r1 receipt](actual-lean-native-v3r1-receipt.json) binds c5bb1ec876db859a3f9f8a9052c140a145df834e, source hashes, patch, binary hash, log, PID2571092 and exit0. A fresh dedicated target prevents a cached binary from a different checkout. The run used at most four build threads and one test thread, with a 16 GiB virtual-memory bound; actual peak RSS was1,170,232 KiB.

There are262,144 exact fixed-input/layout proofs: all14 low/control bits, four higher payload words, two tight layouts and old/new folds. The frozen phase kernel proves zero phase for every independent measurement outcome in each layout, including the nested condition introduced by the conditional temporary erasure. Every quantum wire is checked. Dirty padding,512 dirty classical ABI bits and their quantum copies are retained. Another786,432 native cases verify all outputs, arbitrary incoming phase and classical ABI, with c6 outcomes forced to zero, one and alternating patterns. A removed phase CZ is detected; all four frozen phase-kernel fault tests pass.

| Layout room | Old emitted CCX | New emitted CCX | Old executed total | New executed total | Cases per version |
| --- | ---: | ---: | ---: | ---: | ---: |
| 4 | 124 | 123 | 20,456,448 | 20,358,144 | 196,608 |
| 5 | 123 | 122 | 20,124,672 | 20,026,368 | 196,608 |

The subsequent [v3r3 dropped-carry receipt](actual-lean-native-v3r3-receipt.json) qualifies fin3/drop1 with an actual dropped chunk, explicitly asserted from the emitted source plan. Its room3 layout passes131,072 all-measurement fixed-input/layout proofs and393,216 native cases. Old/new emitted counts are131/130; executed totals are20,613,120/20,514,816 over196,608 cases per version. The true source caller at tick129, room39, cap1234 emits1322/1321 at unchanged peak1234 and hits the new guard once.

The source-caller resource fixture uses cap1234, room40 and tick128. Its old/new emitted counts are1299/1298, its peak remains1234, and the new guard executes exactly once. This fixture establishes applicability, allocation and cost, not the full producer's arithmetic or phase.

## Preserved failure and scope limits

[The original v3 failure](actual-lean-native-v3-receipt.json) remains preserved. Both room4 variants passed their exact phase and native checks, but the fixture incorrectly interpreted the third return from `analyze_ops` as an emitted Toffoli count; that return is the register count. Its zero counts and failed assertion are explicitly invalid. V3r1 changes only this count to the explicit number of CCX operations; the mathematical helper and y15 source are unchanged.

[The v3r2 failure](actual-lean-native-v3r2-receipt.json) also remains preserved. Its component passed, but the drop1 parameter selected a merged plan with zero actually dropped chunks in rooms4/5. Its room40/tick129 source caller was fin1 rather than the required fin3, and its log mistakenly printed a hardcoded tick128. These scope mistakes do not qualify the actual dropped-carry prefix. V3r3 instead asserts one dropped chunk, uses component room3 and the documented fin3 caller room39/tick129. No failing input was removed.

Four tested higher words do not establish all higher quantum inputs for the entire fold. The changed cleanup reads only the low6 data and its constructor/control bank, so the 16,384-row identities are exact at that explicit boundary; general propagation through the unchanged ladder remains a separate composition obligation. The actual fin4 producer also changes E0/E1 while shedding E2, so the earlier abstract E2-missing model does not admit fin4. A separate exact top1/direct/nondeep producer contract and native v4 experiment are pending. The c5 full circuit is independently known to have inherited approximation failures, and no full qualification is inferred from these component checks.
