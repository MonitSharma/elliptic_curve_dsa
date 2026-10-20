import hashlib,json,os,re,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'tool';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();env=os.environ.copy()
def run(args,log,cwd=r,extra=None):
 e=env.copy();e.update(extra or{})
 with(r/log).open('xb')as out:p=subprocess.Popen(['timeout','1800']+args,cwd=cwd,env=e,stdout=out,stderr=subprocess.STDOUT);(r/(log+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 if rc:(r/'run.exit').write_text(str(rc)+'\n');raise SystemExit(rc)
run(['python3','prepare.py'],'prepare.log');run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','wide_stream_audit','--no-run'],'build.log',t)
def records(p):
 with p.open('rb',buffering=0)as raw:
  header=raw.read(16);assert header[:8]==b'QECCOPSZ';n=int.from_bytes(header[8:],'little');h=hashlib.sha256();size=0;process=subprocess.Popen(['zstd','-dc'],stdin=raw,stdout=subprocess.PIPE)
  while b:=process.stdout.read(1<<20):h.update(b);size+=len(b)
  assert process.wait()==0 and size==56*n
 return {'operations':n,'record_sha256':h.hexdigest()}
parent=ws/'breakthrough-wide-loan-policy-20261020';deadline=time.time()+1800
while not(parent/'run-v2.exit').exists():
 assert time.time()<deadline;time.sleep(5)
assert(parent/'run-v2.exit').read_text().strip()=='0';pf=json.loads((parent/'SOURCE_FREEZE.json').read_text());f=json.loads((r/'SOURCE_FREEZE.json').read_text());assert len(pf['protected_files'])==17;assert all(sha(parent/'observer'/p)==h for p,h in {**pf['source_files'],**pf['protected_files']}.items());ad=json.loads((parent/'ADMISSION-RESULT.json').read_text());cases=[c for c in ad['cases']if c['exit']==0 and(c['cap']==1234 or c['cap']>=1256)];assert cases[0]['cap']==1234
(r/'INPUT-FREEZE.json').write_text(json.dumps({'source_freeze_sha256':sha(parent/'SOURCE_FREEZE.json'),'cases':cases,'scope':'All successful predeclared wider budgets>=1256 plus original1234 control. Source fixed before stream audit; no input/packet tuning.'},indent=2)+'\n');rows=[]
for c in cases:
 cap=c['cap'];assert all(sha(t/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items());inputfile=parent/f'cap{cap}/ops.bin';assert sha(inputfile)==c['raw_sha256'];output=r/f'cap{cap}.ops.bin';start=time.time();log=f'cap{cap}.log'
 run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','wide_stream_audit','--','--ignored','--nocapture','--test-threads=1'],log,t,{'WIDE_AUDIT_INPUT':str(inputfile),'WIDE_AUDIT_OUTPUT':str(output),'WIDE_AUDIT_CAP':str(cap)})
 text=(r/log).read_text();assert re.findall(r'test result: ok\. (\d+) passed; 0 failed;',text)==['1'];record=records(output)
 if cap==1234:assert record==records(ws/'breakthrough-generic-postpass-20261020/generic-cap1234/ops.bin')
 row={'cap':cap,'seconds':time.time()-start,'input_sha256':sha(inputfile),'output_sha256':sha(output),'output_records':record,'generic_stages':[l for l in text.splitlines()if l.startswith('GENERIC_STAGE ')]};rows.append(row);(r/'AUDIT-PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
(r/'AUDIT-RESULT.json').write_text(json.dumps({'status':'COMPLETE_GENERIC_WIDE_AUDIT_NOT_SCORED','cases':rows,'scope':'Control full operation records match original generic pipeline. Wider outputs omit source-bound/census/nonce passes. Depth weights diagnostic only; no executed resource record, correctness gate or benchmark.'},indent=2)+'\n');(r/'run.exit').write_text('0\n')
