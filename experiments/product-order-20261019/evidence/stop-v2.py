"""Stop only this research build before accepting an incomplete RNG proof."""
import json,os,signal,time
from pathlib import Path
r=Path(__file__).resolve().parent;pid=int((r/'run-v2.pid').read_text())
assert Path(f'/proc/{pid}/cwd').resolve()==r
cmd=Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0',b' ').decode()
assert 'bash run-v2.sh' in cmd and os.getpgid(pid)==pid
record={'at_unix':time.time(),'pid':pid,'command':cmd,'reason':'Before source execution: both R and Hmr consume RNG, so R must join the global event chain. No candidate/gate/search produced here.',
    'tests_log_exists':(r/'tests.log').exists(),'reordered_stream_exists':(r/'reordered.ops.bin').exists()}
(r/'STOP-V2.json').write_text(json.dumps(record,indent=2)+'\n')
os.killpg(pid,signal.SIGTERM)
print(json.dumps(record))
