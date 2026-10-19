"""Record research progress; stage document additions independently of user edits."""
import difflib,hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
root=Path(__file__).resolve().parents[2];r=Path(__file__).resolve().parent
stamp=datetime.now(timezone.utc).isoformat()
reports={
'breakthrough-assessment-20261020':'''# Structural breakthrough assessment

Research targets only; no new scored result. Baseline official d9ae2845 is
Q1234/T761077/product939169018. Fresh immutable public snapshots retain the
same three record holders (product939169018, width675, Toffolis752991 atQ1863).
TARGETS.json contains illustrative sub800million products, not forecasts.
Raw public snapshots are preserved in their .json.gz files with SHA256 manifests.

history-model.py compares independent bit-logic and valuation descriptions of
a generic full-precision macro-step on786432 cases. All agree. Inverse-fiber
witnesses32/28/32 refute a simple four-bit codec for that generic interface.
They do not bound the seeded circuit or different arithmetic representations.

forced-walk-model.py compares one-bit forced blocks with a generic adaptive
walk on4096 fixed labelled field inputs per variant and504 small supported
prime inputs. A one-bit step does not materially shorten total transcript in
this model. The initial small-prime seed-admission failure is separately
preserved; the corrected controls use only primes congruent3 mod4.

Primary literature context is linked in LITERATURE.json. It does not establish
novelty or directly comparable complete resource results for these prototypes.
''',
'breakthrough-profile-20261020':'''# Accepted-source cost and live-workspace audit

Completed observation-only audit; no new candidate or score. The observer's
entire compressed stream exactly matches official d9ae2845:
125deb3a03b460ec991df012e6aa8e6a6b67fc96ffc525a165b5ca3e67282501.
All17 protected files are unchanged. Three phase-mapper controls and two replay
controls pass;8 fresh batches match every protected scalar quantum/classical
wire, phase, RNG draw and executed-Toffoli count. All512 diagnostic rows match
the unchanged original replay binary exactly, including failing inputs.

On512x64 fresh labelled shots, measured mean executed costs are division
358252.50 (47.07%), multiplication362703.79 (47.66%), square39491.01 (5.19%).
These diagnostic means are not submitted scores. Every regional sum equals
the exact total. There are62 value-failing shots,38 phase-failing shots and
zero dirty shots in this baseline sample; it is not a final statistical gate.

The first build-time peak is1234 in division. Its nine owner groups include
206 decision-history qubits and134 carry qubits. This is ownership evidence,
not a lower bound or a reduced-width implementation. WORKSPACE-OWNERS.json
and EXECUTED-COST-PROFILE.json retain the exact breakdown.

The65-member evidence.tar.gz and every included file hash were verified
locally. Full operation streams remain server-retained with hashes. Runtime,
source patch, added source, tests and original replay comparison are bound in
the archive. Raw server process arguments were excluded from public evidence.
''',
'breakthrough-cap-cost-20261020':'''# Raw-arithmetic capacity admission study

Negative admission result; no reduced-width circuit or scored result.
The predeclared capacities were1234,1200,1168,1136,1104. Raw cap1234 exactly
matches every serialized operation byte of the admitted baseline prepass.
All four smaller settings fail native generation because pinned payload-fold
and carry ladders do not have enough scratch. For example cap1200 reaches
forward tick97 with room14 where39 is required; cap1168 fails a forward fold
with budget6 and active1164. No failing generation is a resource result.

Original failed admissions are preserved: the first compared differing zstd
framing, and the second reader passed a buffered file descriptor at the wrong
offset. The corrected unbuffered reader proves identical header and all
630743288 decompressed bytes without regenerating the baseline or changing
source. These are diagnostic tooling repairs, not statistical gate reruns.
All17 protected files remain unchanged. The51-member evidence archive has
been verified locally. Full baseline stream remains on the research server.
''',
'breakthrough-cofactor-history-20261020':'''# Integer-cofactor history reconstruction component

Positive mathematical and native component result; no complete point-addition
circuit, width reduction, statistical gate, nonce search or scored record.
For C divisible8,D odd, q=7-2s0-4s1-8s3 and e=3+k1+2k2, define
Cnew=C+qD,Dnew=2^eD. The two forced signs follow from low cofactor bits; the
two exponent flags follow from the2-adic valuation of Dnew. Thus four flags
can be reversibly erased while retaining s3. The first macro-step is exceptional.

Unbounded-integer solver checks:13 UNSAT domain queries, plus a SAT negative
control showing why the first-step admission is necessary. Native codec:
14 Toffolis, at most3 clean scratch, zero measurements or phase gates. Three
native tests pass: all128 quantum lookup cases,3072 signed coefficient residue
cases with exact inverse, and an incorrect-history dirty-flag negative control.
The initial test-helper generic-type compile failure is preserved separately;
the passing v2 changes only that helper type and leaves primitive gates intact.

The4096-field-input integer model and67584 decoder controls pass determinant,
modular-scaling and inverse checks. Model history averages128 bits versus621
for five-bit records. These are model dimensions, not physical resources:
cofactors grow, and observed maxima must not become allocation cuts.
bounds-study.py enumerates all inputs of11 small primes and4096 field inputs
per rule. Neither the generic nor minimum-next-target rule gives a constant
multiple-of-p cofactor bound; growth remains a serious allocation issue.

The28-member native evidence archive is locally verified. SMT/model evidence
is preserved alongside it. Complete coefficient bounds, endpoint handling,
final power-of-two normalization, multiplication and cleanup remain unimplemented.
''',
'breakthrough-cofactor-update-20261020':'''# Native signed cofactor update and inverse

Positive arithmetic component; no point-add integration or resource record.
Implements Cnew=C+(7-2s0-4s1-8s3)D, variable sign-aware scaling Dnew=2^eD,
four-flag erasure and explicit inverse. Uses the existing phase-correct Gidney
carry ladder through a diagnostic wrapper. Protected17 files remain unchanged.

Six native controls pass: the three history-codec controls,131072 exhaustive
eight-bit signed-adder inputs,1792 signed sixteen-bit edge/wrap cases with
inverse, and every physical measurement-phase coefficient on64 basis states.
The phase probe checks that random outcomes only control single phase gates;
therefore its one-hot probes cover the linear phase coefficients for those
bases, including reset draws. At16-bit word size, a forward component emits
93 Toffolis including scaling and history cleanup. This is a component count,
not an extrapolated scored result. Integer use requires a proved coefficient
bound and excludes overflowing source shifts; target-word wrap is tested.

The18-member native evidence archive has been locally verified. The code is
not part of the accepted circuit. Fixed allocation, GCD endpoint, variable
normalization and complete multiply/cleanup budget remain unresolved.
''',
'breakthrough-subphase-20261020':'''# Raw arithmetic rail and payload cost attribution

Diagnostic observer in progress. Base90e777ea; raw cap1234 must reproduce
native stream13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b
exactly. Observe pmark/pacc spans without moving operations; reject any static
cost-key collision crossing a scored gate. A fresh512x64 replay, with8 complete
protected scalar controls, will measure the partition using the previously
verified kernel. No candidate, final gate, nonce or score is declared.

Initial compile failed on a const HashMap initializer. The failed source,
manifest and log are preserved; repair-v2 uses runtime thread-local
initialization and retains the full-stream equivalence requirement.
Active server supervisor2311292; authoritative exit marker run-v2.exit.
'''}
for name,text in reports.items():(root/'experiments'/name/'STATUS.md').write_text(text,encoding='utf-8',newline='\n')
prefix='''## 20 October 2026, 05:59 SGT: structural research checkpoint

No new complete point-add result. Official d9ae2845 remains the public product
leader at Q1234/T761077/product939169018 on the fresh1684-submission snapshot.
The accepted circuit and every earlier final gate verdict remain unchanged.

The source-identical baseline audit is complete: division47.07% and
multiplication47.66% of actual executed Toffolis; all512 diagnostic rows agree
exactly with the original replay. First-peak ownership includes206 history
and134 carry qubits. All65 archived members verify locally. Lower raw
capacities1200/1168/1136/1104 fail generation; their51-member evidence and
initial tooling failures are preserved. None of these is a scored improvement.

An integer adjoint-cofactor interface now has13 unbounded decoder proofs and
a native14-Toffoli four-flag eraser. Its full bounded-word signed update,
variable shift and inverse pass6 native tests, including131072 exhaustive
adder inputs and measurement-phase controls. This is a component only:
cofactor growth and final normalization may consume the apparent saving.
Never use model maxima as new allocation cuts. Native28/18-member archives
are verified locally; the initial compile failure is preserved.

Active next step: breakthrough-subphase-20261020 repair-v2 under2311292,
source-preserving raw rail/payload attribution. Check run-v2.exit, do not
restart an observation timeout. Then compare the complete mandatory cofactor
cost (proved width, endpoint, normalization, multiplication and cleanup) with
the measured payload budget. Derive a real allocation bound or pivot; no
candidate/gate/nonce is authorized by component success. New submissions queue.

Run log: experiments/autorun-20261020-breakthrough/LOG.md. Detailed status and
evidence: breakthrough-profile-, breakthrough-cap-cost-,
breakthrough-cofactor-history-, breakthrough-cofactor-update-20261020.
Preserve pre-existing user edits, Q692, and every failed or frozen experiment.

'''
patch=[]
for name in['docs/research-plan.md','docs/results-status.md','docs/AGENT_HANDOFF.md']:
 p=root/name;head=subprocess.check_output(['git','show','HEAD:'+name],cwd=root).decode();first,rest=head.split('\n',1)
 updated=first+'\n\n'+prefix+rest.lstrip('\n')
 patch.extend(difflib.unified_diff(head.splitlines(keepends=True),updated.splitlines(keepends=True),fromfile='a/'+name,tofile='b/'+name))
 b=p.read_bytes();first,rest=b.split(b'\n',1);ending=b'\r\n'if first.endswith(b'\r')else b'\n'
 if rest.startswith(ending):rest=rest[len(ending):]
 p.write_bytes(first+b'\n'+ending+prefix.encode().replace(b'\n',ending)+rest)
(r/'checkpoint-index.patch').write_text(''.join(patch),encoding='utf-8',newline='\n')
with(r/'LOG.md').open('a',encoding='utf-8')as f:f.write(f'\n- {stamp}: checkpoint saved; native cofactor update6 tests PASS. All baseline65, cap51, codec28, update18 evidence members independently verified locally. Raw subphase observer v2 supervisor2311292 remains active; original compile failure retained. No final census or nonce or new score. Next: full mandatory-cost and universal coefficient-bound audit.\n')
print('Checkpoint and additive documentation patch prepared; existing user bodies retained.')
