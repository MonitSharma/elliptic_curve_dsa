# Exact complete baseline H45 applicability census

The [source-bound receipt](h45-census-receipt.json) and [observation patch](h45-census.patch) preserve a new clean-c5 checkout with the H45 experiment mode disabled. Only logging and a disabled cleanup helper are added within point_add. The unchanged complete official builder passed every existing source/table fingerprint and completed exit0. Its final operation stream is BYTE-IDENTICAL to the passing baseline, SHA25649b35cf7640ebd529d76894eb8bef93ebf57e7e970fe14b3c27c8c5feb6e73e4. Protected files and nonce are unchanged; no redundant benchmark is run.

All137 forward-fold invocations (including non-payload calls) are logged, with concrete tick, width, loan/fin/ttm/lean/drop flags and exact plans in the [summary](h45-census-summary.json). ZERO match the proposed free-cleanup guard loan && fin0 && !ttm && !lean45 && drop0. The parser explicitly covers PAYLOAD_AT=None; rejecting that initially was a parser assertion, not an arithmetic failure.

The only current source-selected loans are ticks128..136. Tick128 has fin3,ttmtrue,lean45true,drop0;129 has fin3/drop1;130..136 have fin4/drop2. All are ttmtrue and lean45true. The fin0/ttmtrue variant also has no current loan applicability. The independently proved H45 helper remains useful component mathematics but its current guard cannot change this baseline or qualify as a record improvement.

A useful production extension must explicitly handle the actual deferred-lean fin3/4 interfaces or prove a broader loan/replanning transformation. Operation/guard counts do not authorize sampled control deletion or fingerprint bypass. No resource/scorer claim is made.
