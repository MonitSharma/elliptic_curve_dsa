# Agent handoff: start here

## Latest: 17 October 2026, 08:30 Singapore — two queued records, PRODUCT95 searching

- **Ready, queued for the user (not submitted):**
  - PLAIN67 product: **761,121 × 1,234 = 939,223,314** (beats 939,347,948).
    Candidate tree `/home/hclau/ecdsa_research/plain67-final-20261016/candidate`;
    note `experiments/plain67-final-20261016/SUBMISSION-NOTE.md`.
  - WIDE95 Toffoli: **753,694 T** at Q1556 (beats our 753,721). Candidate tree
    `/home/hclau/ecdsa_research/wide95-native-20261017/candidate`; note
    `experiments/wide95-20261017/SUBMISSION-NOTE.md`.
  Refresh the public records before submitting either one.
- **Running:** PRODUCT95 ascending search
  (`plain95-operational-20261017`, started 08:19:49, 48 h cap, 4 × 14
  threads). Gate PASS vs both the record and PLAIN67 (10.6 T below PLAIN67).
  Watcher `plain95-final-20261017/watch.sh` audits, freezes, benchmarks and
  writes `WATCH_RESULT.json`. **Do not stop or restart it.**
- **Running:** product cache continuation 96–123
  (`product-exact-20261015/product-to123-rank-20261017`, declared before
  generation). If its checkpoints show a real saving, qualify it like PRODUCT95
  (universal certificate, native port, declared gate vs the then-current record).
- **Negative this session:** `experiments/opt-research-20261017` (no provable
  never-firing Toffolis, no sinkable guards, no free qubit at Q1234).


## Latest: 16 October 2026, 09:40 Singapore — PLAIN67 product search running

- **Rule change (user, 16 Oct):** the failure-rate gate is now statistical
  (see `AGENTS.md`). It applies to gates declared from now on. **Product25
  stays ineligible** (its declared gate failed: 4,139 vs 4,118 failing
  batches) and must not be submitted or re-judged.
- **PLAIN67** (record circuit `4b2ec52f` + 67-stage exact cache, Q1234,
  −102.14 ± 0.44 T paired) passes the new gate on its pre-declared cohort:
  value failures 3,622 vs 3,622, McNemar p = 0.65, 17.91 per packet, dirty 0.
  Its ascending nonce search **started 09:36:40 Singapore** on the server:
  4 × 14 threads, 48 h cap, expected about 18.5 h, queue mode. **Do not
  stop or restart it.** Monitor and finish it as described in
  [its STATUS](../experiments/plain67-operational-20261016/STATUS.md).
  A watcher (`plain67-final-20261016/watch.sh`, dry-run verified) audits and
  finalizes a pass automatically, up to the unchanged benchmark and a
  public-record comparison. Check `plain67-final-20261016/WATCH_RESULT.json`;
  `READY_FOR_USER_REVIEW` means: write the note and ask the user to submit.
- Overnight evidence is committed (`e6052371`). Files over 5 MB are listed with
  their hashes in `experiments/LARGE-FILES-MANIFEST-20261016.json`.
- The other overnight pipelines (ALL70, ALL74, PRESEED10) remain stopped
  (`T` state). Resume them only on an explicit user request.

## STOPPED at user's request: 16 October 2026, 09:07 Singapore (historical)

**Do not launch or resume research, searches, benchmarks, censuses or
submissions.** The user requested a stop and candidate analysis in the review
chat. Our owned live pipelines are reversibly stopped; all sources and partial
outputs are preserved. Product25's unchanged benchmark finished just before
STOP: **Q1234/T761171/product939285014**, all9,024shots/channels pass. Its final
fresh census is NOTRUN, so it is not fully READY. The post-verifier is paused.
Read [the complete stop and readiness checkpoint](../experiments/autorun-20261015-2239/STOP-20261016-0907.md)
and each agent's STOP-CHECKPOINT before any continuation. Original active
checkpoints below are historical. No submission or automatic resume was set.

## Latest: 16 October 2026, 08:55 Singapore

Read the newest research-plan section first. PRODUCT25 SEARCH IS TERMINAL:
lowest protected pass47,449,113, complete audited prefix47,452,160/overrun3047.
ROOT_TERMINAL_AUDIT.json passes every row and runtime pin; never restart the
old four workers. Product agent owns isolated final source/unchanged benchmark
in product25-final-20261016. Root owns the predeclared final census and queue
gate; no submission. A search pass is not yet a scored resource result.

Plain67's persistent pilot passes; ideal64 mean16.2–16.5h is a scaling model,
not measured64 throughput. Any search requires then-current failure eligibility.
Seed's sole fresh comparison is active. NEW complete PRESEED10+fresh67 is the
cheap source-family repair lead, with an additional mandatory comparison against
the frozen final product25 source if its final gate passes. ALL70/ALL74 chains
are separate, unchanged studies. Root current-parent4096 universal stage passes
via a reviewed proof-only identity adapter; native/full-state replay pending,
4.3948T proxy/Q1473 is not a score. Public08:55 unchanged Q677/T753721/product939347948.

## Current checkpoint:16 October2026,08:15Singapore

Read the newest research-plan section. Public08:00 unchanged Q677/T753721/
product939347948;12 publication checks pass. Original25 four-worker48thread
search untouched: verified08:10:46 snapshoteb95aac0 =42,586,112 distinct rows,
lower prefix42,184,704, no pass signal. Keep ascending lowest-pass policy and
terminal auditor/final fixed census. Snapshot is not a scored result.

Plain67 diagnostic102.13839T and repaired67 diagnostic49.55103T stay pending
benchmark. New ALL70 restoration native base06cdc5de is complete; all other
Ops/MR/classical/tail equal original2a,17 protected dependencies unchanged.
Agent product_savings now freshly derives fixed67 caches/universal proof per
stage, final native source then sole32768/source label
product-all70-fixed67-independent-20261016-v1. No interim selection/resampling;
one worker/source (2total) after qualification. Restore cost56..70T/Q0, source
proxy63 is not measured T. Fresh whole-source mask is independently queried
by prefilter agent, cap32/all512 outputs/24GiB/900s. No original-mask transfer.

Seed+1T/Q0 repair sole fresh cohort active under failure_floor:
seed-restore-20261016/seed-fresh/{parent,candidate}.{log,jsonl,exit}; parent
PID427621, coordinator412785, sequential4workers. Do not claim final failure
benefit. Complete207 source freeze/root native+whole12mOp comparison PASS.
N2 readonly normalization and temporal separate clean-hole storage negative;
no arbitrary dirty/reset shortcut. ALL74 deletion-family source study pending.

Disabled-filter preparation profile: C curve70.955%, C rail26.099% of summed
worker time, startup separate. New scientific preparation figure explicitly
separates scopes. Scalar window16 lowers memory/startup but no stable compute
gain; original production20/library unchanged. Old repaired67 cost proposal
stays hard-disabled. Root independently verified34/28/60/21/16/26 respective
source-family/review/scalar/fanout/cleanup/readonly archive members; no score.

Root isolated wide15-retained4096-20261016 single-stage study active, PID518734,
one core/64GiB/2700s with minavailable preflight228GiB and own-stop110GiB. Parent
is current official1d8c05ee; not oldwide95 retry. Source-only; no new nonce or
fresh census until native/universal/phase gates. Its DECLARATION freezes the
prospective32768/source label before generation. Preserve unrelated jobs.

Latest remotely verified backup4f5b7ab. Queue only. README/submission edits
belong to the separate chat and must stay out of root path-limited commits.

## Current checkpoint:16 October2026,07:43Singapore

Read [research-plan.md](research-plan.md)'s newest section for exact evidence
and next steps. Public07:06 remains Q677/T753721/Q*T939347948. This run is
QUEUE only. The separate submission chat owns README upload edits and its
submission directory; exclude them from path-limited root commits.

Product25 unchanged48thread search:07:44:22 immutable65-file snapshot320deb1b
verifies38,182,912 distinct completed nonces/lowerprefix37,810,176/no pass.
Plain67 saves102.13839T/Q1234; repaired67 saves49.55103T/Q1234. Neither has
a selected nonce or full benchmark. Complete raw85/fused79 filter runtime
checks PASS, but measured4process8thread cost FAILS. Hard-disabled proposal
stays disabled; no inferred search authority from source proofs/component3x.
Timing archive65f6dc1f has87members/65536 matching rows; restart-inclusive
232..239h forecasts must not be confused with program-only110..121h proxies
or actual64thread/persistent-worker measurements. Prepare fine-grained profile.

Square4 exact+16T/Q0/MR0 source passes sole32768fresh gate:4175->4173 batches,
2value repairs/no new channel failures; independent736member/168source/fullrow
review PASS. Standalone is not a resource record, no cache composite authorized
from this evidence alone. New exact seed restoration adds1T/Q0/MR0 and changes
one inherited CX back to originalCCX; all other11630715Ops/MR/classical/ABI/tail
are identical. BDD arbitrarytarget/96MR+actual-prefix48clean proof independently
reviewed. Fullnative/protected qualification PASS; fixed32768parent/candidate
census active4workers/PID427621. Do not claim population failure improvement yet.

Per-phase attribution addendum57f220bd corrects old latch limitation:34fold,
14N2,3square,4unresolved among55 current advisory-unexplained witnesses. Seed
diagnosis3ae03610 isolates one additional inherited control fault and its exact
entry predicate; not a sampled rate improvement. Independent29member review
4f05ba79 includes all source generators. All-N2 retention+8Q/native-table failure
and complete3903-artifact dirty-RHS negative are preserved. Signed64 advisory
tail component passes; timings noisy, no production adoption. Wide15 quadratic
and affine guard-cofactor source-only censuses both negative.

Latest remotely verified backup092b536a. Current checkpoint work is not yet
pushed. No chemistry changes, external submissions or active-search restarts.

Last updated 16 October 2026, 07:43 Singapore. This page is for an AI agent (or
person) continuing the work. It holds the current state, the rules, the tools
and the next steps in order. Details live in the linked reports. Do not copy
numbers from older reports without checking the date.

**06:54 checkpoint:** public full refresh06:08 confirms Q677,
T753721/Q1468 (our separately submitted03be8e19), and product939347948.
Product25 unchanged ascending search has28,557,312 distinct completed nonces,
complete lower prefix28,446,720 at06:45:59; no pass. Immutable65-file snapshot
f5b517ef... independently verified. Preserve its four active workers and source.

Plain67 remains the strongest qualified saving:102.13839T/Q1234, no67nonce or
complete benchmark. Repaired67's universal proof is now COMPLETE: all67stages,
245849leases/540826uses. Root independently checked every actual newstage54..67
log, immutable kernel/protected hashes and complete source chain. The full3845
artifact history verifies through unchanged3390base,9ec98892delta and new
750713-byte97be8c18delta; no oversized canonical archive is committed.

The new A29 conditional arithmetic theorem b351ae4c... permits transfer only
when public discrepancy G355f9951... is zero. All29 paired helpers have arbitrary
dirty entry contracts, independent internal MR and complete live-classical/frame
proofs. Actual-prefix composition uses1831784nodes/1024ports, and independent
root compiler/binary/ABI review passes. New dependency is old_dependency OR G.
Existing fixed445 coverage retains418/421 old certified value witnesses and
excludes all14 parent-only repaired53 lanes. This is not a fresh census or
phase/Fiat transfer. Isolated repair67-conditional-filter-20261016 is now in
DISABLED qualification, including ownFiat, protected9024fullstate/phase/MR,
fixed445 known-bit containment, wide classical65535/66244 and explicit forced
scheduler fallback. Initial missing receipt and detached Cargo PATH failures
precede evaluation and are preserved; continuation uses the same prepared tool.
Do not enable or replace any production filter from these static proofs alone.

Failure attribution now uses actual final2a, not the old raw pre-table observer.
Every431 witness/all413 original64-lane contexts exactly matches protected
q/b/phase/T. Advisory-unexplained55witnesses/54batches gives1.8588867 perpacket
on that fixed4096cohort, distinct from oldB3's roughly1.1. Fourteen cases first
fail one low_keep_add because N2-loaned scratch q555/q556 enters dirty; the
observed +/-4/8 matches the reused carry. Generic reversible repair/cost is
pending. Never reset away the retained quantum information. Separately, the
predeclared all-four C130 square carry candidate (+16T/Q0/MR0) is frozen and
its sole32768/source fresh census remains active; no subset/resampling/composite.

New method negatives: earlier global cleanup found no selected opportunity
outside existing LCA admission on either fixed4b/95. Restored-product endpoint
analysis recovered159nonconstant endpoints, but ALL42 feasible selected leases
have mutually exclusive execution guards and exactly zero reuse gain. No
renderer was justified. Preserve both reports and the independent guard proofs.
Scope restoration alone passes4.4million protected lanes, not a circuit result.

Current priority: finish disabled repaired67 integration and independent review;
continue original25 search; derive source-family N2 loan repair; finish frozen
square census. No external submission from this run; preserve the other chat's
README upload note and submission directory. Root main HEAD3deaf6a2 contains
the README facts only; the latest remotely verified backup is448b3686.

**06:05 checkpoint:** public read-only refresh at05:45 confirms our753721/Q1468
is now officially scored, submission03be8e19, sourceb5adb653. The service rejects
it solely because its product does not improve the accepted product record;
it is the independent public Toffoli minimum. Q677 and product939347948 remain
unchanged. Submission was performed by the separate authorized chat; this run
remainsqueue. Preserve its shared README/submission edits.

Product25 unchanged search:05:46 snapshot18,866,176 distinct completed nonces,
complete lower prefix18,780,160, no pass. Immutable snapshot2a8caa82... verified.
Plain product67 remains the strongest qualified saving:102.13839T/Q1234,
native/fresh/universal/cache-transfer/disabled-runtime PASS, no67nonce or full
benchmark. Repaired67 now passes native and sole32768fresh gate atQ1234:
49.55103+/-0.50630T saved,4134candidate/4138parent failed batches,dirty0.
Value lanes3632->3620:12fixed/zero new in2,097,152shots; final14-stage cache
audit is active. Repaired53 universal A29-relative audit is complete; independent
root review nowPASS, including all53logs/hashchain and identical reviewed
kernel. Root independently verifies67's170native files and all failure lanes.
Neither repair may reuse original4b arithmetic masks.

A29 whole-lifetime v3/v4 proofs accept the exact mapped folds, including all37
in v4, but still certify zero output bits; residual square cleanup is being
investigated with source-bound contracts. Root separately tests the same37
whole folds on original4b in original37-mask-20261016, with fresh local proofs,
original reset files, private outputs, one core and24GiB. Production mask560c
and search stay unchanged. Never infer global independence from local proofs.

Rootwide2048 is TERMINAL FAILED: sole32768sample gives1351candidate versus
1338old5a/1350new753721 failed batches. No resample/search/fullbenchmark.
161source files/17protected dependencies/allthree full cohorts verified;
owned tree removed after archive and workload checks. Its conditional nonce
plans are abandoned. The failure team is testing a potential short-donor exact
precision primitive; no donor has yet been proved available in the target
source and there is no new circuit candidate from it.

**05:31 checkpoint:** product67 complete disabled filter nowPASS ownFiat
controls, protected9024q/b/phase/physicalMR,128+partialpackedshadows and all6
4096row crosskernel comparisons. Root independently re-counted rows/markers,
verified unchangedbinary and exactsource differences onlycandidate/proofbinds.
75-filearchive9f392381... verified. Two-thread coldtrial medians36.895009s
generic/35.168452direct have large variation, not a measured48thread forecast.
No67nonce/searchauthority/fullbenchmark yet; production25 remains unchanged.

FreshA29mask is TERMINAL NEGATIVE: exit0,33native+4protected containment
streams,4161freshreset+376freshhelpercontractsPASS, but all512rootsCONST1
(2-node maskfb176266...). No certifiablebits/fastrejection.80-filearchive
fef4d688... independentlyverified. This is model weakness, not proof of real
MRdependence. Prefilter now checks the first residual tick128 carry lifetime
using exact prefix relations; a short-window contract correctly remained
unproved, including nonzero q195. No clean-carry assumption is permitted.

Flag12 fixed4096physicalgatePASS506→499batches, but sameinputs/oldMR-mapped
diagnostic gives EXACTLYidentical506batches/548shots/437value/328phase,
zero actual repairs/regressions, +5.998718T. Drop cache composite for no observed
benefit. Its separately reviewed universal coordinate transfer/source theorem
is useful proof infrastructure only; no improvedfailureclaim. Failureagent
returns to true value-floor contracts.

Rootwide2048nativequalification nowactive: frozenf84c499f...,Q1560,
10,548,555ops,~67.949anchoredT saving. Sole originaldeclared32768sample/label
unchanged; presample05:22:53extension adds complete753721 reference on SAME
inputs, no candidate resampling. Onecoreper3streams after nativebyteidentity.
Both failure references must pass before nonce work. Extra width is intentional.

Separate authorized submission chat uploaded the prior753721/Q1468 result at
05:19 as03be8e19; publicAPI checked05:23 saysvalidating/noofficialmetrics.
This research run made no external submission and remainsqueue. Preserve that
chat's README/submissionfiles/jobs; do not stage its edits. Currentrootbackup
commitbffb3826 is pushed/remoteverified. Use path-limited commits for owned work.

**05:09 checkpoint:** public refresh05:06 finds new Q677/T950615823,
source d9d5e99119f0ef7702f926ff3c70a9d1efd93903, submission18912d63;
T753771 and product939347948 unchanged. Product25 live snapshot05:06:01
has12,410,880 complete distinct rows/lower prefix12,345,344, no pass;
archiveb5e0c504... independently verified. Production workers remain unchanged.

Repaired53 native13d1f734... now PASS18tests/full stream identity;
170 full source files independently rehashed, protected harness unchanged.
Its sole fixed32768 paired census passes:4185parent/4141candidate failed
batches, lambda18.007965/17.818634, zero dirty. Net39.349014±0.509027T
saved atQ1234. Value failures3553→3539shots,12parent-only batches/zero
candidate-only; phase/MR coupling remains noisy. No full benchmark or nonce.
Original4b masks/zeroMR IR are INVALID for its changed arithmetic. Fresh
A29-relative53 universal audit and A29 mask are active. Root fresh A29 zeroMR
IRa408f996... passes512protected allq/b+512scope fixtures; no phase/MR
independence claim. See experiments/repair-zero-mr-20261016/STATUS.md.

The 3390-file product archiveaa137f82... is independently verified, with
170 native repaired-source files checked separately. Supplementa8fedefb...
reconstructs all3444 target artifacts exactly from this immutable base, including
terminal2048/4096 studies. Offered64 scratch capacity yields actualQ1560,
not1620: cap2048 saves one extra anchoredT beyondwide95; cap4096 terminates
on its24GiB memory cap. Neither is scored. Repaired67 generation continues.

Both-back-seam zero-cost phase repair has zero effect on its sole4096 census:
531failures each, lambda18.27905>18; no search/composite. Its521-file and
free-borrow208-file negative archives independently verified. New Flag12
one-Toffoli lower-MAJ family has universal local phase/value proofs and12
wrong-cleanup negatives; native/fresh qualification is active, no result yet.
Post-cache composition must check added lower reads against donor leases.
NUMA binding is negative (3.66% slower median); no active affinity changes.
Two strict dirty-fanout/shared-control source queries find zero eligible sites
on all4 fixed streams. All such diagnostics stay outside README resource plots.

**04:40 checkpoint:** universal67 certificate303a75ec... nowPASS67stages,
245820leases/540759uses, same verifier2e9f5ee6... as25. Per-input transferd774c492...,
MD5914f683..., ABI2d7f0fc1..., identicalordered4x256physicalports,Q1234/B54995.
Independent2214x8candidateMRknownbitchecksPASS17712; jointworkspace54995.
No67search/fullbenchmarkyet. Product25active unchanged; immutable04:28:41snapshot
76a74e4b... contains6459392complete/lowerprefix6410240,65filesrootverified,no pass.
Newterminalaudit.py SHA70dd1d43... reviewedwith23lane+11fullsyntheticcontrols,
notrunonactiveJSONL; requirescleanexits/exactcoverage/lowestpass/runtimehashes.
Allfinalbenchmark/census/prefixgatesremainrequired.

RootdirectthreadCkernel1444e146... passes8192arbitrary+512actualallq/b checks;
disabledfullpipeline3paired4096/8trials median9.969237→9.258027s,allrows/shadowsPASS.
Do NOT replace productionlibs. Maskcone/lazynegative;49outputzeroMRcone only0.447%
smaller. Scalar-split365407f4... APIvalidatedand5.1%prepsaving,butrootdropindeferral
FAILS81/128witnessidentity:rail_fast_ffi consumes expected.x for reversewalk.
Preservefailedproduct-lazy-sum source/logs, no deployment. NUMAcomparisonprepared
byagentprefilter, onlyisolateddisabledtool, noactiveworker affinitychanges.

Productagentnew3265filearchive214865b6... rootverified; ownsproduct95, repaired53
native/fresh(originalcomparison),wide95thenindependentretainedANF2048/4096+scratch.
Wide151abandonedBEFORElaunchbasedsourceonlyproxy1.8e-11; declarationretained.
Strictwidthnegative correction709unhandled(not585),752paidT,124conditionalentry
loansunproved. Backphase2sitezeroT/Q/MRrepair97f16886... native/proofPASS,
fixed4096freshgateactive; inheritedR5cleanliness104/105UNKNOWNexplicit.
Generic1CCX+HMRMAJprecisionfamily cost/proofnext. Runtime/failure/scriptnegative
evidence staysoutsideREADMEscoredplots; queuedbestT753721unchanged.

**04:15 checkpoint:** product25 search continues unchanged, about3.8million
complete nonces and no pass at04:12. Final paired census is now predeclared in
`product25-operational-20261016/FINAL-CENSUS-PLAN.json`, label
`product25-final-nonce-20261016-v1`,32768batches/source, no failed-gate resampling.
Public04:08 refresh leaves all records unchanged. Wide67Q1556 native tests and
exact stream pass, but sole32768 fresh gate FAILS1351candidatevs1335parent;
61.4383T diagnostic, no nonce. All161sourcefiles/41outer artifacts verified,
owned native worktree safely removed. Separatewide95 remains active.
Front-seam zeroT/zeroQ phase-precision repair9aaf3117 passes universal local
proof/native admission but fixed4096 freshgateFAILS cap18.14136, exactlysame
outcomesasparent; no measuredbenefit/no search/no phasefix67launch. Phase509file
andseam283file archives independentlyverified. Agentfailure now audits structural
ordinary/TOP1freeborrow and bothbackseams. Prefilteragent boundedQ1233route has
585unhandledspans and752paidT, so no candidate; separatepruned-mask analysisnext.
Productagent owns repaired53nativeport/census and universal67append, thenproduct95.
Keepactiveproduct25source/libsimmutable; do not overwrite/restart its directory.

**03:50 active search:** root started frozen product25 at03:47:11,4processes×12
threads, source180af069... from nonce1, lowestpass only, queue mode. All gates
are accepted in receipt2c33d3e2...; independent reviewa53ced52... closes four
bookkeeping/backend findings. Selected mask560c12d5..., fusedplan1ccbbfc4...,
libdc8219ae..., originalscalar3bb230... are immutable. Exact early fallback
matches every q/b/phase and physicalMR position on a full9024packet; every
potential pass still gets protected full confirmation. Four-worker262144 timing
takes115.355s with startup, mean projection19.609h at48threads, conservative23.148h.
First checkpoint03:48:41 records188416complete rows/lowerprefix180224; no pass.
Monitor `/home/hclau/ecdsa_research/product25-operational-20261016/{passes,worker*-progress.json,search.log,search.exit}`.
Do not overwrite/restart this directory or modify selected runtime/source.
Before claiming lowestpass audit every lower JSONL disposition, then unchanged
native benchmark/final predeclared census/pre-tail identity audit. Source and
live atomic progress are preserved in checkpoint-evidence.tar.gz; full active
logs remain server-only. Keep≥100GiB available and total research≤64threads.

Product67 native/static reproduction and fixed32768 fresh gate PASS:
source268aefe2...,Q1234,102.13839±0.44367T saving,4162vs4168failed,lambda17.909
vs17.935,dirty0. Full sources/patch/census35-artifact archive verified. Active
native tree product67-native-20261016/product67/candidate retained. Agent's
universal67 append audit2×12GiB is running before maskreuse; no67nonce search.
Originalmask runtime workspace must cover max original/candidate metadata and
physical ABI must match on any futurevariant. Wide67 finalQ1556 (not earlier
checkpoint1490),60.9492T diagnostic; rootnative qualification uses2workers/source.
Wide95 ranked cycles are active; product95 waits until universal67 completes.
Repair53 recomputation and exact recursive follow-ups continue. Failure agent
has a source-defined zeroT/zeroQ frontseam extra-borrow-bit repair under proof;
both inherited lowfold cuts are preserved, no packet-selected repairs.
Public03:16 refresh remains Q678,T753771,product939347948. Best queuedcompleteT753721.

**03:17 checkpoint:** complete queued T753721/Q1468 remains best. Frozen v3
input-conditioned mask SHA560c12d5... is terminal:7,914,981nodes,33tests,
2,214inputs×8MR streams, expanded-definition audit and independent C audit pass.
The1,034-file prefilter archive2787c305... is root-verified. Original-source
disabled integration passes128/partial zero-MR comparisons and known positive
1046072871510 full9024shots;1024/16workers takes1.853312s. No nonce selected.
Only known output bits can reject; advisory flags never do. Candidate25 still
requires own Fiat binding and separate per-input transfer/phase fallback checks.
Width-adaptive C kernel120dc358... passes290.50million node/input comparisons,
27ms sparse versus56–68ms512-input work; separate disabled integration running.
Frozen v3 remains unchanged while agent investigates partial contracts in v4.
A29precision source1cd3457b... is native/fresh tested but NOT eligible:3value
repairs/0value regressions,+43.5604T,lambda18.0725>18. Full227-file archive verified.
Product agent recomputes53stages from repaired input with a new composite census
required. Phase-only boundary observer passes protected512replays and points
away from complete fold bodies. Further fixedproduct67/wide67/recursive runs
continue; preserve all declared endpoints and negative gates.

**02:55 checkpoint:** public refresh02:35 remains Q678, T753771 and product939347948.
The two queued complete Toffoli passes below remain the only new resource results.
Fixed product53 and wide43 native static ports reproduce their frozen streams,
but both32768-batch fresh failure gates fail (4133vs4120 and1393vs1391).
No nonce search follows; full sources/patches/logs archived and owned trees removed.
[Rejected qualifications](../experiments/frozen-next-20261016/STATUS.md).

Product25 remains the gate-passing58.15T/Q1234 fallback. Its independent universal
cache-equivalence audit now passes all25 stages,95801leases/219473uses, with exact
stream reconstruction. The separately stated per-input/per-bit transfer theorem
still requires a sound source-bound known-bit mask; sampled replay is insufficient.
Full-RNG reduced-value screening passes correctness but is slower in a fixed
comparison. Packed512-input and streamed-input zero-MR benchmarks are faster,
but rejection remains disabled. The next proof route is source-bound input-conditioned
dependency masks: only scored bits proved MR-free for that input may reject.
The AVX512 mask evaluator passes154.94million independent node/lane comparisons;
actual circuit export/integration is pending. Global proof, candidate transfer,
and runtime validation are separate gates. A uniform late-forward precision family
is also under structural/native admission, with failed families preserved.

**Active run, started 22:39 Singapore:** user priority is **product, Toffolis,
qubits**, in that order; submission mode **queue**. See
[`experiments/autorun-20261015-2239/LOG.md`](../experiments/autorun-20261015-2239/LOG.md)
before starting overlapping jobs. Four isolated workstreams cover the
prefilter, exact product savings, unexplained failure localization, and the
wide cache pass. **Two complete local results are queued: T753721/Q1468 and
T753745/Q1464.** Public refresh at02:35 leaves records unchanged: Q678,
T753771, product939347948. Wide15 passes the unchanged benchmark9024shots,
allchannels0; nonce644 lowest from1,731 screened. Final16384 paired census
passes670candidate versus674parent failed batches, dirty0; independent audit
confirms only the96-op identity tail changed. Full source/stream archive verified,
owned detached tree removed. [New complete result](../experiments/wide15-record-20261016/STATUS.md).

Product25 native27tests and exact generation pass. Its full32768 paired census
saves58.15368 +/-0.44249 T/Q1234;17.82724 failures per packet versus17.84445
parent, dirty0. No product nonce search: certified affordable screening remains
unresolved. A separate frozen-table source emits the identical product25 stream
in2m58s, passes4 binding tests and all protected-file checks; no resource change.
Its tree is `frozen-cache-table-20261016/candidate`. See
[candidate status](../experiments/product-exact-20261015/STATUS.md).
Search acceleration combines validated C curve preparation, exact SIMD8
simulation and SHAKE8. The integrated exact screen still projects 63–84 hours
on 64 threads at the old product failure rate, so no product search has started.
Zero-MR output slicing is faster but remains disabled for rejection: the global
RNG-independence proof is unresolved. Arithmetic predictions may prioritize an
exact check but must never directly skip a nonce.

The frozen exact census v2 at `simd-census-v2-20261016/bin/simd_census_v2`
reproduces all4096 v1 rows, protected full-state/T checks and every MR word;
4096 batches take11.54s/4workers. SHA790e9226...; full hash/ABI in its
`FREEZE.json`. Existing live jobs retain their declared runner/sample.
The local value proof certifies250 complete phase-helper clauses and547
comparators over arbitrary incoming quantum/classical/MR values, without a
clean-scratch assumption. A certified reduced value IR preserves all906156
original MR events; original transcript hash remains2a522394. Phase is excluded.
Global RNG independence is still pending; never derive packet seeds from the
reduced program or enable rejection from local proofs alone.
The first current-product +1-bit fold repair passes source admission but its
fresh failure gate fails; no nonce search. Failure work now helps local macro
RNG-independence proofs for the product prefilter.

**16 October, 00:19:** wide native21tests and unchanged benchmark pass:
**753745T/Q1464**, nonce92 lowest from1,164screened. Final paired16384-batch
census passes674candidate versus678parent failed batches,5.8004 versus5.8348
per packet, zero dirty. Candidate queued in
[`READY.md`](../experiments/autorun-20261015-2239/READY.md); no external submission.
The qualified detached tree was removed after full source/patch/stream archival.
Product fixed deep census32768batches/source passes failure gate17.83154
versus parent's17.88318, below18; exact saving14.55994 +/-0.44253T.
Frozen product may be searched only after the affordable-search gate passes.
SIMD advisory rails match262144 inputs at6.28us/shot; exact bucket scheduler
is being measured. [Wide result](../experiments/wide-record-20261015/STATUS.md).

## 1. Read in this order

1. [`AGENTS.md`](../AGENTS.md): binding project rules, including the
   **disclosed-failure-rate standard** for nonces.
2. This page.
3. [`experiments/nonce-screen-20261015/STATUS.md`](../experiments/nonce-screen-20261015/STATUS.md):
   how our official Toffoli record was made, with the screener and census.
4. [`experiments/product-tip-20261015/STATUS.md`](../experiments/product-tip-20261015/STATUS.md):
   why the product record is blocked, with search-cost figures.
5. [`docs/research-plan.md`](research-plan.md) (newest entries first) and
   [`docs/results-status.md`](results-status.md) as needed.
6. [`docs/SERVER_HANDOFF.md`](SERVER_HANDOFF.md) for server directories of
   older experiments.

To run continuously, use the cycle and backlog in
[`docs/AUTONOMOUS_PROMPT.md`](AUTONOMOUS_PROMPT.md) (paste it with `/loop`).

## 2. State of the three records

Refresh first: `.venv-research/Scripts/python.exe scripts/analyze-leaderboard.py --refresh --plot`
(writes `docs/data/latest-leaderboard.json`, `docs/frontier-results.md` and
`docs/figures/frontier.*`).

| Record | Public best (16 October 05:06 refresh) | Ours | Strict next target |
|---|---|---|---|
| Min executed Toffolis | **753,771 at Q1464 — ours** (`3f32acd2`, source `5a7c3902`) | Official | T ≤ 753,770 |
| Min Q × T | 939,347,948 = 761,222 × 1,234 (jackylee0424, `85d067da`, source `4b2ec52f`) | None | T ≤ 761,221 at Q1234; T ≤ 760,605 at Q1235 |
| Min qubits | 677 (jackylee0424, `18912d63`, source `d9d5e991`) | Local Q692 pass only, unsubmitted | Q ≤ 676 |

The user's priority (15 Oct, night): improve any of the three records, each
judged independently, in long unattended runs
([AUTONOMOUS_PROMPT.md](AUTONOMOUS_PROMPT.md)). The Q679/Q680 sources are on
the upstream branches `submissions/80fe2050-…` and `submissions/ebf0b736-…`.

## 3. Rules that shape every decision

- Only `src/point_add/` may differ in a submission. The harness, evaluator,
  simulator, curve reference, Cargo files and toolchain stay byte-identical.
- **Nonces.** Screen an identity-tail nonce only on a **frozen** circuit
  that passes the **statistical failure-rate gate** in `AGENTS.md` (16 Oct). On the same
  declared fresh inputs (one label, ≥ 32,768 batches) versus the exact stream
  of the record it beats: value failures no more than the parent's; one-sided
  exact McNemar p ≥ 0.05 on the discordant batches; ≤ 18 failed batches per
  packet; zero dirty shots. A declared gate's verdict is final; never re-judge
  or resample. Pre-declare the nonce
  policy (we use: ascending from 1, lowest pass). Never pick a nonce for its
  T, never tune circuit content to a packet, and never cut gates that trade
  correctness for T. Publish the nonce, the census and the number screened.
- Submitting is outward-facing, so ask the user first. The `ecdsafail` CLI
  is installed and authenticated on the server at
  `/home/hclau/.local/bin/ecdsafail`. Never handle or commit credentials
  (`.env` is ignored).
- README plots show only officially scored or complete locally passing
  results. Diagnostic figures stay in experiment reports.

## 4. Key facts learned (use these numbers)

| Fact | Value | Source |
|---|---|---|
| Official packet | 141 batches × 64 shots; inputs and measurement randomness come from a SHAKE256 hash of the whole op stream | `src/bin/eval_circuit.rs` |
| Pass probability on a fresh packet | (1 − f)^141, where f = census batch-failure fraction (**not** e^−λ when f is large) | census |
| Exact screener speed | Integrated bucket screener: 1,024 nonces in 38.37 s at 2 threads or 6.538 s at 16 threads on the original product source | `experiments/prefilter-20261015/STATUS.md` |
| Search cost with the integrated exact screener | Old four-stage candidate at λ17.83154: 61.9–84.4 h on an ideal 64 threads; compact eleven-stage at λ17.68094: 52.1–71.0 h. Candidate throughput and 64-thread scaling remain unmeasured | `experiments/search-cost-update-20261016/STATUS.md` |
| Product tip `4b2ec52f` | failure rate 17.69, fresh mean 761,221.70 T, packet SD of mean T 6.2 | product-tip report |
| Our official entry | failure rate 5.47 (B3: 17.73), fresh mean 753,763.5 T | nonce-screen report |
| One qubit at Q1234 is worth | about 617 T of product | 761,222 / 1,234 |
| Width-free exact cache saving | Frozen twenty-five-stage product candidate: **58.15368 ± 0.44249 T**, Q1234, 27 native tests pass; fresh census gate passes, official benchmark pending | `experiments/product-exact-20261015/STATUS.md` |
| Wider Toffoli result | Complete unchanged benchmark: **753,721 T / Q1468**, nonce644, 731 screened; queued. Earlier Q1240 diagnostic 101 T saving did not transfer directly | `experiments/wide15-record-20261016/STATUS.md` |
| Tail smoothing (walk rows 137/138) | +37 T for about −1.4 failed batches (wide circuit) | widen-walk |
| Failure anatomy | Historical wide residuals localized to forward/reverse folds and merged square windows. Current product census finds about 1.17 dropped-carry events per packet spread over 34 ticks; a one-bit repair did not improve the paired failure rate | `experiments/failure-floor-20261015/STATUS.md`, `experiments/precision-repair-20261016/STATUS.md` |

## 5. Tools (all on `smu_server` under `/home/hclau/ecdsa_research`)

Before any launch, check `uptime`, `free -g` and the top processes (two large
`python` jobs from the separate chemistry project usually use about 35 cores;
leave them alone). Use `nohup`/`setsid`, dedicated logs and PID files.
Defaults: `CARGO_BUILD_JOBS=4`, `RAYON_NUM_THREADS=1`; 32 screener or census
threads have been fine.

| Tool | Path | Usage |
|---|---|---|
| Fresh-input census | `failure-census-20261015/target/release/failure_census` | `failure_census OPS LABEL 0 4096 32 out.jsonl` → 262,144 shots in about 35 s. Failure rate = 141 × (failed batches / 4096). The same LABEL on two streams gives **paired** inputs. |
| Nonce screener | `nonce-screen-20261015/screen/target/release/nonce_screen` | `nonce_screen OPS FIRST COUNT THREADS out.jsonl` (lowest passing nonce ≥ FIRST, then a verbatim `run_tests` re-check); `nonce_screen OPS @official` replays the stream's own packet. Source: [`experiments/nonce-screen-20261015/screen`](../experiments/nonce-screen-20261015/screen). |
| Official benchmark | `./benchmark.sh` in a candidate tree | Appends a row to `results.tsv`; revert that before committing. Template: `experiments/nonce-screen-20261015/run-benchmark.sh`. |
| Stream cache rewriter (external) | `cache-idle-20261015/target/release/product_paired_diagnostic` | `CACHE_ATOM_CAP=32 CACHE_PRODUCT_CAP=200000 product_paired_diagnostic IN.bin OUT.bin`. For **measurement only**: a submission must generate the stream itself, so port the pass into `src/point_add`, as `experiments/toffoli-readiness-20261015/prepare.py` / `prepare-wide.py` do (`lazy_cache.rs` plus `ops = lazy_cache::optimize(ops);` before the nonce tail). |
| Public challenge clone | `toffoli/` (origin = Layr-Labs/ecdsafail-challenge) | `git fetch origin <sha>`, then `git worktree add ../<exp>/tip <sha>`. |
| Product tip source | public commit `4b2ec52f` | Removed from the server on 15 Oct. Recreate: `git -C toffoli fetch origin 4b2ec52fc55da796aa8f5ef851290297e8706424 && git -C toffoli worktree add --detach ../<exp>/tip 4b2ec52f`, then `cargo build --release --locked --offline --bin build_circuit` and run `build_circuit` (about 2 min) to get `ops.bin` (SHA-256 `2a522394…`). |
| Official-entry source | patch `experiments/nonce-screen-20261015/evidence/candidate-7ff2ba53.patch.gz` (also `nonce-screen-20261015/candidate-7ff2ba53.patch` on the server) | Worktree and branch removed on 15 Oct. Recreate: `git -C toffoli worktree add --detach ../<exp>/cand b3c9fdd6` and `git -C ../<exp>/cand am <patch>`. Rebuilt stream must hash to `01aad987…`. The scored copy is `5a7c3902` on the public challenge repo. |

Locally, use `.venv-research/Scripts/python.exe` (there is no `python` on
PATH). Run `scripts/test_leaderboard.py` and `scripts/test_frontier_plot.py`
after touching the data or plots.

## 6. Next steps, in priority order

1. **Lower our own Toffoli record.** The direct cache transfer was measured
   during the 22:39 run: **6.43 ± 0.75 T**, Q1468, on official source
   `5a7c3902`; it does **not** deliver the 101 T measured on B3. Its first
   census has 161 failed batches versus 159 for its fresh paired parent, so
   screening was not launched. Larger expression limits and additional exact
   public passes are being tested. See
   [wide-cache status](../experiments/wide-cache-20261015/STATUS.md).
   The original proposed recipe was: start from commit
   `7ff2ba53` (recreate it from its patch; see the tools table). Port the larger-expression cache (cache-retention 128/1,000,000,
   about −101 T, about +5 qubits; width is free for this record) into
   `src/point_add` as a final pass before the nonce tail. Then do these in order:
   1. Paired-census it against the official stream (same label) to confirm T
      and an unchanged failure rate.
   2. Freeze it and screen nonces from 1.
   3. Run `benchmark.sh` and write the report and note in the style of
      `nonce-screen-20261015`.

   The earlier expected result of about 753,670 T is **not supported by the
   measured direct transfer**. Also consider `mid2-smooth-anch2` (failure rate 4.18, but
   +4.7K T, so worse for T).
2. **Unblock the product record with a classical value-failure prefilter.**
   Model the leapfrog GCD walk (`src/point_add/leapfrog.rs`, steps table in
   `leapfrog_data/`) with the record's rail envelope. Use a fast secp256k1
   scalar multiplication (the evaluator's `curve.mul` is slow). Cost target:
   ≤ 10 µs per shot. Validate it on census failures: it must flag the tip's
   known failing inputs (the census jsonl stores k1/k2 per failing shot) with
   essentially no false passes. Run the exact screener only on prefilter
   survivors. It must not change which nonce the lowest-pass policy selects;
   the prefilter can only skip nonces that would fail anyway.
3. **Find exact width-free T savings of ≥ 12–15 T on `4b2ec52f`.** Only then
   is a product attempt worth its search: the fresh mean is 761,221.70
   against a threshold below 761,221.5, with a packet SD of 6.2.
4. **Win back failure rate cheaply** (each batch removed cuts the search
   about e-fold). The historical non-walk floor of about 1.1 batches was
   localized during this run. **23:15 update:** all 31 saved cases have observed faulty
   primitives: 17 forward Y15 folds, 12 reverse folds, two square merged
   windows. The existing addend supplies the fold correction's sign, but
   high-word propagation and clean phase repair remain unresolved. A uniform
   +4 actual Y15 window costs 1064.71 T at unchanged Q1464 and removes about
   1.14 failed batches on the **unsmoothed** parent. Do not treat its 7.68/6.54
   census rates as the official circuit's rates.
   [Verified terminal diagnosis](../experiments/failure-floor-20261015/STATUS.md).

## 7. Pitfalls already hit

- **Git hygiene (user preference):** keep only the `main` branch, locally, on
  GitHub and in the server clone. Use detached worktrees for experiments,
  save each experiment's patch under `experiments/`, and remove the worktree
  when the experiment ends. The three submodules are pinned (detached, no
  branches) and fetch only upstream `main`. About 48 older detached
  worktrees from 14–15 October remain in the server clone (`git -C toffoli
  worktree list`); check for unsaved source edits before removing any.

- **Windows shell:** the Bash tool runs Git Bash. Long heredocs inside
  `ssh '...'` can fail to parse; write files with an editor tool and `scp` them.
  Server scripts must use LF line endings.
- **Background SSH:** `nohup ... &` inside `ssh` keeps the session open; use
  `(setsid nohup ./run.sh > log 2>&1 < /dev/null &)`.
- **Dirty submodules:** `agents/qubits` and `agents/toffoli` carry uncommitted
  edits from 14–15 October that are not ours to discard. Stage only the files
  you changed.
- **Poisson shortcut:** e^−λ underestimates search cost by about 3× at a
  failure rate of 18. Use (1 − f)^141.
- **Paired T noise:** paired census T differences have a batch SD of about
  80 T, because measurement-dependent cleanup diverges. Use all 4,096 batches
  and report the standard error.
- **Scored vs diagnostic:** census means and paired savings are diagnostic.
  Only a `benchmark.sh` pass or an official evaluation is a result.

## 8. Checklist for each experiment

Create `experiments/<name>-YYYYMMDD/` with a `STATUS.md` (result first; then
method, evidence, caveats and server paths) and the launchers. Keep an
`evidence/` folder with stream SHA-256s, protected-file hashes, logs (gzip
anything large), patches and census jsonl. Keep failed runs, clearly
labelled. Update `README.md` (only for scored or complete local passes),
`docs/research-plan.md` (newest entry on top), `docs/results-status.md` and
this page.
