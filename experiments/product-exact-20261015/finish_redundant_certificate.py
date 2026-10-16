"""Do not leave the duplicate proof computation paused after the new audit."""
import json,os,signal,time
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'cache-certificate-v2-20261016';old=r/'cache-certificate-20261016'
(r/'finish-redundant-certificate.pid').write_text(str(os.getpid())+'\n')
while not (d/'launcher.exit').exists():time.sleep(15)
if not (old/'PAUSED_FOR_PARALLEL.json').exists():raise SystemExit
row=json.loads((old/'PAUSED_FOR_PARALLEL.json').read_text());pid=row['pid'];p=Path('/proc')/str(pid)
if not p.exists():print('Duplicate already terminal');raise SystemExit
assert (p/'cwd').resolve()==r and 'bash run-cache-certificate.sh' in (p/'cmdline').read_bytes().replace(b'\0',b' ').decode()
assert os.getpgid(pid)==row['pgid']==pid
passed=(d/'launcher.exit').read_text().strip()=='0'
if passed:
    receipt=json.loads((d/'RECEIPT.json').read_text());assert receipt['status']=='UNIVERSAL_CACHE_CHAIN_PASS' and len(receipt['stages'])==25 and all(x['status']=='PASS' for x in receipt['stages'])
    os.killpg(pid,signal.SIGTERM)
os.killpg(pid,signal.SIGCONT)
action={'pid':pid,'pgid':pid,'action':'retire duplicate after complete new universal audit' if passed else 'resume duplicate after new audit did not complete','new_receipt':'cache-certificate-v2-20261016/RECEIPT.json','scope':'Only owned dedicated deterministic proof group; no census/source/other agent process affected.'}
(old/'PAUSE_RESOLVED.json').write_text(json.dumps(action,indent=2)+'\n');print(json.dumps(action))
