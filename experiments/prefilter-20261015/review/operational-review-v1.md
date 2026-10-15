Read-only operational review v1

The fixed four-lane, full4096-window partition and the required-prefix formula are correct. Independent enumeration checks796 prefix cases. Candidate-own Fiat inputs, compacted skip handling, all-keys-before-MR, per-bit conditional mask mapping and exact fallback match the protected semantics. Every possible pass receives full candidate protected9024 replay.

Findings requiring owner resolution:

1. P1: scalar shared library is loaded through SCALAR_FAST_LIB/default without a hash check. Wrong expected curve coordinates could create false authoritative rejects. Pin the resolved backend in acceptance and before loading; bind the operational executable as well.
2. P2: bind CLI first/lookahead/count to the operational receipt. Partial per-worker final windows leave global gaps (count5/lookahead3 omits15,18,21); fixed declared count134217728/lookahead4096 is safe.
3. P2: rescan all pass files after child wait. A smaller pass created after the final poll can be missed when the running-jobs condition becomes false.
4. P2: a lane stopped before its first window legitimately lacks progress. Accept missing aszero only when its required count iszero and exit iszero; otherwise fail closed.

The report records exact reviewed source hashes. No coordinator files were edited and no production search was launched. Any final positive qualification still needs complete JSONL row audit and unchanged benchmark.
