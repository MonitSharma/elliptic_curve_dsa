from pathlib import Path
import os,signal,json,time
r=Path(__file__).resolve().parent
records=[]
for label,script in [('mask-validate','run-mask-validate.sh'),('mask-validate-v2','run-mask-validate-v2.sh')]:
 pid=int((r/f'evidence/{label}.pid').read_text())
 proc=Path(f'/proc/{pid}')
 if not proc.exists(): records.append(dict(label=label,pid=pid,already_completed=True));continue
 cmd=(proc/'cmdline').read_bytes().split(b'\0')
 assert cmd[:2]==[b'bash',script.encode()],cmd
 assert (proc/'cwd').resolve()==r
 pgid=os.getpgid(pid);assert pgid==pid,(pid,pgid)
 record=dict(label=label,pid=pid,pgid=pgid,argv=[s.decode() for s in cmd if s],reason='Expanded reference bytecode has128million nodes; defer runtime validation to exact compact binary-construction-trace export v3. No source/record changed, no unvalidated mask gate enabled.',status='DEFERRED_NOT_VALIDATED',unix_time=time.time())
 records.append(record);(r/f'evidence/{label}-deferred-v3.json').write_text(json.dumps(record,indent=2)+'\n');os.killpg(pgid,signal.SIGTERM)
print(json.dumps(records))
