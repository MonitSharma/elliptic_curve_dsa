# Prefilter agent stop checkpoint

Recorded 16 October 2026 at 09:07:53 Singapore / 01:07:53 UTC, after the parent relayed the user's request to stop and analyze candidates. No further research, benchmark, generation, census, search or submission is authorized by this checkpoint.

## Process disposition

The only active process owned by this agent at the stop request was the bounded source-only affine-cone inventory in `/home/hclau/ecdsa_research/wide15-affine-cones-20261016`.

Ownership was verified before signaling:

| PID | PGID | SID | Role |
|---|---|---|---|
| 641570 | 641570 | 641570 | Dedicated `run.sh` launcher |
| 641571 | 641571 | 641570 | Dedicated 900-second timeout watcher |
| 641572 | 641571 | 641570 | One-core source inventory |

The requested reversible SIGSTOP was attempted only against groups 641571 and 641570. Both groups had naturally exited between verification and signaling: the signal command reported that both groups no longer existed. No signal reached another job. A subsequent explicit process check at 01:07:53 UTC found none of the three PIDs; `run.exit` is 0. There are **no paused or active processes owned by this agent to resume**. Other agents' jobs and unrelated workloads were not changed.

The inventory, logs, declaration, code and before/after source pins were preserved locally and on the server. It completed in 18.522568 seconds, inspected all 10,522,755 operations of immutable stream `1d8c05eeee7b43dd694506b5efe963c771461b7e690bc62f409947b2306b7d77`, and found three rank-four cones and no rank-zero/rank-two cone. No beneficial transformation, candidate, census or nonce search was produced. Declaration SHA-256: `5528a3839f780647d372fbc031b4b9cf33034bbe0036195a097acdb41950e606`.

Any future work requires explicit authorization. Do not restart this completed query or overwrite its evidence. A new experiment would require a new declaration and resource preflight; there is no pending SIGCONT instruction or resumable watcher.

## Candidate and evidence state

- **Product25:** The parent owns the completed operational search and final qualification. Independent review confirms lowest protected passing nonce **47,449,113**, complete operational prefix **47,452,160**, four clean worker exits, and all audited artifact pins. This is not a completed record claim here: the parent controls the unchanged benchmark and predeclared final census. The independent review archive is `experiments/product25-terminal-independent-20261016/evidence.tar.gz`, SHA-256 `1d276faa49e68cc1b340aaef34fc379ec86b0bc8e9a9ab3c7d0299cfeac028e5`. Updated final-census source review pins code `ca07e011727f380447d6e8b70619266c2f4c8af764824d314ff63bbbec41f4ce` in `experiments/product25-terminal-review-supplement-20261016/`.
- **Search accounting:** Five verified prelaunch Product25 archives contain **536,856** complete packet-row attempts over the same **262,144** distinct nonces, all repeated in the operational run. Operational plus those prelaunch row attempts total **47,989,016**; distinct nonces remain **47,452,160**. In-process helper/seed checks and later disabled runtime studies are outside that explicitly prelaunch ledger. Details are in `PRELIMINARY-ATTEMPT-ACCOUNTING.json` in the independent review folder.
- **Plain67:** Frozen source `268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d`, Q1234/B54995, has a qualified disabled runtime and completed persistent cost pilot. All 65,536 trial rows and 22 controls match; four-core measured throughput is 219–223 nonces/s. The ideal 64-thread mean is 16.17–16.47 hours, not measured scaling. A proposed eight-thread/24-hour hedge has only about a 17% ideal-model success probability and remains disabled. Its old failure gate is paired against original4b and cannot establish eligibility against a newly improved Product25 record. Pilot archive SHA-256: `28495fad94ee52e130df1acc0023fc62f2df979c2167b3e6430aa06e684d3eb2`. No search was started.
- **Repaired67:** The separate A29 arithmetic source plus conditional discrepancy guard remains a disabled, qualified component. Its persistent cost archive `95a3659f6e29b68a1c51a23f0e44e3432c9c62262447a009f98a9b001cd73ddb` has 83 verified members and complete row equality. It uses a different source, own census model and guard from Plain67; the cost studies do not establish a causal ranking. No search was started by this agent.
- **ALL70:** Fresh native base `06cdc5de3dadbe23a2ff306466ec2ef27514bed53be1145ec83bdf490cb99a7a` has a new partial MR-independence mask with 180 conditional roots and a fresh zero-MR IR. These are research artifacts, with no runtime/search authority. The mask requires metadata clarification sidecar `bfd68eae7215bfadaa0222b62203ec5cf6dc12c987af30ba6084c4282b07d485`; an old2a-only binding must be rejected. Fresh IR `a805af2e120bc191062d6901cbcd4d4a390abba814f3a2fd5007d4b0b46c3859` is source06-bound. Their archives are respectively `814a8e74aa0c4990e29cddf120a6739c117c45df773544bc6f83d5594ac58b87` plus metadata supplement `6255ca9f9350ce3751866b7ba0da2256295335c80ab62e11656b6faf509079ef`, and IR archive `b9fdff4b3f08f2fd380f69938fdfddfed09a65ca076c7991b160ba12e0a6cc7d`. Fresh cache/native/census work is owned by the product agent, not controlled here.
- **Toffoli source inventories:** Exact four-gate MAJ identity and its bounded two-CCX affine generalization are mathematically validated but source-negative on the current immutable wide15 stream. The four-gate inventory archive `bae49201f77bba64e30215cd3e5dd5d4f32512f643cc67fe15073807e181ab50` is frozen. The just-completed affine inventory is preserved in its separate folder. Neither provides the additional 51 Toffolis needed to reach the exploratory 753,670 target.

All submission artifacts, active/historical production libraries and source circuits were left unchanged by this stop handling. Queue-only policy remains in force. No external submission was performed by this agent.
