import hashlib,json,os,shutil,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';f=json.loads((r/'SOURCE_FREEZE.json').read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();rows=[];binary=sha(t/'target/release/build_circuit')
for mode,cap in [('official',1234),('generic',1234),('generic',1233)]:
 assert all(sha(t/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items());assert sha(t/'target/release/build_circuit')==binary
 case=r/f'{mode}-cap{cap}';case.mkdir(exist_ok=False);env=os.environ.copy();env.update(BREAK_CAP='1234',BREAK_HARD=str(cap),BREAK_POST=mode);start=time.time()
 with(case/'generate.out').open('xb')as out,(case/'generate.log').open('xb')as err:
  p=subprocess.Popen(['/usr/bin/time','-v',str(t/'target/release/build_circuit')],cwd=t,env=env,stdout=out,stderr=err);(case/'child.pid').write_text(str(p.pid)+'\n');rc=p.wait()
 (case/'generate.exit').write_text(str(rc)+'\n');log=(case/'generate.log').read_text();row={'mode':mode,'cap':cap,'exit':rc,'seconds':time.time()-start,'binary_sha256':binary,'generic_stages':[l for l in log.splitlines()if l.startswith('GENERIC_STAGE ')]}
 if rc==0:
  for fn in ['ops.bin','prepass.ops.bin']:shutil.copyfile(t/fn,case/fn)
  row['stream_sha256']=sha(case/'ops.bin');row['raw_sha256']=sha(case/'prepass.ops.bin')
  if cap==1234:assert row['raw_sha256']=='13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'
  else:assert row['raw_sha256']=='8d458cf4cfbf340264c41a33d1ca4e7fae203420690bcc6dc09cbe2f9ed2ad4f'
  if mode=='official':assert row['stream_sha256']=='125deb3a03b460ec991df012e6aa8e6a6b67fc96ffc525a165b5ca3e67282501'
 else:row['failure_tail']=log[-2500:]
 rows.append(row);(r/'AUDIT-PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
 if rc!=0:raise SystemExit(rc)
(r/'AUDIT-RESULT.json').write_text(json.dumps({'status':'COMPLETED_POSTPASS_AUDIT_NOT_SCORED','cases':rows,'scope':'Official stream reproduced only as baseline control; generic streams omit source-bound tables, census cuts and nonce tail. Weighted counts are diagnostic, not executed benchmark metrics.'},indent=2)+'\n')
