import hashlib,json,os,shutil,subprocess,time
from pathlib import Path
from collections import Counter
r=Path(__file__).resolve().parent;t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
for args,log,cwd in[(['python3','prepare.py'],'prepare.log',r),(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build.log',t)]:
 with(r/log).open('xb')as out:rc=subprocess.call(args,cwd=cwd,stdout=out,stderr=subprocess.STDOUT)
 if rc:(r/'run.exit').write_text(str(rc)+'\n');raise SystemExit(rc)
f=json.loads((r/'SOURCE_FREEZE.json').read_text());rows=[];traces={}
for mode in [0,2]:
 assert all(sha(t/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items());case=r/f'mode{mode}';case.mkdir();env=os.environ.copy();env.update(BREAK_CAP='1234',BREAK_HARD='1264',BREAK_STRENGTHEN=str(mode));start=time.time()
 with(case/'generate.out').open('xb')as out,(case/'generate.log').open('xb')as err:p=subprocess.Popen([str(t/'target/release/build_circuit')],cwd=t,env=env,stdout=out,stderr=err);(case/'child.pid').write_text(str(p.pid)+'\n');rc=p.wait()
 (case/'generate.exit').write_text(str(rc)+'\n');log=(case/'generate.log').read_text();row={'mode':mode,'exit':rc,'seconds':time.time()-start,'builder_totals':[l for l in log.splitlines()if l.startswith('HEO_TOTAL ')]}
 if rc==0:
  shutil.copyfile(t/'ops.bin',case/'ops.bin');row['raw_sha256']=sha(case/'ops.bin');traces[mode]=[l.split('\t')[1:]for l in log.splitlines()if l.startswith('LAYOUT_AUDIT\t')];(case/'replay-sites.json').write_text(json.dumps(traces[mode],indent=2)+'\n');row['trace_sites']=len(traces[mode]);row['trace_sha256']=sha(case/'replay-sites.json')
  if mode==0:assert row['raw_sha256']=='7fe2bb94f6b68965b87f7af4debd245d53c4b84df91ee0260e032499d49c14df'
 else:row['failure_tail']=log[-3000:]
 rows.append(row);(r/'ADMISSION-PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
comparison=None
if 0 in traces and 2 in traces:
 a=Counter(tuple(x)for x in traces[0]);b=Counter(tuple(x)for x in traces[2]);comparison={'old_only':sum((a-b).values()),'new_only':sum((b-a).values()),'ordered_trace_identical':traces[0]==traces[2]}
(r/'ADMISSION-RESULT.json').write_text(json.dumps({'status':'GENERATION_ONLY_NOT_SCORED','cases':rows,'trace_comparison':comparison,'scope':f['scope']},indent=2)+'\n');(r/'run.exit').write_text('0\n')
