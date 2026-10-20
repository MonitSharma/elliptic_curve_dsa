from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-groups-context-final-gate-20261020';r=a.parent/'breakthrough-public-best-drop-final-gate-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
s=(old/'census.py').read_text().replace('32768','131072').replace('2097152','8388608');ast.parse(s);(r/'census.py').write_text(s)
s='''import hashlib,json,re,struct,subprocess,urllib.request
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;c=ws/'breakthrough-public-best-drop-finished-20261020';t=c/'candidate';dev=ws/'breakthrough-public-best-drop-development-20261020';parentdir=ws/'breakthrough-public-acd0-reproduction-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert not(r/'GATE-DECLARATION.json').exists();assert(c/'run.exit').read_text().strip()=='0'and(dev/'controller.exit').read_text().strip()=='0';f=json.loads((c/'SOURCE-FREEZE.json').read_text());a=json.loads((c/'RESULT.json').read_text());assert len(f['source_files'])==177 and len(f['protected_files'])==17 and a['native_tests']==1 and a['independent_proof_controls']==9 and a['qubits']==1233;assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());assert sha(c/'SOURCE-FREEZE.json')==a['source_freeze_sha256'];assert f['identity_nonce']==0 and re.search(rb'IDENTITY_NONCE:u64=0;', (t/'src/point_add/public_best_drop_cache.rs').read_bytes());stream=t/'ops.bin';assert sha(stream)==a['stream_sha256']
# Independently check every identity-tail operand. Public prototypes retained
# the historical recipe nonce; the finished wrapper must normalize it to zero.
tail=b'';position=0
with stream.open('rb',buffering=0)as raw:
 header=raw.read(16);assert header[:8]==b'QECCOPSZ';count=int.from_bytes(header[8:],'little');child=subprocess.Popen(['zstd','-dc'],stdin=raw,stdout=subprocess.PIPE)
 while block:=child.stdout.read(1<<20):tail=(tail+block)[-96*56:];position+=len(block)
 assert child.wait()==0 and position==count*56
no=(1<<64)-1;rows=list(struct.iter_unpack('<7Q',tail));assert len(rows)==96 and all(row==(6,no,no,0,no,no,no)for row in rows),'Finished nonce-zero tail must be literal and independently checked';(r/'TAIL-ZERO-VERIFICATION.json').write_text(json.dumps({'status':'ALL96_LITERAL_ZERO_NONCE_IDENTITY_OPERATIONS_VERIFIED','stream_sha256':sha(stream),'tail_sha256':hashlib.sha256(tail).hexdigest()},indent=2)+'\\n')
di=json.loads((dev/'DIAGNOSTIC.json').read_text());co=di['comparisons']['bestdrop'];assert di['summaries']['bestdrop']['dirty_shots']==0 and not co['different_other_lanes'];delta=co['candidate_minus_parent_raw_toffoli'];upper=(756265+delta+2*co['paired_standard_error']+6)*1233
if upper>=933231010:
 (r/'NOT-DECLARED-RESOURCE-NOT-COMPETITIVE.json').write_text(json.dumps({'status':'NO_GATE_DECLARED_RESOURCE_CHECK','diagnostic_parent_relative_delta':delta,'conservative_product_estimate':upper,'scope':'Development estimate only, not a benchmark score. No final census/nonce ran.'},indent=2)+'\\n');raise SystemExit('Development does not give adequate current-product margin; no finalgate declared')
sid='acd0d88e-7445-4430-ba59-3c24c9bf4e0f';api='https://api.ecdsa.fail/api'
def fetch(path):
 with urllib.request.urlopen(api+path,timeout=60)as response:return json.load(response)
public_parent=fetch('/submissions/'+sid);s=public_parent['submission'];assert s['officialMetrics']=={'qubits':1234,'toffoli':756265}and s['officialScore']==933231010 and s['submissionCommitSha']=='7499c902d7989e5a995ccd2331104a532197851b';(r/'PARENT-STATUS-LAST.json').write_text(json.dumps(public_parent,indent=2)+'\\n');receipt=parentdir/'PUBLIC-SOURCE-VERIFICATION.json';pr=json.loads(receipt.read_text());assert pr['status']=='EVERY_PUBLIC_SOURCE_AND_PROTECTED_BYTE_MATCHES_GIT_OBJECTS'and pr['public_submission']==sid and pr['public_source_revision']==s['submissionCommitSha']and pr['source_files']==175 and pr['protected_files']==17;pf=json.loads((parentdir/'SOURCE-FREEZE.json').read_text());assert all(sha(parentdir/'parent'/p)==h for p,h in{**pf['source_files'],**pf['protected_files']}.items());parentstream=Path(pr['stream']);assert sha(parentstream)==pr['stream_sha256']=='3d7c94f1dea887dd2d4ff13326e350756350cc1044d396444c3f820f8bfad827'
snapshot=fetch('/benchmarks/1ffb695a-309b-46b6-a728-2f97d8c7be74/submissions');eligible=[x for x in snapshot['submissions']if x.get('officialMetrics')and(x['status']=='accepted'or x['status']=='rejected'and x.get('rejectionReason')=='score did not improve current best')and x.get('officialScore')==x['officialMetrics']['qubits']*x['officialMetrics']['toffoli']];parent=min(eligible,key=lambda x:x['officialScore']);fields=['id','officialScore','officialMetrics','submissionCommitSha'];public={'at_utc':datetime.now(timezone.utc).isoformat(),'leaders':{'product':{k:parent[k]for k in fields},'toffoli':{k:min(eligible,key=lambda x:x['officialMetrics']['toffoli'])[k]for k in fields},'qubits':{k:min(eligible,key=lambda x:x['officialMetrics']['qubits'])[k]for k in fields}}}
if parent['id']!=sid:
 (r/'NOT-DECLARED-PUBLIC-PARENT-CHANGED.json').write_text(json.dumps(public,indent=2)+'\\n');raise SystemExit('Current publicproduct parent changed before declaration; no gate verdict exists')
assert parent['submissionCommitSha']==pr['public_source_revision'];(r/'PUBLIC-RECORDS.json').write_text(json.dumps(public,indent=2)+'\\n');exe=ws/'simd-census-v2-20261016/bin/simd_census_v2';assert sha(exe)=='790e92266ea67ec54ef701b2deed76fe8d0b766b411ca9eab877f82ae2c11a66';deps=json.loads((ws/'breakthrough-output-audit-20261020/TOOL-SOURCE-FREEZE-v2.json').read_text())['protected_dependency_files'];assert all(sha(Path(p))==h for p,h in deps.items())
d={'declared_at_utc':datetime.now(timezone.utc).isoformat(),'label':'public-best-drop-product-final-20261020-v1','batches':131072,'shots_per_batch':64,'shots_per_source':8388608,'first_batch':0,'workers_per_source':8,'protected_scalar_batches_per_source':8,'candidate_root':str(t),'candidate_source_freeze':str(c/'SOURCE-FREEZE.json'),'candidate_source_freeze_sha256':sha(c/'SOURCE-FREEZE.json'),'candidate_stream':str(stream),'candidate_stream_sha256':sha(stream),'candidate_qubits_from_protected_analyzer':1233,'identity_nonce':0,'parent_record':public['leaders']['product'],'public_refresh_at_utc':public['at_utc'],'public_records_sha256':sha(r/'PUBLIC-RECORDS.json'),'parent_source_receipt_sha256':sha(receipt),'parent_stream':str(parentstream),'parent_stream_sha256':sha(parentstream),'census_binary':str(exe),'census_binary_sha256':sha(exe),'protected_dependency_files':deps,'development_plan_sha256':sha(dev/'PLAN.json'),'development_result_sha256':sha(dev/'DIAGNOSTIC.json'),'tail_zero_verification_sha256':sha(r/'TAIL-ZERO-VERIFICATION.json'),'criteria':{'candidate_value_failing_shots_no_more_than_parent':True,'one_sided_exact_mcnemar_p_minimum':0.05,'failed_batches_per_9024_shot_packet_maximum':18,'packet_batches':141,'dirty_ancilla_shots':0},'verdict_policy':'Sole finalgate for this frozen statically selected exact carry-schedule/cache source. Fixed131072batches declared before census. Outcome final: no relabel, rerun, extension or nonce to reverse a failure. All profile/cache choices frozen before development. No prior gate verdict is reused.','scope':f['scope']};(r/'GATE-DECLARATION.json').write_text(json.dumps(d,indent=2)+'\\n');print(json.dumps({'label':d['label'],'declared_at_utc':d['declared_at_utc'],'batches':d['batches'],'declaration_sha256':sha(r/'GATE-DECLARATION.json'),'candidate_stream_sha256':sha(stream),'exact_parent':sid,'parent_stream_sha256':sha(parentstream)}),flush=True)
''';ast.parse(s);(r/'declare.py').write_text(s)
s=(old/'run.py').read_text().replace('breakthrough-groups-context-finished-20261020','breakthrough-public-best-drop-finished-20261020').replace('breakthrough-groups-context-development-20261020','breakthrough-public-best-drop-development-20261020').replace("d/'DEVELOPMENT-CONTROLLER.exit'","d/'controller.exit'").replace('<7200','<14400');ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Sole prospective final product gate, frozen before its fresh census

Queue only after final best-drop source/full-output development completes.
Verify177source/17protected bytes, runtime/proof controls, exact publicacd0
source/stream, actualQ1233 and independently decode every final96 identity op
as literal noncezero. Public research prototypes retained historical1052246623534;
the finished wrapper checks/removes it and must append zero before this gate.

Require development resource margin (parent-relative actualT,2SE plus6T packet
reserve) before declaration; otherwise preserve no-gate status. Refresh exact
current publicproduct parent before declaration and stop if changed, without
creating a gate verdict. Fresh labelpublic-best-drop-product-final-20261020-v1,
131072batchesx64 =8388608shots/source, eightworkers/eightprotectedscalarbatches
per source, paired identical fresh inputs, all four userstatistical criteria.
This label/count is fixed and written before census. A declared result is final;
never rerun/relabel/extend or use a nonce to reverse failure. No nonce/benchmark
is authorized by this controller until the actual gate verdict is PASS.
''');print(r)
