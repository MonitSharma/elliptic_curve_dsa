import hashlib,json,os,shutil,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
for args,log,cwd in[(['python3','prepare.py'],'prepare.log',r),(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build.log',t)]:
 with(r/log).open('xb')as out:rc=subprocess.call(args,cwd=cwd,stdout=out,stderr=subprocess.STDOUT)
 if rc:(r/'run.exit').write_text(str(rc)+'\n');raise SystemExit(rc)
f=json.loads((r/'SOURCE_FREEZE.json').read_text());rows=[]
for mode in['generic','certified']:
 assert all(sha(t/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items());case=r/mode;case.mkdir();env=os.environ.copy();env.update(BREAK_CAP='1234',BREAK_HARD='1234',BREAK_POST=mode);start=time.time()
 with(case/'generate.out').open('xb')as out,(case/'generate.log').open('xb')as err:p=subprocess.Popen([str(t/'target/release/build_circuit')],cwd=t,env=env,stdout=out,stderr=err);(case/'child.pid').write_text(str(p.pid)+'\n');rc=p.wait()
 (case/'generate.exit').write_text(str(rc)+'\n');log=(case/'generate.log').read_text();row={'mode':mode,'exit':rc,'seconds':time.time()-start,'generic_stages':[l for l in log.splitlines()if l.startswith('GENERIC_STAGE ')],'bindings':[l for l in log.splitlines()if l.startswith(('REBIND ','Y42_BOUND ','RBA '))]}
 if rc==0:
  shutil.copyfile(t/'ops.bin',case/'ops.bin');row['stream_sha256']=sha(case/'ops.bin')
  if mode=='generic':assert row['stream_sha256']=='40a55e81af487e4f830eca1827d9904f60ed215b33d3bee9f12a801a46c4479c'
 else:row['failure_tail']=log[-3000:]
 rows.append(row);(r/'AUDIT-PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
 if rc:break
(r/'AUDIT-RESULT.json').write_text(json.dumps({'status':'CERTIFICATE_PREFIX_AUDIT_NOT_SCORED','cases':rows,'scope':f['scope']},indent=2)+'\n');(r/'run.exit').write_text('0\n')
