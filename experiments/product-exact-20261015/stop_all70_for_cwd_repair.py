"""Stop only owned isolated launch groups; preserve complete stages and interrupted output."""
from pathlib import Path
import os,signal,time,json,shutil,hashlib,subprocess
r=Path(__file__).resolve().parent;d=r/'all70-cache67-20261016';out=d/'launcher-cwd-repair-attempt1';out.mkdir(exist_ok=False)
roles=[('cache',d/'cache-launcher.pid','watch-all70-cache67.sh'),('native',r/'all70-native67-20261016/launcher.pid','watch-all70-native67.sh'),('census',r/'all70-native67-20261016/census-launcher.pid','watch-all70-census67.sh')]
groups=[]
for role,path,name in roles:
 pid=int(path.read_text());assert os.getpgid(pid)==pid;cmd=Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0',b' ').decode();assert str(r/name)in cmd;groups.append({'role':role,'pid':pid,'pgid':pid,'cmdline':cmd})
(out/'OWNED_GROUPS_BEFORE.json').write_text(json.dumps(groups,indent=2)+'\n')
for name in ['run_all70_cache67.py','watch-all70-cache67.sh','watch-all70-native67.sh','watch-all70-census67.sh']:shutil.copyfile(r/name,out/name)
# Preserve current proof; stop immediately after its next fully audited receipt.
initial=json.loads((d/'CACHE_STAGE_RECEIPTS.json').read_text());target=len(initial)+1;deadline=time.monotonic()+240
for g in groups[1:]:os.killpg(g['pgid'],signal.SIGTERM)
while True:
 try:rows=json.loads((d/'CACHE_STAGE_RECEIPTS.json').read_text())
 except json.JSONDecodeError:time.sleep(.2);continue
 if len(rows)>=target or (d/'cache-launcher.exit').exists() or time.monotonic()>=deadline:break
 time.sleep(.2)
(out/'LAST_COMPLETE_STAGE_RECEIPTS.json').write_text(json.dumps(rows,indent=2)+'\n')
try:os.killpg(groups[0]['pgid'],signal.SIGTERM)
except ProcessLookupError:pass
time.sleep(2)
for g in groups:
 live=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit():continue
  try:
   if os.getpgid(int(p.name))==g['pgid']and (p/'stat').read_text().split(') ',1)[1].split()[0]!='Z':live.append(int(p.name))
  except(FileNotFoundError,ProcessLookupError,PermissionError):pass
 assert not live,(g,live)
for p in [d/'cache-chain.log',d/'cache-launcher.pid',d/'cache-launcher.exit',r/'all70-native67-20261016/launcher.pid',r/'all70-native67-20261016/launcher.exit',r/'all70-native67-20261016/census-launcher.pid',r/'all70-native67-20261016/census-launcher.exit']:
 if p.exists():shutil.copyfile(p,out/(('native-'if p.parent.name.startswith('all70-native')else'')+p.name))
last=len(rows);assert last<25
for p in list(d.glob('all70-*')):
 parts=p.name.split('-')
 if len(parts)>2 and parts[1].isdigit()and int(parts[1])>last:shutil.move(str(p),out/p.name)
shutil.copyfile(d/'chain.manifest',out/'original-chain.manifest')
record={'status':'CONTROLLED_OWNED_GROUP_STOP_FOR_CWD_REPAIR','completed_universal_stages':last,'groups':groups,'source_recipe_changed':False,'numerical_packets_run':0,'future_census_label_changed':False,'interrupted_files_preserved':True,'next_stage':last+1};(out/'RECEIPT.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
