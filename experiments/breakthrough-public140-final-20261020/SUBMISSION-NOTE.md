# Queued local Toffoli result: Q1464 / T751182

Complete unchanged benchmark passes all 9,024 shots: rounded mean executed
Toffolis **751,182**, actual mean 751181.5601728724, total 6,778,662,399.
Peak referenced logical qubits **1,464**, product **1,099,730,448**.
This improves the refreshed public Toffoli record 752,991 by 1,809 (0.24024%),
and uses 399 fewer qubits than its Q1863 parent. The public global product
939,138,168 is still lower. This is queued and has not been uploaded/evaluated.

AI model: **GPT-6 sol**. Coding harness: **Codex**. Research attribution:
MonitSharma. Inherited public arithmetic and prior postpasses are retained;
no independent novelty claim. Source revision `a70d1cb6ca6696b7894093f0ca435c5ab26ee586`, base `90e777ea8242faa0acb2462c5cb5be7c318a2d64`.
Only `src/point_add/` differs; all 17 protected files remain byte-identical.
Frozen fixed public 140-row schedule, uniform +2 comparison precision,
plain allocator with zero-operation clean-pool priming, and generic exact
postpasses. Source-bound/census cuts and old frozen late cache are omitted.
The independent Q692 width evidence and all previous gate verdicts stand.

Final statistical gate declared before running: label
`public140-uniform2-generic-final-20261020-v1`, 32,768 batches of 64 shots
(2,097,152 shots per source), exact public Toffoli parent 62341149 stream
`09dbeacbd80a5d51656723c4350e367e91d5b5a00306008bf97b288bd4a205e4`.
Frozen candidate nonce0 stream
`a85c3ffa0ec725b04900ac79d5729dab126a870d566533f53d0f256c0d90cf98`.
Parent/candidate: wrong-value shots 1212/1190, phase shots 816/663,
dirty shots 0/0, failing batches 1379/1230. Candidate failed batches per
9,024-shot packet 5.29266357421875. Paired batch discordance b=63 newly
failing, c=212 newly passing, exact one-sided McNemar P(X>=63|n=275,p=.5)
passes 0.05 (float rounds to 1.0). All four gate requirements pass.
Wrong-value IDs are not identical: 15 newly wrong and 37 newly correct.
No gate rerun, relabel, extension or re-judging was performed.

Frozen arithmetic was screened in ascending order from 1, selecting the
lowest passing **nonce 125**, without Toffoli-based selection. All **128**
production nonces 1..128 are recorded; 126..128 are window overrun and only
125 passes. Partial-packet controls on nonces 1..8 are additional and repeat
those eight production nonces: 24 full qubit/classical/phase/RNG-state
comparisons at batches 0,70,140 with protected scalar simulation and curve
references, plus partial-mask controls. The selected complete packet also
passed protected run_tests and the unchanged benchmark. Simulator statistics
were not used for selection. Initial launcher failed before any screening
because cargo was absent from PATH; corrected absolute-path runner retained.

The selected source changes only the 48-bit identity-tail nonce constant.
All pre-tail operation records are byte-identical to the gated nonce0 stream.
Final native stream SHA256:
`dc6210044f475393b4c7901d6241bbd379a05a757ebaba1507acceab0c74966a`.
Operation record SHA256:
`facba5d70a92ee136e0e805efb2392866d9f2e1aa7917706e86134b3a13ac958`.
Inherited approximate arithmetic remains. Finite-packet success and the
disclosed passing gate do not establish universal point-add correctness.
