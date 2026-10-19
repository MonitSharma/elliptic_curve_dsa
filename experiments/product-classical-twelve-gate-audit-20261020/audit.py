"""Audit the sealed verdict from existing rows only. Never rerun/rejudge it."""
import hashlib,io,json,math,statistics,tarfile
from pathlib import Path
ws=Path(__file__).resolve().parent.parent;r=ws/'product-classical-twelve-native-20261019';q=r/'qualification'
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
assert (r/'gate.exit').read_text().strip()=='0'
decl=json.loads((q/'DECLARATION.json').read_text());verdict=json.loads((q/'RESULT.json').read_text())
assert decl['label']==verdict['label']=='pareto-parent4-classical12-gate-20261019-v1'
assert decl['batch_count']==verdict['batches']==262144 and decl['shots_per_batch']==64
assert verdict['status']=='FAILURE_GATE_PASS' and all(verdict['rules'].values())
assert sha(r/'qualify.py')==decl['driver_sha256'] and sha(r/'SOURCE_FREEZE.json')==decl['frozen_source_manifest_sha256']
freeze=json.loads((r/'SOURCE_FREEZE.json').read_text());tree=Path(freeze['candidate'])
assert len(freeze['protected_files'])==17
assert all(sha(tree/p)==h for p,h in {**freeze['source_files'],**freeze['protected_files']}.items())
rows={}
for name,path in decl['streams'].items():
    assert sha(Path(path['path']))==path['sha256']==verdict['stream_sha256'][name]
    file=q/(name+'.jsonl');assert sha(file)==verdict['census_sha256'][name]
    a=[json.loads(line) for line in file.open()];assert len(a)==262144
    rows[name]={x['batch']:x for x in a};assert sorted(rows[name])==list(range(262144))
    assert all(x['shots']==64 and x.get('skipped',0)==0 for x in a)
p,c=rows['parent'],rows['candidate']
failed={k:sum(bool(x['failures']) for x in a.values()) for k,a in rows.items()}
value={k:sum(x['value_shots'] for x in a.values()) for k,a in rows.items()}
dirty={k:sum(x['dirty_shots'] for x in a.values()) for k,a in rows.items()}
b=sum(bool(c[i]['failures']) and not p[i]['failures'] for i in p);nc=sum(bool(p[i]['failures']) and not c[i]['failures'] for i in p)
# Independent exact-integer recurrence, rather than repeatedly calling comb.
n=b+nc;term=math.comb(n,b);numerator=term
for k in range(b+1,n+1):term=term*(n-k+1)//k;numerator+=term
prob=numerator/(1<<n)
assert (failed,value,dirty)==(verdict['failed_batches'],verdict['value_shots'],verdict['dirty_shots'])
assert b==verdict['newly_failing_b'] and nc==verdict['newly_passing_c'] and prob==verdict['mcnemar_one_sided_p']
rules={'value_not_above_parent':value['candidate']<=value['parent'],'paired_mcnemar_p_at_least_005':prob>=.05,'failed_batches_per_packet_at_most_18':141*failed['candidate']/262144<=18,'zero_dirty_shots':dirty['candidate']==0}
assert rules==verdict['rules'] and all(rules.values())
delta=[(p[i]['toffoli']-c[i]['toffoli'])/64 for i in p]
assert statistics.mean(delta)==verdict['paired_mean_toffoli_saving']
assert statistics.stdev(delta)/len(delta)**.5==verdict['saving_standard_error']
audit={'status':'SEALED_CLASSICAL12_VERDICT_AND_ALL_EXISTING_ROWS_VERIFIED','gate_status':verdict['status'],'label':decl['label'],'batches':262144,'shots_each':16777216,
 'verdict_sha256':sha(q/'RESULT.json'),'declaration_sha256':sha(q/'DECLARATION.json'),'exact_integer_mcnemar_tail_matches':True,
 'all_rows_unique_complete_unskipped':True,'all_source_and_17_protected_hashes_unchanged':True,'no_new_census_or_verdict_change':True,
 'scope':'Read-only audit of the one final gate. No benchmark record, nonce selection or new statistical evidence.'}
(r/'GATE-AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
names=['qualification/DECLARATION.json','qualification/RESULT.json','qualification/parent.jsonl','qualification/candidate.jsonl','qualification/parent.log','qualification/candidate.log',
 'GATE-AUDIT.json','GATE-PLAN.md','SOURCE_FREEZE.json','NATIVE-RECEIPT.json','qualify.py','run-gate.sh','gate.exit','gate.pid','gate-preflight.json','GATE_SOURCE.sha256','PUBLIC-RECORD.json','GATE-ADMISSION-FAILURE.json']
names=[name for name in names if (r/name).exists()]
files={name:{'bytes':(r/name).stat().st_size,'sha256':sha(r/name)} for name in names}
archive=r/'gate-evidence.tar.gz'
with tarfile.open(archive,'x:gz') as a:
    for name in names:a.add(r/name,arcname=name)
    raw=(json.dumps({'scope':audit['scope'],'included_files':files},indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
receipt={'archive':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive),'files':len(files),'gate_status':verdict['status']}
(r/'GATE-EVIDENCE.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
