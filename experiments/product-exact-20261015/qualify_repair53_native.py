"""Admit native source/full-stream identity, then consume the complete fixed sample."""
import hashlib,json,math,subprocess,tarfile,sys
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'repair53-native-20261016';tree=d/'candidate';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze=json.loads((r/'REPAIR53_FREEZE.json').read_text());plan=json.loads((r/'REPAIR53_FRESH_CENSUS_PLAN.json').read_text())
native=tree/'ops.bin';assert sha(native)==freeze['external_stream_sha256'];subprocess.run(['cmp',str(native),str(r/freeze['external_stream'])],check=True)
for name in ['loader-native-tests.log','precision-native-tests.log']:assert '9 passed; 0 failed' in (d/name).read_text(),name
paths=subprocess.check_output(['git','-C',str(tree),'diff','--name-only','HEAD'],text=True).splitlines();assert all(p.startswith('src/point_add/') for p in paths)
protected={}
for name in subprocess.check_output(['git','-C',str(tree),'ls-files'],text=True).splitlines():
    if name.startswith('src/point_add/'):continue
    actual=(tree/name).read_bytes();assert actual==subprocess.check_output(['git','-C',str(tree),'show','HEAD:'+name]),name;protected[name]=hashlib.sha256(actual).hexdigest()
files={str(p.relative_to(tree/'src/point_add')):sha(p) for p in (tree/'src/point_add').rglob('*') if p.is_file()}
record={'status':'NATIVE_REPAIRED53_SOURCE_AND_BYTE_IDENTITY_PASS','native_stream_sha256':sha(native),'source_base_revision':subprocess.check_output(['git','-C',str(tree),'rev-parse','HEAD'],text=True).strip(),'source_files_sha256':files,'protected_files_sha256':protected,'diff_paths':paths,'source_prefix_binding':freeze['repair_parent_prefix_manifest'],'native_loader_tests':9,'native_precision_tests':9,'nonce_search_performed':False,'score':None}
(d/'NATIVE_RECEIPT.json').write_text(json.dumps(record,indent=2)+'\n')
with tarfile.open(d/'point-add-source.tar.gz','w:gz') as archive:archive.add(tree/'src/point_add',arcname='point_add')
(d/'source-archive-sha256.txt').write_text(sha(d/'point-add-source.tar.gz')+'  point-add-source.tar.gz\n')
if '--native-only' in sys.argv:
    print('NATIVE_SOURCE_AND_BYTE_IDENTITY_PASS_CENSUS_NOT_LAUNCHED',flush=True);sys.exit(0)
runner=Path(plan['runner']);assert sha(runner)==plan['runner_sha256'];assert sha(r/plan['original_reference_stream'])==plan['original_reference_sha256']
assert plan['batches_per_source']==32768 and plan['first_batch']==0 and plan['last_batch']==32767
# Source jobs are sequential solely to keep root48+otherresearch<=64.
# Every label, batch, shot, source and per-source8-worker setting is unchanged.
for role,ops in [('parent',r/plan['original_reference_stream']),('candidate',native)]:
    out=d/f'{role}-census.jsonl';assert not out.exists()
    with (d/f'{role}-census-preflight.json').open('w') as f:subprocess.run(['python3','/home/hclau/ecdsa_research/server-preflight.py'],stdout=f,check=True)
    with (d/f'{role}-census.log').open('w') as log:
        p=subprocess.Popen([str(runner),str(ops),plan['label'],'0','32768','8',str(out),'0'],stdout=log,stderr=subprocess.STDOUT);(d/f'{role}-census.pid').write_text(str(p.pid)+'\n');rc=p.wait()
    (d/f'{role}-census.exit').write_text(str(rc)+'\n');assert rc==0
rows=[]
for role in ['parent','candidate']:
    data=[json.loads(line) for line in (d/f'{role}-census.jsonl').read_text().splitlines()];assert len(data)==32768 and sorted(row['batch'] for row in data)==list(range(32768)) and all(row['shots']==64 for row in data);rows.append({row['batch']:row for row in data})
a,b=rows;delta=[(a[i]['toffoli']-b[i]['toffoli'])/64 for i in range(32768)];mean=sum(delta)/len(delta);fail=[sum(bool(row['failures']) for row in data.values()) for data in rows];dirty=[sum(row['dirty_shots'] for row in data.values()) for data in rows]
summary={'status':'COMPLETE_FIXED_CENSUS_NOT_A_RESOURCE_RECORD','label':plan['label'],'batches_each':32768,'shots_each':2097152,'parent_sha256':plan['original_reference_sha256'],'candidate_sha256':freeze['external_stream_sha256'],'failed_batches':dict(zip(['parent','candidate'],fail)),'failures_per_packet':dict(zip(['parent','candidate'],[141*f/32768 for f in fail])),'dirty_shots':dirty,'paired_mean_T_saving':mean,'saving_standard_error':math.sqrt(sum((x-mean)**2 for x in delta)/(len(delta)*(len(delta)-1))),'failure_gate_pass':fail[1]<=fail[0] and 141*fail[1]/32768<=18 and dirty[1]==0,'workers_each':8,'source_jobs_sequential_for_global_thread_cap':True,'runner_sha256':sha(runner),'all_declared_rows_retained':True,'nonce_search_performed':False,'score':None}
(d/'census-summary.json').write_text(json.dumps(summary,indent=2)+'\n');(r/'repair53-census-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)
