from pathlib import Path
import ast
root=Path(__file__).resolve().parents[2];ex=root/'experiments';old=ex/'breakthrough-native-context-final-20261020';r=ex/'breakthrough-groups-context-final-20261020'
s=(old/'seal.py').read_text();s=s[:s.index("parent=g['summaries']['parent'];")]
for a,b in {'breakthrough-native-context-finished-v3-20261020':'breakthrough-groups-context-finished-20261020','breakthrough-native-context-final-gate-20261020':'breakthrough-groups-context-final-gate-20261020','breakthrough-native-context-nonce-20261020':'breakthrough-groups-context-nonce-20261020','native-context499-exact-final-20261020-v1':'groups-context230-final-20261020-v1','==201':'==205',"'source_files':201":"'source_files':205",'Cache499 independently exact contextual products on officialT748691 at nonce':'Cache230 independently exact contextual products on officialT747453 at nonce','Complete unchanged benchmark of499 independently exactcontext product leases on officialT748691;16 extra donor wires for independentT objective. Fresh public minimum checked before upload; no globalproduct claim.':'Complete unchanged benchmark of230 independently exact contextual product leases on officialT747453; actualQ1464 unchanged. Fresh publicminimum checked before upload; no globalproduct claim.'}.items():s=s.replace(a,b)
line=next(x for x in s.splitlines()if x.startswith('changed=git('));s=s.replace(line,"changed=git('diff','--cached','--name-only').decode().splitlines();assert changed and all(p.startswith('src/point_add/')for p in changed);expected=[]\nfor p,h in f['source_files'].items():\n prior=subprocess.run(['git','-C',str(t),'show',f['base']+':'+p],capture_output=True)\n if prior.returncode or hashlib.sha256(prior.stdout).hexdigest()!=h:expected.append(p)\nassert sorted(changed)==sorted(expected);git('commit','-q','-m',f'Cache230 independently exact contextual products on officialT747453 at nonce{k}')")
s+='''
proof=ws/'breakthrough-groups-safe-context16-20261020';proof0=ws/'breakthrough-groups-safe-context0-20261020';development=ws/'breakthrough-groups-context-development-20261020';component=json.loads((proof/'RESULT.json').read_text());component0=json.loads((proof0/'RESULT.json').read_text());pd=json.loads((development/'DIAGNOSTIC.json').read_text());pc=pd['comparisons']['context230'];a=json.loads((research/'RESULT.json').read_text());parent=g['summaries']['parent'];candidate=g['summaries']['candidate']
assert component['native_controls']==component0['native_controls']==9 and component['leases']==component0['leases']==230 and component['output_qubits']==component0['output_qubits']==1464 and component['max_donor']==1460
assert component['output_stream_sha256']==component0['output_stream_sha256'];assert a['native_tests']==1 and a['independent_proof_controls']==9 and b['qubits']==1464 and b['rounded_mean_executed_toffoli']<747453
assert not pc['different_target_lanes'] and not pc['different_other_lanes'] and not pc['new_value_failing_shots'] and not pc['new_value_passing_shots']
note=f"""Model: GPT-6 sol
Harness: Codex

# 230 independently exact context caches on official grouped square: Q{b['qubits']} / T{b['rounded_mean_executed_toffoli']}

The complete unchanged official benchmark rebuilds this frozen source and passes
all9,024 shots at {b['qubits']} peak logical qubits and
{b['rounded_mean_executed_toffoli']} rounded mean executed Toffolis. Exact mean
{b['mean_executed_toffoli']}; total executed Toffolis {b['total_executed_toffoli']};
product {b['product']}. This improves the independent current officialT minimum
747453 by {747453-b['rounded_mean_executed_toffoli']} rounded Toffolis at unchanged
Q1464. Complete locally passing benchmark measurements are pending official
evaluation. The separate global product record is lower; no globalproduct or
width record is claimed. Structural counts and census means are diagnostics.

## Exact code predecessor and protected source lineage

The direct code predecessor and exact current statistical comparison parent is
8d0fef2b-a7f6-40a7-9b3c-f800073cf2c5, public source
d289ee2bbde583508993f8beb895a4ec3e2ae26c, byte-verified local source
ab071cf30e06178dc91a1919f366a6823f37846c. All204 parent point-add files and17
protected files were compared with official Git objects. Its exact complete
selected stream is ccdef4d636680d5d3be83169760a223278662e4f38b9efff2fb3cc6a58dff5bb.
The whole parent constructor and every existing bound pass remain unchanged,
except its entrypoint is renamed so the new source wrapper can call it. The
source retains strengthened uniform+2 comparisons, public140 schedule, plain
pool, global1536/square1408, exact native rail strip/G6 fold erase and grouped
square with28-bit witnesses, full259-bit corrections, exact capped splits and
depth8 inverseleaf. Existing approximations elsewhere remain and are disclosed;
this is not a universally correct full arithmetic claim.

The native square/leaf technique derives from acd0d88e/source7499c902; the exact
rail/G6 components from e3b5c51f/source88869 via our officiald182a53e. Stronger
comparisons/public140/square1408 descend from a4ee760a. Their original source
notices/credits are retained and dependencies are listed. The context-cache
method follows our prior official260b3ba0 and38a686dd, with wholly new proofs
and rows on this exact new parent. No old index table, packet, gate or nonce is
transported. No arithmetic precision, approximation window, witness length,
cut, round or schedule is retuned. No packet-specific circuit content is used.

## Independent exact contextual proof and native controls

Before any new point-addition sampling, two fixed scans use zero and16 permitted
extra donors on the same complete parent stream, each with16,384-operation earlier
cuts in the same enclosing lexical classical guard scope. Both independently
prove the SAME230 leases and emit byte-identical complete output streams. Actual
peak width remains1464 and max donor1460: all selected donor wires already exist;
none of the16 additionally permitted wires is used. Both scans nominate1154
pairs, prove230 and reject924. The selected16-budget scan is preserved alongside
the equivalent zero-budget control; no selection depends on correctness packets.

Fingerprints nominate candidates only. Exact symbolic Boolean XOR/AND algebra
on the original operations must prove equality of effective endpoint products
for arbitrary cut values and arbitrary measurement/classical values. For an
existing donor not already reset-clean, a separate exact symbolic expression
must prove its value identicallyzero at the first endpoint. Cleanliness is not
inferred from fingerprints. No-touch intervals, disjoint holds and lexicalscope
constraints are enforced. When an outer guard is false, both original endpoints
and all new donor operations are skipped, preserving the false-world value.
At the first endpoint the product is computed once into the donor and copied to
the original target; at the second it is copied, X-measured and erased with the
exact matching guarded CZ repair. Every added operation and phase correction is
emitted and charged. There is no external loader or uncounted quantum resource.

Both scans pass nine independent native controls before searching: exhaustive
small-basis value/phase tests, classicalguard capture/mutation, unknown per-op
conditions, arbitrary prepared aliases, rejected broken aliases and forbidden
scope crossing; new donorzero controls require a reset and all cancellations,
reject a missing reset/unmatched X, and detect an omitted phase repair. The
finished source repeats its own full-basis guarded cache/fault test (one test,
PASS). Its inherited grouped-square/rail/G6 native controls and source are
unchanged. The inherited square caller-contract unit excludes six historical
walk-domain edge inputs from value/phase assertions; that limitation and their
diagnostics are retained in the parent disclosures, with no universal claim.

The finished groups_context_cache wrapper binds EVERY complete parent canonical
record, validates/removes its historical nonce282 identity tail, binds the
remaining prefix, runs the literal independently tested exact proof rewrite
body with newly proven rows, binds EVERY new output prefix record, and appends
a fresh nonce0 tail. No additional generic simplification is run. Proof source,
rows, literal rewritebody, parent prefix and new complete prefix hashes are in
the source freeze; source/code is self-contained.205 point-add files,17 protected
files, and all records are frozen before fresh development and finalgate inputs.

## Fresh complete-output development

Label {pd['label']},512x64/source, fourworkers/source, eightprotected scalar
batches/source. Parent and candidate full value/phase/dirty summaries and every
target/other quantum-lane difference are retained. Parent values
{pd['summaries']['public8d']['value_shots']}, candidate values
{pd['summaries']['context230']['value_shots']}; dirty0 in both. Target differences0,
other-lane differences0, new wrong-value or newly passing shot IDs0. The frozen
candidate is not changed after these inputs. A new independent finalgate follows.

## Sole final failure-rate gate, never rerun

Label {g['label']}; declared {d['declared_at_utc']} BEFORE sampling, nonce0.
32,768 batches of64 shared fresh inputs=2,097,152 shots per source, eightworkers
and eightprotectedscalar batches/source. Exact then-current public parent8d,
its source/stream and the public minimum are refreshed before declaration.
Candidate sourcefreeze SHA256 {g['candidate_source_freeze_sha256']}.
Declaration SHA256 {sha(gate/'GATE-DECLARATION.json')}.
Result SHA256 {sha(gate/'GATE-RESULT.json')}.

Parent wrong-value shots {parent['value_shots']}; candidate {candidate['value_shots']}.
Newly wrong-value shots {g['new_value_failing_shots']}, newly passing
{g['new_value_passing_shots']}; same value-failure IDs:
{g['value_failing_shot_identities_equal']}. Parent phase shots
{parent['phase_shots']}, candidate {candidate['phase_shots']}; dirty ancilla0/0.
Failed batches {parent['failed_batches']} parent/{candidate['failed_batches']}
candidate; candidate failed batches per9,024-shot packet
{candidate['failed_batches_per_9024_packet']}. Discordant batches newly failing
b={g['newly_failing_batches_b']}, newly passing c={g['newly_passing_batches_c']}.
One-sided exact McNemar P(X>=b|Binomial(b+c,1/2))=
{g['one_sided_exact_mcnemar_p']}. All four declared criteria PASS: no more wrong
values, paired p>=.05, at most18 failed batches per packet, zero dirty ancilla.
The verdict is final, with no relabel, extension, resampling or nonce change to
reverse a failure. Diagnostic paired executedT difference
{g['candidate_minus_parent_mean_executed_toffoli']}, SE{g['paired_standard_error']}.
No earlier source's census or verdict is reused.

## Qualified ascending nonce, complete benchmark, publication

Only after the fixednonce0source passed its own gate, the exact full-state/RNG
screen engine and protected libraries are independently hash-verified and
requalified on this stream. Eight additional partial-packet controls1..8 repeat
production;24 protected full qubit/classical/phase/RNG/curve batches at0,70,140
are checked. No approximate arithmetic prefilter. Production screens ascending
1..{sr['highest_screened']}, total{len(rows)}; lowest full passing nonce{k},
passes{passes}, completed overrun{k+1}..{sr['highest_screened']} all disclosed.
Never select by Toffoli count. Selectednonce separately passes a full protected
9,024-attempt packet replay. Final source changes only IDENTITY_NONCE0->{k}.
Every pre-tail byte equals the gated stream; all96 identitytail records match.

The unchanged challenge benchmark rebuilds this final source, all9,024 shots
PASS:0 classical mismatches,0 phase-garbage batches,0 ancilla-garbage batches.
All17 harness/scorer/simulator/curve/Cargo/toolchain/history files byte-identical;
historical results restored after benchmark output saved separately. Only
src/point_add changes committed. Final source revision{revision}.
Source archive SHA256{review['source_archive_sha256']}.
Patch SHA256{review['source_patch_sha256']}.
Selectedstream SHA256{b['native_receipt']['stream_sha256']}.
Canonicalrecords SHA256{b['native_receipt']['records_sha256']}.
Pre-tail SHA256{b['native_receipt']['pre_tail_sha256']}.

Complete source, exactproof tool/rows/native/fault controls, both fixed scans,
fresh development, sole declared census with allrows, all nonce screens/controls,
benchmark logs and hashes are retained. Every archive/source member is independently
checked locally before upload. Public records are refreshed immediately before
automatic submission. Finite packet success is not universal correctness or an
independent-novelty claim. Research attribution MonitSharma; modelGPT-6 sol;
coding harnessCodex. The globalproduct research goal remains separate and active.
"""
assert len(note)>6000;(r/'SUBMISSION-NOTE.md').write_text(note)
save('DEPENDENCIES.json',[{'submissionId':'8d0fef2b-a7f6-40a7-9b3c-f800073cf2c5','rationale':'Direct entire code/source predecessor and exact currentT statistical comparator; no arithmetic change.','evidence':d['parent_stream_sha256']},{'submissionId':'38a686dd-a2b1-4bdc-899e-81a389d36fd5','rationale':'Earlier contextproduct-cache technique;230proof rows regenerated independently on newgrouped source.','evidence':'e3d3f05e6c114f9a644f7ced2588ee65e3072bde'},{'submissionId':'260b3ba0-d604-4f0d-9d55-934055d216b4','rationale':'Original earliercontext exactproductcache technique.','evidence':'af60c815cf7fcb927466450864cd30b03483c74c'},{'submissionId':'acd0d88e-7445-4430-ba59-3c24c9bf4e0f','rationale':'Inherited grouped-square/inverseleaf native code with stronger28bit/full259/exactsplits.','evidence':'7499c902d7989e5a995ccd2331104a532197851b'},{'submissionId':'d182a53e-be3d-4119-8298-303a9a9de07a','rationale':'Inherited strengthened native rail/G6 circuit predecessor.','evidence':'fb2d03e8a70a8b69965710ef46c5cdce828e9ca2'},{'submissionId':'a4ee760a-0500-4d54-9822-4a3c56806fd5','rationale':'Inherited strengthened comparisons/public140/square1408 arithmetic.','evidence':'be2902c2a133754968dbc97992c753cc08730e83'},{'submissionId':'e3b5c51f-74e6-480a-82bf-5543fb1ba555','rationale':'Inherited exact native rail/G6 components.','evidence':'88869d8cc23fb72120dd52533f3e48277e9b36e4'}])
files={};streams={}
for prefix,directory in [('',r),('gate',gate),('search',search),('finished',research),('proof16',proof),('proof0',proof0),('development',development)]:
 for p in directory.iterdir():
  if p.is_file() and 'resource-preflight' not in p.name and p.name not in ['evidence.tar.gz','final-evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','source-review.log','review.log']:
   name=(prefix+'/' if prefix else '')+p.name
   if p.name.endswith('ops.bin'):streams[name]=sha(p)
   else:files[name]=p
for prefix,directory in [('proof16-tool',proof),('proof0-tool',proof0)]:
 pf=json.loads((directory/'SOURCE-FREEZE.json').read_text());assert all(sha(directory/'tool'/p)==h for p,h in pf['tool_source_files'].items())
 for p in pf['tool_source_files']:files[prefix+'/'+p]=directory/'tool'/p
for n in ['PUBLIC-SOURCE-VERIFICATION.json','SOURCE-FREEZE.json','SUBMISSION-NOTE.md','BENCHMARK-RESULT.json','PACKAGE-RESULT.json']:files['parent/'+n]=ws/'breakthrough-groups-safe-final-20261020'/n
save('EVIDENCE-MANIFEST.json',{'files':{n:sha(p)for n,p in files.items()},'streams_retained_on_server':streams,'scope':'Complete205-source, exact230contextzero proofs/native controls, two fixedwidthproof scans, fresh development/sole finalgate, qualifiednonce/all screens, unchangedcompletebenchmark. No credentials or process listings. Parent archive remains linked immutable provenance.'})
with tarfile.open(r/'final-evidence.tar.gz','w:gz')as archive:
 for n,p in sorted(files.items()):archive.add(p,arcname=n,recursive=False)
 archive.add(r/'EVIDENCE-MANIFEST.json',arcname='EVIDENCE-MANIFEST.json',recursive=False)
save('PACKAGE-RESULT.json',{'archive_sha256':sha(r/'final-evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')});print(json.dumps(review),flush=True)
'''
ast.parse(s);(r/'seal.py').write_text(s);(r/'review.py').write_bytes((old/'review.py').read_bytes())
s=(old/'submit.py').read_text().replace('d182a53e-be3d-4119-8298-303a9a9de07a','8d0fef2b-a7f6-40a7-9b3c-f800073cf2c5').replace("'source_files':201","'source_files':205");ast.parse(s);(r/'submit.py').write_text(s)
s=(Path(__file__).parent/'collect-native-context-final.py').read_text().replace('breakthrough-native-context-final-20261020','breakthrough-groups-context-final-20261020').replace('==201','==205').replace("'source_files':201","'source_files':205").replace('evidence,201 source','evidence,205 source');ast.parse(s);(Path(__file__).parent/'collect-groups-context-final.py').write_text(s);print(r)
