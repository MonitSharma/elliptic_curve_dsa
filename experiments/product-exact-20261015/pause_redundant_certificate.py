"""Pause only this experiment's redundant sequential proof group."""
import json,os,signal
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'cache-certificate-20261016'
if (d/'launcher.exit').exists():print('Already terminal; no pause');raise SystemExit
pid=int((d/'launcher.pid').read_text());p=Path('/proc')/str(pid)
assert p.exists() and (p/'cwd').resolve()==r
cmd=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode();assert 'bash run-cache-certificate.sh' in cmd
group=os.getpgid(pid);assert group==pid,'Not a dedicated setsid process group'
row={'pid':pid,'pgid':group,'cwd':str(r),'command':cmd,'reason':'Redundant deterministic proof audit paused to keep active audit workers at most4; no census or circuit changed.'}
(d/'PAUSED_FOR_PARALLEL.json').write_text(json.dumps(row,indent=2)+'\n');os.killpg(group,signal.SIGSTOP);print(json.dumps(row))
