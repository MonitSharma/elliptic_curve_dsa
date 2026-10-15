# Project instructions

The objective is to improve three separate ECDSA.fail resource records: peak
logical qubits, rounded mean executed Toffolis, and their product. Refresh public
records before comparing. Read README.md and docs/research-plan.md first.

Current user priority (15 October 2026): focus research on lower executed
Toffolis and lower Q × T. Defer width-only optimization and Q692 submission
engineering; preserve existing width evidence. Treat qubits as a tradeoff:
extra width is acceptable for a Toffoli improvement, while a product improvement
must reduce the complete measured Q × T. Keep these two objectives independent.

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
- Do not search identity-tail nonces or tune hash-derived test packets. Run the
  unchanged official benchmark on final source and independent tests as needed.
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
