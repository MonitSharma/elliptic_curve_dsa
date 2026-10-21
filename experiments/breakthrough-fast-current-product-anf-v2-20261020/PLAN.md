# Faster exact current-parent proof by storing constants inline

Optimized representation ONLY: keep word constants inline rather than allocating a one-element polynomial Vec. Same exact boundedANF multiplication, <=8totalterms including nonzero constant, degree4/fullkeyopaque policy/productcache65536/16mmonomialbudget and soundTVfallback. Same currentpublic1829 source/cache/192fixedfixtures. Require all37native controls and33fullprotected numericIR/knownbit comparisons. Timing is verifier performance only, never quantumresources. No gate/nonce/source-circuit changes or production rejection. Truthoracles remain test witnesses only.

All input fixtures and quantum source are unchanged. Keep both old and new performance/precision outcomes. No cost-based nonce selection, statistical gate rerun or record claim.
