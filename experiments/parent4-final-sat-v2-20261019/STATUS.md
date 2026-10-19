# Corrected queue-only parent4 final verifier

Created19 October2026 after detecting a stale qualification-directory literal
in the first finalizer. Its expected archive hash was correct71bbeefc..., but
it looked in product67-native-20261016/product67 (actual archive428f0806...,
missing manifest) instead of product-pareto-20261019/parent4-qualification.
The search, acceptance, passing gate, source and source hashes are unchanged.
The old verifier's terminal-auditor controls did not cover this input path.

Preserve the entire old verifier and PID record. The v2 source changes only
the qualification path and its own run directory, plus read-only all-input
path/hash/archive/gate checks before launch. Re-run the six terminal-auditor
corruption controls. Bind all new Python/shell sources before waiting. Start
the corrected queue-only watcher, verify it live, then stop only stale waiting
manager610395 after checking its exact command, cwd and nonterminal search.
SWITCH.json records the replacement. No uploader or new gate/nonce search.

Actual native reproduction, tail invariance and unchanged official benchmark
still require a certifiable lowest pass and complete terminal JSONL prefix audit.
No scored resource result is claimed by the read-only path audit.
