from pathlib import Path
import re,json,sys,importlib.util
import walk_model as m
root=Path(__file__).resolve().parent
original='--original' in sys.argv
if original:
 spec=importlib.util.spec_from_file_location('original',root/'walk_model-original.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
source_t0='--source-t0' in sys.argv
if source_t0:
 spec=importlib.util.spec_from_file_location('source_t0',root/'source-t0-model/walk_model.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rx=re.compile(r'PAYLOAD_OBS shot=(\d+) id=(\d+) before=(\w+) phase=(\w+) tick=(\d+) rev=(\w+) at=(\d+) p0=(0x\w+) p1=(0x\w+) tape=(\[.*\])')
entry={};errors=[];allrecords=[]
for line in (root/'observer.log').read_text().splitlines():
 z=rx.match(line)
 if not z:continue
 shot,idx,before,phase,tick,rev,at,p0,p1,tape=z.groups();shot,idx,tick,at=map(int,[shot,idx,tick,at]);rev=rev=='true';pay=[int(p0,16),int(p1,16)];tape=json.loads(tape);key=shot,idx
 if before=='true':entry[key]=(pay,tape);continue
 old,saved=entry.pop(key);ti=tick%2;si=1-ti;tape=saved if rev else tape
 ns=len(tape)-2;signs=tape[:ns];extra=tape[-2]+2*tape[-1];a,b=old[ti],old[si]
 if not rev:
  if tick<137:want=m.onefold(a,b,signs,extra,tick)
  else:want=m.half((a+(-b if signs[0]else b))%m.P)
 else:
  if 1<=tick<127:want=m.onefold(a,b,signs,extra,tick,True)
  else:
   want=a*(1<<extra)%m.P
   for s in reversed(signs):want=(2*want+(b if s else -b))%m.P
 want%=m.P
 result=dict(shot=shot,phase=phase,tick=tick,rev=rev,at=at,tape=tape,a=a,b=b,expected=want,actual=pay[ti]%m.P,delta=(pay[ti]-want)%m.P,source_delta=(pay[si]-b)%m.P)
 allrecords.append(result)
 if result['delta']or result['source_delta']:errors.append(result)
families=json.loads((root/'packets/audit-rows.json').read_text());first={}
for e in errors:first.setdefault(e['shot'],e)
report={'checked_ticks':len(allrecords),'local_model_mismatches':len(errors),'first_divergences':[dict(families[s],**e)for s,e in sorted(first.items())],'all_mismatches':errors}
(root/('payload-divergences-original.json'if original else'payload-divergences-source-t0.json'if source_t0 else'payload-divergences.json')).write_text(json.dumps(report,indent=2)+'\n')
print('checked_ticks',len(allrecords),'mismatches',len(errors))
for shot in range(len(families)):
 e=first.get(shot);print(shot,families[shot]['family'],families[shot]['batch'],families[shot]['lane'],None if e is None else {k:e[k]for k in ['phase','tick','rev','tape','delta','source_delta']})
