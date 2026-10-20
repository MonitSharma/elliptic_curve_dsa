import hashlib,json,os,shutil,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';f=json.loads((r/'SOURCE_FREEZE.json').read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();binary=sha(t/'target/release/build_circuit');rows=[]
def records(path):
 with path.open('rb',buffering=0)as raw:
  header=raw.read(16);assert len(header)==16 and header[:8]==b'QECCOPSZ';count=int.from_bytes(header[8:],'little');h=hashlib.sha256();size=0
  p=subprocess.Popen(['zstd','-dc'],stdin=raw,stdout=subprocess.PIPE)
  while chunk:=p.stdout.read(1<<20):h.update(chunk);size+=len(chunk)
  assert p.wait()==0 and size==56*count
 return {'operations':count,'record_sha256':h.hexdigest()}
expected={}
for cap,hashvalue in [(1234,'13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'),(1233,'8d458cf4cfbf340264c41a33d1ca4e7fae203420690bcc6dc09cbe2f9ed2ad4f')]:
 p=r.parent/'breakthrough-t0-shared-product-20261020'/f'cap{cap}/ops.bin';assert sha(p)==hashvalue;expected[cap]=records(p)
assert (r/'run.exit').read_text().strip()=='1';assert all(sha(t/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items())
for mode,cap in [('official',1234),('generic',1234),('generic',1233)]:
 assert all(sha(t/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items());assert sha(t/'target/release/build_circuit')==binary
 case=r/f'{mode}-cap{cap}';recovered=mode=='official'
 if recovered:
  assert (case/'generate.exit').read_text().strip()=='0';rc=0;seconds=None
 else:
  case.mkdir(exist_ok=False);env=os.environ.copy();env.update(BREAK_CAP='1234',BREAK_HARD=str(cap),BREAK_POST=mode);start=time.time()
  with(case/'generate.out').open('xb')as out,(case/'generate.log').open('xb')as err:
   p=subprocess.Popen(['/usr/bin/time','-v',str(t/'target/release/build_circuit')],cwd=t,env=env,stdout=out,stderr=err);(case/'child.pid').write_text(str(p.pid)+'\n');rc=p.wait()
  seconds=time.time()-start;(case/'generate.exit').write_text(str(rc)+'\n')
  if rc==0:
   for fn in ['ops.bin','prepass.ops.bin']:shutil.copyfile(t/fn,case/fn)
 log=(case/'generate.log').read_text();row={'mode':mode,'cap':cap,'exit':rc,'seconds':seconds,'recovered_existing_official_control':recovered,'binary_sha256':binary,'generic_stages':[l for l in log.splitlines()if l.startswith('GENERIC_STAGE ')]}
 if rc==0:
  row['stream_sha256']=sha(case/'ops.bin');row['raw_framed_sha256']=sha(case/'prepass.ops.bin');row['raw_records']=records(case/'prepass.ops.bin');assert row['raw_records']==expected[cap]
  if mode=='official':assert row['stream_sha256']=='125deb3a03b460ec991df012e6aa8e6a6b67fc96ffc525a165b5ca3e67282501'
 else:row['failure_tail']=log[-2500:]
 rows.append(row);(r/'AUDIT-PROGRESS-v2.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
 if rc!=0:raise SystemExit(rc)
(r/'AUDIT-RESULT-v2.json').write_text(json.dumps({'status':'COMPLETED_POSTPASS_AUDIT_NOT_SCORED','cases':rows,'scope':'Official byte stream exactly reproduced as baseline only. Diagnostic raw writer useswindow_log27, unlike official default: compare full uncompressed56-byte records and header length. Original compressed-hash assertion failure preserved; no source or binary changed. Generic streams omit source-bound tables, census cuts and nonce tail. Depth weights are diagnostic, not executed metrics.'},indent=2)+'\n')
