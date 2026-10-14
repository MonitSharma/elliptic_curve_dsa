"""Keep every attempt/status and bind child test logs beyond the generic receipt."""
from pathlib import Path
import subprocess,json,hashlib,gzip,re,ast,datetime
tracked=Path(__file__).parent;raw=Path('research-output/overnight-20261014/product');root='/home/hclau/ecdsa_research/overnight-20261014/product-evidence/'
names=['repair57-components','repair57-components-r1','repair57-components-r2','repair57-production-components','repair57-production-components-r1','repair57-production-bdd']
summary={}
for name in names:
 d=raw/name;d.mkdir(parents=True,exist_ok=True)
 subprocess.run(['scp','-r','smu_server:'+root+name+'/',str(raw)+'/' ],check=True)
 if not (d/'run.exit').exists():raise RuntimeError(name+' still active; no complete receipt')
 logs=sorted(d.glob('*.log'));files={}
 for f in logs:
  output=tracked/(name+'-'+f.name+'.gz');output.write_bytes(gzip.compress(f.read_bytes(),mtime=0));files[f.name]=hashlib.sha256(f.read_bytes()).hexdigest()
 for f in [d/'receipt/receipt.json',d/'receipt/candidate.patch',d/'source.sha256',d/'native.sha256',d/'input.sha256',d/'verification.json']:
  if f.exists():(tracked/(name+'-'+f.name)).write_bytes(f.read_bytes());files[str(f.relative_to(d))]=hashlib.sha256(f.read_bytes()).hexdigest()
 test=(d/'product_repair57_body_inverse_probe.log').read_text() if(d/'product_repair57_body_inverse_probe.log').exists()else''
 metrics=[]
 for line in test.splitlines():
  if line.startswith(('REPAIR57_BODY_NATIVE','REPAIR57_PRODUCTION_NATIVE_VALIDATED','REPAIR57_PRODUCTION_BDD_PROVED','REPAIR57_FORWARD_ALLMR','REPAIR57_PAIR_ALLMR','REPAIR57_STRONG_VALIDATED')):metrics.append(line)
 cost=[]
 for line in test.splitlines():
  if line.startswith('REPAIR57_PRODUCTION widths='):
   kind=re.search(r'forward_kinds=(\{[^}]+\})',line)
   cost.append({'widths':re.search(r'widths=(\([^)]*\))',line)[1],'forward_ops':int(re.search(r'forward_ops=(\d+)',line)[1]),'forward_kinds':ast.literal_eval(kind[1]),'old_slice_equal':'original_slice_equal=true' in line,'freeq_order_matches_old':'freeq_order_matches_old=true' in line,'freeb_order_matches_old':'freeb_order_matches_old=true' in line})
 status={'repair57-components':'INVALID_VERIFICATION_ZERO_TEST_LIBRARY_TARGET','repair57-components-r1':'COMPONENT_ALLMR_AND_NATIVE_FINITE','repair57-components-r2':'ROOMY_COMPLETE_POINT94_ALLMR_AND_NATIVE_FINITE','repair57-production-components':'INCONCLUSIVE_ANF_CAP_BEFORE_NATIVE','repair57-production-components-r1':'EXACT_POOL_NATIVE_FINITE_ANF_INCONCLUSIVE','repair57-production-bdd':'EXACT_POOL_BDD_AND_NATIVE_FINITE_PENDING_VALIDATION'}[name]
 if name=='repair57-production-bdd':
  assert int((d/'run.exit').read_text())==0
  assert 'running 1 test' in test and '1 passed; 0 failed' in test
  assert test.count('REPAIR57_PRODUCTION_BDD_PROVED')==3
  assert int((d/'fault.exit').read_text())==0
  assert '4 passed; 0 failed' in (d/'fault-tests.log').read_text()
  status='EXACT_POOL_BDD_AND_NATIVE_FINITE_PROVED'
 summary[name]={'status':status,'qualified_score':None,'exit':int((d/'run.exit').read_text()),'cost':cost,'metrics':metrics,'artifact_hashes':files}
(tracked/'repair57-evidence-summary.json').write_text(json.dumps({'collected_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'qualified_score':None,'scope':'Component correctness at fixed producer input94, not complete point-addition repair/record; allfutureMR only internal, incomingphase additive, pastMR not quantified.','attempts':summary},indent=2)+'\n',newline='\n')
print(json.dumps({n:r['status']for n,r in summary.items()},indent=2))
