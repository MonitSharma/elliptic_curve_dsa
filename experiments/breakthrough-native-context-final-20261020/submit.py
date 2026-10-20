"""Submit once after complete source/evidence/local verification and fresh public check."""
import hashlib,json,subprocess,urllib.request
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'candidate';api='https://api.ecdsa.fail/api';bench='1ffb695a-309b-46b6-a728-2f97d8c7be74';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def save(n,v):(r/n).write_text(json.dumps(v,indent=2)+'\n')
def fetch(path):
 with urllib.request.urlopen(api+path,timeout=60)as response:return json.load(response)
def git(*a):return subprocess.check_output(['git','-C',str(t),*a])
assert not(r/'UPLOAD-STARTED.json').exists(),'Inspect any existing response/public status; never blindly duplicate an upload'
f=json.loads((r/'SOURCE-FREEZE.json').read_text());v=json.loads((r/'FINAL-VERIFICATION.json').read_text());b=json.loads((r/'BENCHMARK-RESULT.json').read_text());local=json.loads((r/'LOCAL-VERIFICATION.json').read_text());receipt=json.loads((r/'PACKAGE-RESULT.json').read_text());manifest=json.loads((r/'EVIDENCE-MANIFEST.json').read_text())
assert local['status']=='EVERY_FINAL_EVIDENCE_AND_SOURCE_MEMBER_VERIFIED_LOCALLY'and local['archive_sha256']==receipt['archive_sha256']==sha(r/'final-evidence.tar.gz');assert local['source_revision']==v['source_revision']==git('rev-parse','HEAD').decode().strip()
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());assert{p.relative_to(t).as_posix()for p in(t/'src/point_add').rglob('*')if p.is_file()}==set(f['source_files'])
protected=[p for p in git('ls-files').decode().splitlines()if not p.startswith('src/point_add/')];assert len(protected)==17
for p in protected:assert(t/p).read_bytes()==git('show','HEAD:'+p)
assert not git('diff','--name-only').strip()and not git('diff','--cached','--name-only').strip();assert sha(t/'ops.bin')==v['native_receipt']['stream_sha256'];assert sha(r/'source.patch')==v['source_patch_sha256'];assert sha(r/'point-add-source.tar.gz')==v['source_archive_sha256'];assert sha(r/'BENCHMARK-RESULT.json')==v['benchmark_result_sha256']
assert b['tested_shots']==9024 and b['qubits']==v['qubits'] and v['unchanged_benchmark_passed_shots']==9024 and v['selected_protected_packet_passed'];assert(r/'run.exit').read_text().strip()=='0';assert 'all 9024 shots OK'in(r/'benchmark.log').read_text()
snapshot=fetch('/benchmarks/'+bench+'/submissions');save('public-before-upload.json',snapshot)
eligible=[x for x in snapshot['submissions']if x.get('officialMetrics')and(x.get('status')=='accepted'or x.get('status')=='rejected'and x.get('rejectionReason')=='score did not improve current best')and x.get('officialScore')==x['officialMetrics']['qubits']*x['officialMetrics']['toffoli']]
parent=min(eligible,key=lambda x:x['officialMetrics']['toffoli']);assert parent['id']=='d182a53e-be3d-4119-8298-303a9a9de07a','Fresh Toffoli parent changed; preserve existing final-gate verdict and assess target'
assert b['rounded_mean_executed_toffoli']<parent['officialMetrics']['toffoli'],'Measured finished packet does not beat current public T; do not choose another nonce by cost'
note=r/'SUBMISSION-NOTE.md';deps=r/'DEPENDENCIES.json';assert note.stat().st_size>=4000 and json.loads(deps.read_text())[0]['submissionId']==parent['id']
duplicates=[x['id']for x in snapshot['submissions']if x.get('solverUsername')=='MonitSharma'and v['source_archive_sha256']in(x.get('note')or'')];assert not duplicates,duplicates
audit={'at_utc':datetime.now(timezone.utc).isoformat(),'source_revision':v['source_revision'],'source_files':201,'protected_files':17,'local_evidence_sha256':local['archive_sha256'],'source_archive_sha256':v['source_archive_sha256'],'native_stream_sha256':v['native_receipt']['stream_sha256'],'note_sha256':sha(note),'dependencies_sha256':sha(deps),'model':'GPT-6 sol','harness':'Codex','submission_mode':'auto','user_authorization':'20October2026 direct request:submit every new verified improvement','fresh_parent_id':parent['id'],'fresh_parent_T':parent['officialMetrics']['toffoli'],'candidate_Q':b['qubits'],'candidate_T':b['rounded_mean_executed_toffoli'],'candidate_product':b['product'],'gate_and_nonce_complete':True};save('PREUPLOAD-AUDIT.json',audit)
with(r/'UPLOAD-STARTED.json').open('x')as out:json.dump({'at_utc':datetime.now(timezone.utc).isoformat(),'source_revision':v['source_revision'],'note_sha256':sha(note)},out)
with(r/'submission-response.json').open('xb')as out,(r/'submission-submit.err').open('xb')as err:
 p=subprocess.run(['/home/hclau/.local/bin/ecdsafail','submit','--note-file',str(note),'--dependencies-file',str(deps),'--model','GPT-6 sol','--harness','Codex','--claimed-score',str(b['product']),'--json'],cwd=t,stdout=out,stderr=err)
(r/'upload.exit').write_text(str(p.returncode)+'\n');assert p.returncode==0,'Inspect response/errors and public API; never blindly retry an uncertain upload'
response=json.loads((r/'submission-response.json').read_text());sid=response['submission']['id'];save('submission-status.json',fetch('/submissions/'+sid));print(json.dumps({'id':sid,'status':response['submission']['status'],'Q':b['qubits'],'T':b['rounded_mean_executed_toffoli'],'product':b['product']}),flush=True)
