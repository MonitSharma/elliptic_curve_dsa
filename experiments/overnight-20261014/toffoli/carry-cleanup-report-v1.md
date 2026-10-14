# Changed consumer carry cleanup: exact primitive, pending production route

The H45 cleanup removes the shipped forward loan's one unconditional carry regeneration in its explicit component interface. The original full c5 circuit has **zero calls satisfying that interface**, so this is not a point-addition resource record. Product research is independently studying an early loan expansion; the actual deferred late cleanup remains a separate experiment.

## Exact interface and proof

The unrestricted primitive has14 input bits: acc0..5,E0..2,Nm0..2,k1,k2. The source is public c5bb1ec876db859a3f9f8a9052c140a145df834e; canonical y15 source LF hash879b85060f6a5cfa412561d64860f1cab697f7a334f180f5be9102070d5a23b9. The guard is `loan && fin==0 && !ttm && !lean45 && drop==0`.

The consumer writes final bit3 and rebases y3 by c3, then measures c3. This changes the physical span: original acc3 is no longer an exported value. The previous fixed W40 free-cleanup obstruction therefore does not apply. Final low6 data plus E,Nm,k and the remaining30 physical helpers span45 independent functions. Reverse quadratic phase closure finds30 helper directions generated from final data/passengers. A reversible164-gate linear rebase maps the exact physical bank to these directions;30 independent HMR repairs use745 quadratic Z/CZ terms and zero charged gates.

[carry-cleanup-closure-v1.json](carry-cleanup-closure-v1.json), [carry-cleanup-rebase-v1.json](carry-cleanup-rebase-v1.json), and their source-bound scripts preserve every direction, coordinate and phase term. The verifier independently replays every quadratic identity and the invertible physical rebase on all16,384 input rows. The physical helper emitter hash is a3de0bf45baa2efd199c1b5d178a4c65f12aab9e0e17dcb9c4a92f5bb4fe6f22.

## Native component verification

[carry-cleanup-native-v1r2-receipt.json](carry-cleanup-native-v1r2-receipt.json) and [source patch](carry-cleanup-native-v1r2.patch) bind the passing native fixture to source, protected-file hashes, dedicated binary, log, PID2533045 and exit0. There are100,925,440 positive native cases. Both old and new loan folds test every14-bit input,38 higher payload words, and zero/every independent measurement coefficient. The old fold has80 measurements and the new fold79. A symbolic linear checker confirms conditioned XOR conjugations restore every value; there are no multiplied classical guards in those phase-basis layouts. This supports all measurement outcomes for those tested higher-word layouts. A removed phase repair is detected.

Seven paired room profiles independently check values, input passengers, dirty padding and every clean scratch wire, with matched random measurement prefixes. Each49152-shot profile emits and executes exactly one fewer Toffoli per shot. The sampled peaks are unchanged. These counts are complete fold-component evidence, not scorer results. The all-input low-boundary polynomial identity extends the cleanup algebra to arbitrary higher register values at that boundary; the finite native higher-word list alone does not prove the complete fold on every higher input.

The failed v1 compile and v1r1 test assumptions remain preserved. v1 used an unsupported QubitId hash assertion. v1r1 rejected conditional linear conjugations that cancel, and its cost assertion compared unmatched later-batch random outcomes. v1r2 changes those assertions and RNG pairing; the frozen cleanup helper is unchanged. No failed version is labeled passing.

## Actual production applicability and next interface

The independent full c5 census reported by product research is byte-identical to the baseline and has137 forward fold calls. It finds zero current H45 guard calls. The actual loan at128 is fin3/ttmtrue/deferred lean;129 is fin3 with drop1;130..136 are fin4 with drop2. The separate resource-only tight-room trace has93 successful and33 failed contexts, all retained in [carry-trace-v2-receipt.json](carry-trace-v2-receipt.json). These arbitrary room recipes are not a full-circuit frequency count.

The actual lean research first showed that simply moving low carry rebuilds and omitting c4/c5 does not admit all-free cleanup. The closed span misses exactly the c6 phase. A changed choice of regenerated helper is more promising: regenerate c4 instead of c3, keep y3 in its loan basis, and use the exact factor `p=(sum4+a4)*(a4+c4)`, with `c5=p+c4`. Then `c6=p*L5+c4*L5+a5*sum5+a5`, where `L5=sum5+a5+1`. The c6 measurement phase can use one conditional AND instead of the old two. The prospective mean saving is0.5 per admitted fold; physical scheduling, peak and all-measurement verification are pending.

The abstract E2-missing case in [actual-lean-c4-swap-v2.json](actual-lean-c4-swap-v2.json) is **not yet admitted for actual fin4**: ESh also changes the values of E0 and E1. That model assumes those two original values remain available. A native fin3 prototype can start with all E values retained. Actual fin4 needs a larger producer-aware interface or restoration of all E values after sufficient exact helper cleanup. No abstract ownership model is labeled a native whole-body result.

No protected harness/toolchain/scorer/simulator changes, nonce tuning, identity-tail search or sample-control census deletion were used. No full qualified score is attached to this report.
