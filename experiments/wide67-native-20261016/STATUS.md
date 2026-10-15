# Wide67: terminal failure-rate rejection

The fixed 67-stage endpoint passes four native binding tests and reproduces
the frozen stream exactly, but fails its sole predeclared paired fresh census.
No nonce search, resampling or benchmark record follows.

The candidate has Q1556 and stream SHA256
`813d2863eebbba814c8d0b64eec28cdc6e47965a6d1839e3d0bb082dadaa80dd`.
Its unchanged parent is our public Toffoli source `5a7c3902`.
On 32,768 batches / 2,097,152 fresh shots per source, label
`wide67-frozen-20261016`, the candidate fails 1,351 batches versus 1,335
for the parent: 5.813324 versus 5.744476 failures per 9,024-shot packet.
Both have zero dirty shots. Diagnostic paired saving is
61.438305 ± 0.278440 Toffolis; it is not a scored resource result.

The complete 161-file point-add source archive, patch, protected-file checks,
native tests, generated stream hashes and census logs were preserved and
independently verified before the owned detached worktree was removed.
The 41-artifact outer archive is also independently verified. Cleanup checked
the exact worktree owner and active process paths. The frozen stream remains
on the server; all prior evidence and unrelated work remain intact.

The separately declared fixed wide95 continuation is a different experiment.
Its endpoint will receive its own qualification; no earlier checkpoint will
be substituted after seeing census outcomes.
