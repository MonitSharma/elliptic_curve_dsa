# Wider walk caps — terminal negative result

The predetermined caps 1792 and 2048 both generate the exact unchanged public
Toffoli stream at source 5a7c390233c72133df9b591c92e43422c5892142:
01aad987cfe03e7ca97df6f3dcd26085a21a5836aa6e661ec8fbd9c9c1b63740.
The configured 1536 cap is already above the width required by this path.
No new benchmark result, census or nonce search follows from this experiment.

Both candidates pass the six dynamic allocator tests. An initial broader test
invocation yields 29 passes and three failures; the untouched parent reproduces
the same three failing test names. Raw logs and the corrected comparison are
preserved, including the first parser attempt. This is not an all-tests-pass claim.

Protected tracked files were checked byte-identical. Both candidate patches,
complete point_add source archives, source hashes and generation logs are
preserved before removal of the three owned detached worktrees.
