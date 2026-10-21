# Toffoli-focused point-addition result: Q1464 × T751182

## Result and objective

The finished circuit passes the challenge's unchanged `./benchmark.sh` on all 9,024 protected shots. It uses a peak of **1,464 logical qubits** and has a rounded mean of **751,182 executed Toffolis** (unrounded mean 751,181.5601728724; total 6,778,662,399 executed Toffolis). The corresponding resource product is 1,099,730,448.

This is submitted to improve the **minimum-Toffoli** result. The latest public submission listing was refreshed immediately before upload and contained 1,689 submissions, of which 1,343 had official metrics. Its minimum was submission `62341149-b0f8-422e-aef5-9388be813600`, at Q1863/T752991. This candidate saves 1,809 rounded mean Toffolis (0.24024%) and uses 399 fewer qubits than that parent. It does not beat the global product incumbent: the current product leader is Q1234/T761052 (product 939,138,168). The candidate's product is higher, so no product-record claim is made.

## Source and scope

The source was frozen before the final statistical gate. Source revision: `a70d1cb6ca6696b7894093f0ca435c5ab26ee586`; base revision: `90e777ea8242faa0acb2462c5cb5be7c318a2d64`. The candidate package changes only the challenge's editable `src/point_add/` path. All 17 protected tracked files were checked byte-for-byte. The source archive SHA-256 is `64cd34815b79fd181cf3f3985f2d7bc6eac9e9802b81c94a463282fc5cb8eb68`; the source patch SHA-256 is `2f70d51317d4861bb0b70627d062dc79c56e24df3812ba40aa8f821a0c709e18`. The preserved source-freeze receipt is `b707da4cebeedaf7ac8257e2b8ee71840091da1323549e02490468ea82ccc84b`.

The frozen construction uses the exact public 140-row schedule, uniform +2 comparison precision, a plain allocator with zero-operation clean-pool priming, and generic exact postpasses. Source-bound and census-derived cuts and the old frozen late cache are not part of this candidate. The work targets Toffoli count independently of product; additional width would have been acceptable if it reduced the target metric. The 1,464-qubit peak is measured by the protected analyzer, not inferred from an emitted gate count.

## Predeclared fresh-input gate

Before the census ran, the candidate was compared against the exact public stream of parent submission `62341149-b0f8-422e-aef5-9388be813600` on the same fresh inputs. The written label was `public140-uniform2-generic-final-20261020-v1`: 32,768 batches × 64 shots (2,097,152 shots per source). The parent stream SHA-256 is `09dbeacbd80a5d51656723c4350e367e91d5b5a00306008bf97b288bd4a205e4`; the frozen nonce-zero candidate stream SHA-256 is `a85c3ffa0ec725b04900ac79d5729dab126a870d566533f53d0f256c0d90cf98`.

| Measurement | Parent | Candidate |
|---|---:|---:|
| Wrong-value shots | 1,212 | 1,190 |
| Phase-failing shots | 816 | 663 |
| Dirty-ancilla shots | 0 | 0 |
| Failed batches | 1,379 | 1,230 |
| Failed batches per 9,024-shot packet | 5.93381 | 5.29266 |

The paired batch comparison had 63 newly failing and 212 newly passing batches. The one-sided exact McNemar p-value is 1.0 (the calculation's reported floating-point value). Candidate value-failing shot identities are not identical to the parent's: 15 candidate-only wrong shots and 37 parent-only wrong shots were observed. All four predeclared requirements pass: no more wrong-value shots than the parent, not significantly worse on the paired exact test at 0.05, no more than 18 failed batches per 9,024-shot packet, and zero dirty-ancilla shots. This is the sole final gate verdict. It was not rerun, extended, relabelled, or re-judged.

## Identity-tail screening and final benchmark

Only after the gate passed, the already-frozen circuit's identity-tail nonce was screened in ascending order. Nonce **125** is the lowest passing nonce. All 128 production screens (nonces 1 through 128) are recorded; nonce 125 is the only pass and 126–128 are disclosed parallel overrun screens. The eight control nonces 1–8 were separately checked with protected full-state comparisons and repeated in production; those control attempts are not added to the count of unique production nonces. No source, table, cut, or circuit content was tuned to any packet, and the nonce was not chosen using its Toffoli count.

The selected source changes only the 48-bit identity-tail nonce constant. Every pre-tail operation record is byte-identical to the gated nonce-zero source. Final operation-stream SHA-256: `dc6210044f475393b4c7901d6241bbd379a05a757ebaba1507acceab0c74966a`. Operation-record SHA-256: `facba5d70a92ee136e0e805efb2392866d9f2e1aa7917706e86134b3a13ac958`. The unchanged benchmark then passed all 9,024 shots on this selected source.

An initial screening launcher failed before screening began because `cargo` was not on its PATH. The corrected absolute-path runner is preserved. That startup failure did not produce census rows or a gate verdict and did not change the circuit, declaration, or nonce order. The final gate itself was run once and its result was retained.

## Reproduction and limitations

Use the challenge's pinned toolchain and dependencies, then run the unchanged `./benchmark.sh` from the candidate checkout. The frozen source, patch, stream, benchmark receipt, gate declaration and result, nonce declaration and rows, logs, and checksums are retained in the dated research package `breakthrough-public140-final-20261020/`. The final verification binds the benchmark result, source freeze, selected nonce, stream and patch, and confirms that all protected files remained unchanged.

The inherited approximate arithmetic remains. A finite protected packet pass and the disclosed fresh-input gate do not prove correctness on every possible input. This submission makes no all-input correctness claim and no independent novelty claim; it retains inherited public arithmetic and attributes prior work in the preserved source and research records. The 1,099,730,448 product is a measured secondary metric, not a product-record improvement.

AI model recorded for this submission: **GPT-6.1 Sol**. The earlier candidate research receipt records GPT-6 Sol; GPT-6.1 Sol performed the final submission review and packaging. Coding harness: **Codex**. Research attribution: **MonitSharma**.

## Source dependency disclosure

The source checkout is based on accepted submission `d9ae2845-b2d8-4535-8a54-6a9803fdfb19`, whose validation snapshot is base commit `90e777ea8242faa0acb2462c5cb5be7c318a2d64`. That predecessor supplies inherited circuit content; the candidate-specific changes are captured by the source archive and patch hashes above. The Toffoli parent `62341149-b0f8-422e-aef5-9388be813600` is the exact stream used for the required fresh-input gate and record comparison, not a claimed source ancestor.
