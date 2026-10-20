# Recheck the same solver proof using RAM-backed anonymous files

Kissat produced UNSAT on one fixed source/input; initial180s DRAT-trim check
timed out, so result remains INCONCLUSIVE. No solver rerun/input/circuit change.
Verify original CNF/proof/binary/source hashes, copy identical bytes into Linux
anonymous memfd objects (no filesystem outsideworkspace), and independently
check the SAME proof with line-buffered progress and900s budget/6GiBaddress cap.
Require >=8GiBavailable memory before copying. Anonymous copies closed afterward.
Only DRAT-trim VERIFIED plus exit0 establishes certificate; otherwise unknown.
No statistical gate rerun/extension, nonce screen/rejection or quantumrecord.
