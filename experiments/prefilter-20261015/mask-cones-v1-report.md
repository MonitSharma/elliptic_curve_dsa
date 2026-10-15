# Frozen mask per-root cone audit

Read-only source artifact:MRMASK01 v3 SHA256560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d,7914981 nodes,1024 inputs,512 scored-coordinate roots. No frozen artifact or operational library changed.

A backward exact512-root membership propagation counts each root's node cone and contiguous groups of1,2,4,8,16,32,64 roots. All kind/child/port/aux/root bounds are checked. Independent iterative DFS and original-node identity reconstruction validate min/median/max groups at each size (21 checks). Reconstruction preserves each original node's kind, port/constant and child identities, plus every selected output root; it adds no Boolean simplification or approximation.

There is only1 dead compiled node and103 distinct output-membership signatures. Exactly463 roots are constant dependency1, hence permanently unknown/known0. No root is constant dependency0, so there is no static-known mismatch rejection. The remaining49 roots are OR nodes, corresponding to scored bits309..374 at the positions recorded in mask-cones-root-summary-v1.json.

Every nonconstant root cone is large. The smallest two contain7118558 and7119356 nodes (89.94% of the complete program); the remaining47 exceed99.65%; the largest contains7914293 (99.991%). Accordingly, generic per-root/group pruning is a negative runtime direction, apart from small savings for two bits. No heavier runtime benchmark was justified or launched.

One valid separate filter remains: if zero-MR scored-coordinate mismatch intersects none of the49 nonconstant-root bit positions, that particular input cannot produce a mask-certified rejection and need not run the mask evaluator. This is a skipped witness attempt, followed by another witness or exact fallback; it is not a nonce rejection or acceptance certificate. Empirical operational benefit is unmeasured here.

The census and all21 independent reconstructions completed in5.67seconds on one core, under8GiB. This is structural analysis and does not establish a production speedup.
