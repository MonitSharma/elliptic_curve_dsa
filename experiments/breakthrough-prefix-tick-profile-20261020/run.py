import hashlib,json,os,re,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();os.environ['PEBBLE_HARD_CAP']='1234'
def run(cmd,name,cwd=t):
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,name
try:
 run(['python3','prepare.py'],'prepare',r);f=json.loads((r/'SOURCE-FREEZE.json').read_text());run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build');rows=[]
 for case in f['cases']:
  assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());dest=r/case['label'];dest.mkdir();env=dict(os.environ,BREAK_CAP='1234',BREAK_HARD='1234',BREAK_PREFIX27_WINDOWS='56',BREAK_PREFIX27_MODE=case['mode'],BREAK_PREFIX27_ROOM=str(case['room']),BREAK_RETAIN_MASK=str(case['mask']));start=time.time()
  with(dest/'generate.log').open('xb')as log:
   p=subprocess.Popen(['timeout','1800',str(t/'target/release/build_circuit')],cwd=dest,env=env,stdout=log,stderr=subprocess.STDOUT);(dest/'child.pid').write_text(str(p.pid)+'\n');rc=p.wait()
  (dest/'generate.exit').write_text(str(rc)+'\n');assert rc==0,case;assert sha(dest/'ops.bin')==case['expected_raw_sha256'],'Read-only instrumentation changed raw stream';text=(dest/'generate.log').read_text();ticks=[];keys=set()
  for line in text.splitlines():
   if not line.startswith('RETAIN_TICK '):continue
   fields=dict(x.split('=',1)for x in line.split()[1:]);key=(fields['phase'],fields['direction'],int(fields['t']),fields['payload']=='true');assert key not in keys,('Ambiguous tick key',key);keys.add(key);ticks.append({'key':key,'live_before':int(fields['live_before']),'live_after':int(fields['live_after']),'op0':int(fields['op0']),'op1':int(fields['op1']),'native':int(fields['native']),'cost':float(fields['cost'])})
  assert ticks;row={**case,'raw_sha256':sha(dest/'ops.bin'),'seconds':time.time()-start,'tick_count':len(ticks),'builder_totals':[l for l in text.splitlines()if l.startswith('HEO_TOTAL ')]};(dest/'TICKS.json').write_text(json.dumps(ticks,indent=2)+'\n');rows.append(row);(r/'PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
 (r/'RESULT.json').write_text(json.dumps({'status':'BYTE_IDENTICAL_STRUCTURAL_TICK_PROFILES_NOT_SCORED','cases':rows,'scope':f['scope']},indent=2)+'\n');(r/'run.exit').write_text('0\n')
except BaseException:
 (r/'run.exit').write_text('1\n');raise
