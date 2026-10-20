The preceding v3 stopped at compilation of the new independent phase-product
test: `analyze_ops` requires an iterator, and the test passed `&Vec<Op>`.
No native semantic test or complete point construction ran on v3. V4 changes
only that call to `ops.iter()`. Original failed v3 source and logs remain.
The adaptive one-to-four-carry scope in V3-SCOPE.md applies unchanged here.
No statistical gate or nonce search has been declared on either prototype.
