import hashlib,json,os,shutil,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';f=json.loads((r/'SOURCE_FREEZE.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for cap,enabled in f['cases']:
    assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
    name=f'cap{cap}-bridge{int(enabled)}';case=r/name;case.mkdir(exist_ok=False)
    env=os.environ.copy();env['BREAK_CAP']=str(cap);env['BREAK_BRIDGE']=str(int(enabled))
    start=time.time()
    with(case/'generate.out').open('xb')as out,(case/'generate.log').open('xb')as err:
        p=subprocess.Popen(['/usr/bin/time','-v',str(t/'target/release/build_circuit')],cwd=t,env=env,stdout=out,stderr=err)
        (case/'child.pid').write_text(str(p.pid)+'\n');rc=p.wait()
    (case/'generate.exit').write_text(str(rc)+'\n');log=(case/'generate.log').read_text()
    row={'capacity':cap,'bridge':enabled,'exit':rc,'seconds':time.time()-start,
        'builder_totals':[l for l in log.splitlines()if l.startswith('HEO_TOTAL ')],
        'uses':sum(l.startswith('PARITY_USE\t')for l in log.splitlines()),'case':name}
    if rc==0:
        shutil.copyfile(t/'ops.bin',case/'ops.bin');row['stream_sha256']=sha(case/'ops.bin');row['stream_bytes']=(case/'ops.bin').stat().st_size
        if not enabled:assert row['stream_sha256']=='13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'
    else:
        row['failure_lines']=[l for l in log.splitlines()if'panicked'in l or'cap'in l or'budget'in l][-8:]
    rows.append(row)
    (r/'ADMISSION-PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
(r/'ADMISSION-RESULT.json').write_text(json.dumps({'status':'RAW_ADMISSION_COMPLETE_NO_SCORE','cases':rows,
    'scope':'Native generation and builder diagnostics only, no complete optimized result or final statistical gate.'},indent=2)+'\n')
