"""Extend immutable earlier replay to raw and pre-Y42 stages in a fresh crate."""
from pathlib import Path
import hashlib, subprocess, sys
base,dest,paired=map(Path,sys.argv[1:4])
subprocess.run([sys.executable,str(Path(__file__).with_name('prepare-b3-stage-replay.py')),str(base),str(dest),str(paired)],check=True)
p=dest/'src/main.rs';s=p.read_text()
old='for stage in["before-square-guard","after-square-guard","after-linear-restore","final"]'
new='for stage in["raw-body","before-y42-bound","before-square-guard","after-square-guard","after-linear-restore","final"]'
assert s.count(old)==1
p.write_text(s.replace(old,new),newline='\n')
print('earlier_stage_replay_sha256='+hashlib.sha256(p.read_bytes()).hexdigest())
