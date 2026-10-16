from pathlib import Path
import hashlib,json,subprocess,os
r=Path(__file__).resolve().parent;d=r/'all70-cache67-20261016';attempt=d/'launcher-cwd-repair-attempt1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();stop=json.loads((attempt/'RECEIPT.json').read_text());assert stop['status']=='CONTROLLED_OWNED_GROUP_STOP_FOR_CWD_REPAIR'
for group in stop['groups']:
 try:os.kill(group['pid'],0)
 except ProcessLookupError:continue
 else:raise AssertionError(('old launcher still present',group))
records=json.loads((attempt/'LAST_COMPLETE_STAGE_RECEIPTS.json').read_text());plan=json.loads((d/'DECLARATION.json').read_text());assert len(records)==stop['completed_universal_stages']<25
for i,row in enumerate(records):assert row['config']==plan['stages'][i]and row['stage']==i+1
paths=[d/'cache-launcher.exit',r/'all70-native67-20261016/launcher.exit',r/'all70-native67-20261016/census-launcher.exit']
for p in paths:
 assert p.is_relative_to(r)
 if p.exists():p.unlink()
scripts=['resume_all70_cache67.py','resume-all70-cache67.sh','all70_resource_guard.py','watch-all70-native67.sh','watch-all70-census67.sh']
record={'status':'SAME_FIXED67_REARMED_AFTER_CWD_REPAIR','resume_stage':len(records)+1,'fixed_source_declaration_sha256':sha(d/'DECLARATION.json'),'completed_streams_rederived':False,'source_or_recipe_changed':False,'numerical_packets_previously_run':0,'repair':'Absolute diagnostic manifest paths and cwd=r; preserve all complete universal stages and interrupted output; resource admission waits before new phases','scripts_sha256':{name:sha(r/name)for name in scripts}}
(d/'CWD_REPAIR_REARM_PLAN.json').write_text(json.dumps(record,indent=2)+'\n')
for name,cpus,log in [('resume-all70-cache67.sh','126','all70-cache-resume-nohup.log'),('watch-all70-native67.sh','126,127','all70-native67-resume-nohup.log'),('watch-all70-census67.sh','126,127','all70-census67-resume-nohup.log')]:
 with(r/log).open('wb')as out:
  p=subprocess.Popen(['nohup','taskset','-c',cpus,'bash',str(r/name)],stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True,cwd=r)
 record.setdefault('new_launches',[]).append({'script':name,'pid':p.pid,'pgid':p.pid,'affinity':cpus,'log':log})
(d/'CWD_REPAIR_REARM_RECEIPT.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2),flush=True)
