# Stronger conservative bounds after conditional reset and swap

Declared 19 October 2026, 17:35 Singapore before source screening. Same public
parent9dc3798c / source0c3a0751 / compressed SHA256
99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683.
The frozen parent4 search is independent and unchanged.

The first support method forgets useful branch information: after conditional
reset F, it keeps terms not already known to imply F. Strengthen the upper bound
to S AND NOT F for those remaining terms. Likewise use the precise conservative
conditional-swap bounds: A'=(A AND NOT F) OR (B AND F), and vice versa. A DAG
conjunction containing NOT(AND factors) and all those factors is contradictory.
These are exact Boolean implications, not sampled arithmetic cuts.

Keep the existing 16-term/32-factor bounds and overflow-to-TRUE behavior. Keep
every original operation, execution condition, physical RNG event and Toffoli.
Only relabel zero-proved quantum roles and restore outputs with swaps. No
predicate is inferred from a nonce packet or failure sample.

Three fixed inputs: original public order, the completed RNG-preserving cleanup
schedule, and the completed ordinary measurement-channel schedule. Choose only
by deterministic complete Q; ties prefer the original physical-RNG order.
Each gets protected transcript controls appropriate to its event mapping.
No statistical gate or nonce search follows until a lower-Q complete candidate
has been frozen, reproduced natively and qualified by the existing protocol.

Controls add complementary conditional resets and conditional swap of dirty
and clean roles to the prior exhaustive support/Boolean tests. One build job,
one screen core,32GiB after fresh resource checks. No job launched here yet.
