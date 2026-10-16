from pathlib import Path
import os,signal,json,time,hashlib
r=Path(__file__).resolve().parent
pid=4138361
p=Path('/proc')/str(pid)
cmd=(p/'cmdline').read_bytes().split(b'\0')
assert cmd[0]==b'tool/target/release/a29_rng_mask'
assert cmd[1]==b'../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin'
receipt=dict(status='OWNED_INCOMPLETE_TRIAL_STOPPED_NOT_AN_EXPORT_OR_NEGATIVE_THEOREM',pid=pid,command=[x.decode() for x in cmd if x],proc_status=(p/'status').read_text(),time_unix=time.time(),reason='Superseded by exact-full-body-first candidate mapping; prolonged symbolic helper application and rising memory after the last 7.8m-operation helper receipt. No certificate or mask from this trial is admitted.',log_sha256=hashlib.sha256((r/'global.log').read_bytes()).hexdigest())
(r/'STOPPED.json').write_text(json.dumps(receipt,indent=2)+'\n')
os.kill(pid,signal.SIGTERM)
