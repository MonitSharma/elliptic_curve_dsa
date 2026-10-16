# Project instructions

The objective is to improve three separate ECDSA.fail resource records: peak
logical qubits, rounded mean executed Toffolis, and their product. Refresh public
records before comparing. Read README.md and docs/research-plan.md first.

Current user priority (15 October 2026, night): improve any of the three
records (qubits, Toffolis or Q × T) in long unattended runs; see
`docs/AUTONOMOUS_PROMPT.md`. Keep the objectives independent: extra width is
acceptable for a Toffoli record, a width record may cost Toffolis, and a
product record must reduce the complete measured Q × T. Preserve existing
evidence, including the Q692 width result.

- Candidate submissions may change only `src/point_add/` inside a track. Preserve
  the harness, scorer, simulator, curve reference, Cargo files, toolchain and
  historical results. Research documentation/scripts stay outside submissions.
- Keep source revision, patch, tests, logs and stream hashes for each experiment.
  Preserve failed experiments with clear status. Do not claim component results
  as full point-addition records, or old reports as newly verified evidence.
- README result plots may contain only officially evaluated public records or
  complete locally passing benchmark reproductions, with provenance stated.
  Keep failed, pending and component-only experiments in separate Markdown
  reports. Never display their generated or diagnostic counts as scored results.
- Disclosed-failure-rate standard (user decision, 15 October 2026; replaces the
  earlier no-nonce rule). An identity-tail nonce may be searched only on a
  finished, frozen circuit that meets the failure-rate gate below. Publish
  the nonce, the census (label, inputs, shot count, failure rates, test
  statistics) and the number of nonces screened with every submission. Never
  tune circuit content, tables or cuts to a packet, and never trade
  correctness for Toffolis to exploit the search. Run the unchanged official
  benchmark on final source.
- Failure-rate gate (statistical form, user decision, 16 October 2026). It
  applies only to gates declared after this date; earlier verdicts stand, so
  Product25 stays ineligible. Compare the candidate with the exact public
  stream of the record it would beat (the parent) on the same fresh inputs:
  one census label and at least 32,768 batches of 64 shots, with the label and
  batch count declared in writing before the census runs. All four must hold:
  1. Value-failing shots (wrong output point) in the candidate are no more
     than in the parent.
  2. Not significantly worse on the paired test: with b batches newly failing
     and c newly passing, the one-sided exact McNemar p-value
     P(X ≥ b | X ~ Binomial(b + c, 1/2)) is at least 0.05.
  3. Candidate failed batches per 9,024-shot packet, 141 × (failed batches /
     total batches), is at most 18.
  4. Zero dirty-ancilla shots.
  The outcome of a declared gate is final. Never rerun with a new label, more
  batches or another nonce to turn a failure into a pass. Never re-judge a
  past verdict under a newer rule.
- The three tracks are Git submodules. Save experimental diffs under
  `experiments/`; uncommitted nested files are not preserved by a root commit.
- Use SSH alias `smu_server`. ECDSA work belongs in
  `/home/hclau/ecdsa_research`; keep the existing chemistry project separate.
- Before changing `/home/hclau/quantum_chemistry`, verify hostname, branch and
  working-tree status; preserve tracked edits and untracked files. Check active
  jobs before launching or stopping workloads. Stage only requested files.
- Before launching server work inspect CPU, available memory, scheduler and
  processes. Use `nohup`, dedicated logs and PID records for long jobs. Default
  to four build threads and one library thread until capacity is rechecked.
