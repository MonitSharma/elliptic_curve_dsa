# Scheduling with guard-aware cleanup information

Declared 19 October 2026, 17:05 Singapore before screening. Same exact public
parent 9dc3798c / source0c3a0751 and stream SHA256
99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683.
The frozen parent4 search remains independent and unchanged.

Both exact methods alone kept Q1234. Guard supports prove 85,462 conditional
cleanups that the first scheduler's heuristic ignored. Combine these methods
in three fixed, source-only steps:

1. Compact the scheduler's workspace allocation; require exactly the old full
   permutation/hash, preserving the reviewed heuristic and conflict proof.
2. Pin the inherited identity tail, schedule the core with that same heuristic,
   then apply guard-aware lifetime coloring.
3. Use the source-bound proved-clean event list to prioritize zero-lifetime
   closures, with the same legal dependency graph and pinned tail; color again.

No quantum gates, arithmetic cuts or physical RNG events are added by these
steps. Every reordered circuit gets the full independent permutation audit;
the final allocator proves clean state again on the actual resulting order.
The annotations affect only scheduling priority, never correctness decisions.
Resource selection uses whole deterministic width, not sampled packets.
No statistical gate or nonce search is authorized by diagnostic counts alone.

Implementation limits remain one build job, one screen core,32GiB after a
fresh resource check. Further work after a zero result moves to the separately
declared materialized-guard construction rather than heuristic seeds or caps.
