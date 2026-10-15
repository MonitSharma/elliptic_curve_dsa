from pathlib import Path
import os,signal,json,time,hashlib
r=Path(__file__).parent
pid=3704116
cmd=Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
assert cmd[:4]==[b'tool/target/release/global_rng_anf_hybrid',b'/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin',b'packets/audit.tsv',b'32'],cmd
status=Path(f'/proc/{pid}/status').read_text()
report=dict(pid=pid,argv=[c.decode() for c in cmd if c],reason='First precision loss localized to MR-dependent scope guards, which pure-A BDDs do not represent. Superseded by targeted macro analysis per coordinator; incomplete, no output certificate.',status=status,unix_time=time.time())
(r/'evidence/global-anf-hybrid-stopped.json').write_text(json.dumps(report,indent=2)+'\n')
os.kill(pid,signal.SIGTERM)
print(json.dumps(dict(pid=pid,termination_sent='SIGTERM',status='INCOMPLETE_NO_CERTIFICATE')))
