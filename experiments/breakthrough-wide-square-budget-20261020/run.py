import hashlib,json,os,shutil,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
for args,log,cwd in[(['python3','prepare.py'],'prepare.log',r),(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build.log',t)]:
 with(r/log).open('xb')as out:rc=subprocess.call(args,cwd=cwd,stdout=out,stderr=subprocess.STDOUT)
 if rc:(r/'run.exit').write_text(str(rc)+'\n');raise SystemExit(rc)
f=json.loads((r/'SOURCE_FREEZE.json').read_text());rows=[]
for name,strength,square in [('control',0,1234),('square',0,1264),('strong-square',2,1264)]:
 assert all(sha(t/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items());case=r/name;case.mkdir();env=os.environ.copy();env.update(BREAK_CAP='1234',BREAK_HARD='1264',BREAK_STRENGTHEN=str(strength),BREAK_SQUARE_CAP=str(square));start=time.time()
 with(case/'generate.out').open('xb')as out,(case/'generate.log').open('xb')as err:p=subprocess.Popen([str(t/'target/release/build_circuit')],cwd=t,env=env,stdout=out,stderr=err);(case/'child.pid').write_text(str(p.pid)+'\n');rc=p.wait()
 (case/'generate.exit').write_text(str(rc)+'\n');log=(case/'generate.log').read_text();row={'name':name,'strength':strength,'square_cap':square,'exit':rc,'seconds':time.time()-start,'builder_totals':[l for l in log.splitlines()if l.startswith('HEO_TOTAL ')]}
 if rc==0:
  shutil.copyfile(t/'ops.bin',case/'ops.bin');row['raw_sha256']=sha(case/'ops.bin');trace=[l.split('\t')[1:]for l in log.splitlines()if l.startswith('LAYOUT_AUDIT\t')];(case/'replay-sites.json').write_text(json.dumps(trace,indent=2)+'\n');row['trace_sites']=len(trace);row['trace_sha256']=sha(case/'replay-sites.json')
  if name=='control':assert row['raw_sha256']=='7fe2bb94f6b68965b87f7af4debd245d53c4b84df91ee0260e032499d49c14df'
 else:row['failure_tail']=log[-3000:]
 rows.append(row);(r/'ADMISSION-PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
(r/'ADMISSION-RESULT.json').write_text(json.dumps({'status':'SQUARE_BUDGET_GENERATION_ONLY_NOT_SCORED','cases':rows,'scope':f['scope']},indent=2)+'\n');(r/'run.exit').write_text('0\n')
