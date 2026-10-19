"""Queue one serial whole-source screen after the pair screen, never rerun it."""
from pathlib import Path
ws=Path(__file__).resolve().parent.parent;r=ws/'product-linear-witness-20261020';old=ws/'product-pair-witness-20261020'
assert not (r/'run.py').exists()
s=(old/'run.py').read_text().replace("old=ws/'product-copy-cache-witness-20261020'","old=ws/'product-pair-witness-20261020'")
s=s.replace("ANF_PAIR_WITNESSES='0',ANF_WITNESSES='1'","ANF_LINEAR_WITNESSES='0',ANF_PAIR_WITNESSES='0',ANF_WITNESSES='1'")
s=s.replace("dict(os.environ,ANF_PAIR_WITNESSES='0')","dict(os.environ,ANF_PAIR_WITNESSES='1',ANF_LINEAR_WITNESSES='0')")
s=s.replace("dict(os.environ,ANF_PAIR_WITNESSES='1'))","dict(os.environ,ANF_PAIR_WITNESSES='1',ANF_LINEAR_WITNESSES='1'))")
s=s.replace('EXACT_TWO_WIRE_XOR_PRODUCT_SOURCE_SCREEN_COMPLETED','EXACT_LINEAR_CURRENT_WIRE_PRODUCT_SOURCE_SCREEN_COMPLETED')
s=s.replace("'pair_witness_sites':sum(x.get('kind')=='exact_two_wire_xor_product'","'linear_witness_sites':sum(x.get('kind')=='exact_current_wire_linear_product'")
s=s.replace("'source':result,'disabled_complete_report", "'source':result,'additional_change_beyond_pair_baseline':result['output_sha3_256']!=baseline['output_sha3_256'],'disabled_complete_report")
s=s.replace("'pair_witness_mode':(env or os.environ).get('ANF_PAIR_WITNESSES')", "'linear_witness_mode':(env or os.environ).get('ANF_LINEAR_WITNESSES')")
needle="commands=[]";assert s.count(needle)==1
s=s.replace(needle,"native=json.loads((ws/'product-linear-witness-controls-v2-20261020/RESULT.json').read_text());assert native['status']=='EXACT_LINEAR_WITNESS_30_PRIMITIVE_CONTROLS_PASS'\nassert all(hashlib.file_digest((r/p).open('rb'),'sha256').hexdigest()==h for p,h in native['source_files'].items())\n"+needle)
(r/'run.py').write_text(s,newline='\n')
(r/'run.sh').write_text((old/'run.sh').read_text().replace('product-pair-witness-20261020','product-linear-witness-20261020'),newline='\n')
(r/'launch.py').write_text((old/'launch.py').read_text().replace('product-copy-cache-witness-20261020','product-pair-witness-20261020').replace('Local exact two-wire XOR product job','Local exact sparse linear product job'),newline='\n')
(r/'watch.py').write_text('''import hashlib,json,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'product-pair-witness-20261020';bound=json.loads((r/'WATCH_SOURCE.json').read_text());assert not (r/'WATCH_RESULT.json').exists()
while not (old/'run.exit').exists():time.sleep(15)
assert all(hashlib.sha256((r/p).read_bytes()).hexdigest()==h for p,h in bound.items())
if (old/'run.exit').read_text().strip()!='0' or not (old/'RESULT.json').exists():
 (r/'WATCH_RESULT.json').write_text(json.dumps({'status':'REFUSED_OLD_SOURCE_SCREEN_NOT_PASS','at_utc':datetime.now(timezone.utc).isoformat(),'run_started':False},indent=2)+'\\n');raise SystemExit(0)
result=subprocess.run(['python3',str(r/'launch.py')],check=True)
(r/'WATCH_RESULT.json').write_text(json.dumps({'status':'PRIOR_SCREEN_FINISHED_NEW_SERIAL_SCREEN_LAUNCHED','at_utc':datetime.now(timezone.utc).isoformat(),'launch_exit':result.returncode},indent=2)+'\\n')
''',newline='\n')
(r/'launch_waiter.py').write_text('''import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;assert not (r/'watch.pid').exists() and not (r/'run.pid').exists()
assert (r.parent/'product-linear-witness-controls-v2-20261020/LOCAL-VERIFICATION.json').exists()
bound={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in r.iterdir() if p.suffix in ['.py','.rs','.sh']};(r/'WATCH_SOURCE.json').write_text(json.dumps(bound,indent=2)+'\\n')
with (r/'watch-nohup.log').open('xb') as f:p=subprocess.Popen(['nohup','python3','watch.py'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'watch.pid').write_text(str(p.pid)+'\\n');print('Idle local linear-screen waiter',p.pid)
''',newline='\n')
print('Prepared immutable serial linear driver and waiter; not launched')
