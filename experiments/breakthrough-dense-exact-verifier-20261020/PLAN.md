# Exact dense verifier qualification and control-only timing

Candidate61927788/gate unchanged; no quantum source or FS modification. Repack
surviving nonce lanes after each full simulator batch; exact backend, original
RNG words and fullstate classifier unchanged. All active states have consumed
identical bytecounts. SHAKE combine validates positions; every regroup compares
64bytes/lane against originalctx clone. Surviving nonce gets exact advanced
ctx+newlane. Failednonce finalstate witness retained; no model/IR rejection.

Freeze engine/libraries before8nonce partial/24protectedfullstate qualification.
Then repeat first1024 already-screened product nonces in both engines solely as
controls,16workers/1024windows; assert exact pass/kind/firstfailure/batchcount
equality. Record every additional2056 productcontrol attempt (8+1024+1024).
One separate positive control: officialdepth12 selectedstream63370be6,nonce41,
all141batches plus protected9024 replay. Total2057partial/controlattempts; not
newproductionselection. No candidate/gate/census change. No Toffoli/Q score.
Only after fullPASS and useful speed may a separate declared continuation be
considered. Existing original search/continuation and finalpipeline unchanged.
