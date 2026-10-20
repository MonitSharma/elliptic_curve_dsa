import hashlib,json,os,shutil,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';f=json.loads((r/'SOURCE_FREEZE.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
# V1 controller stopped before generation: absent metadata field. Runtime source unchanged.
for cap in [1234,1233]:
    assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
    case=r/f'cap{cap}';case.mkdir(exist_ok=False);env=os.environ.copy();env['BREAK_CAP']='1234';env['BREAK_HARD']=str(cap);start=time.time()
    with(case/'generate.out').open('xb')as out,(case/'generate.log').open('xb')as err:
        p=subprocess.Popen(['/usr/bin/time','-v',str(t/'target/release/build_circuit')],cwd=t,env=env,stdout=out,stderr=err);(case/'child.pid').write_text(str(p.pid)+'\n');rc=p.wait()
    (case/'generate.exit').write_text(str(rc)+'\n');log=(case/'generate.log').read_text()
    row={'cap':cap,'exit':rc,'seconds':time.time()-start,'builder_totals':[l for l in log.splitlines()if l.startswith('HEO_TOTAL ')]}
    if rc==0:
        shutil.copyfile(t/'ops.bin',case/'ops.bin');row['raw_sha256']=sha(case/'ops.bin')
        if cap==1234:assert row['raw_sha256']=='13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'
    else:row['failure_tail']=log[-3000:]
    rows.append(row);(r/'ADMISSION-PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
(r/'ADMISSION-RESULT.json').write_text(json.dumps({'status':'RAW_ADMISSION_COMPLETE_NOT_SCORED','cases':rows},indent=2)+'\n')
