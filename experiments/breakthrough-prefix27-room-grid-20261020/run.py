import hashlib,json,os,re,shutil,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'breakthrough-prefix27-cleanup11-native-20261020';t=old/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text());assert(old/'run-v2.exit').read_text().strip()=='0';assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());cases=[31,32,34,35,37,41];(r/'ROOM-GRID-DECLARATION.json').write_text(json.dumps({'declared_at_utc':datetime.now(timezone.utc).isoformat(),'rooms':cases,'global_cap':1234,'windows':'56','source_freeze_sha256':sha(old/'SOURCE_FREEZE.json'),'binary_sha256':sha(t/'target/release/build_circuit'),'source':str(t),'scope':'Additional fixed architectural scratch-reservation grid on unchanged cleanup11 source. Reuses its11 passing native controls; no new native-test claim, packet, statistical gate or nonce.'},indent=2)+'\n');rows=[]
try:
 for i,room in enumerate(cases):
  assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());dest=r/('room'+str(room));dest.mkdir();env=dict(os.environ,BREAK_CAP='1234',BREAK_HARD='1234',BREAK_PREFIX27_MODE='enabled',BREAK_PREFIX27_ROOM=str(room),BREAK_PREFIX27_WINDOWS='56');start=time.time()
  with(dest/'generate.log').open('xb')as log:
   p=subprocess.Popen(['timeout','1800',str(t/'target/release/build_circuit')],cwd=t,env=env,stdout=log,stderr=subprocess.STDOUT);(dest/'child.pid').write_text(str(p.pid)+'\n');rc=p.wait()
  (dest/'generate.exit').write_text(str(rc)+'\n');text=(dest/'generate.log').read_text();row={'room':room,'exit':rc,'seconds':time.time()-start,'builder_totals':[l for l in text.splitlines()if l.startswith('HEO_TOTAL ')],'prefix27_calls':len(re.findall(r'^PREFIX27_PRODUCTION ',text,re.M))}
  if rc==0:shutil.copyfile(t/'ops.bin',dest/'ops.bin');row['raw_sha256']=sha(dest/'ops.bin')
  else:row['failure_tail']=text[-3000:]
  rows.append(row);(r/'PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
 (r/'RESULT.json').write_text(json.dumps({'status':'RAW_ROOM_GRID_NOT_SCORED','cases':rows,'source_freeze_sha256':sha(old/'SOURCE_FREEZE.json')},indent=2)+'\n');(r/'run.exit').write_text('0\n')
except BaseException:
 (r/'run.exit').write_text('1\n');raise
