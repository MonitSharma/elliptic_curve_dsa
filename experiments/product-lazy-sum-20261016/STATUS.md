# Lazy expected sum: terminal dependency rejection

This attempted drop-in runtime change fails its predeclared row-identity gate.
No production file changed, rejection stayed disabled and no nonce was selected.
It must not be deployed as an equivalent version of the current screener.

The scalar-split API itself passes its independent fixture and edge checks.
The integration also passes all 9,024 point-triple/final-reader comparisons,
the 11-input partial-packet check, protected full-state/MR replay and forced
fallback comparison. Readiness is checked before scored-value comparisons.

However, 81 of the first 128 diagnostic nonce rows use a different advisory
witness. The current two-walk advisory consumes both P.x−A.x and
A.x−(P+A).x. I incorrectly assumed the expected sum was needed only when
confirming a witness or running the full fallback. Supplying a dummy sum to
the reverse-walk advisory changes its heuristic input. The row-identity check
caught this before the later 4,096-row gate or timing stage could run.

This is an omitted consumer dependency, not a finding against the frozen
scalar API or the active product search. The initial source, build, successful
partial controls, failed assertion and differing rows remain preserved.
No validation result is relabelled as a complete pass. A future forward-only
advisory would be a distinct experiment with new correctness and cost gates;
none is authorized for production by this failed drop-in attempt.
