from pathlib import Path
import importlib.util,json,tempfile
root=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('terminal_audit',root/'audit-terminal.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def reject(n):return {'nonce':n,'certified_wrong_value':True,'authoritative_rejection':True,'proof_accepted':True,'witness_batch':0,'witness_shot':1,'witnesses_tried':1}
def fallback(n,passed=False,kind='phase',shots=64,protected=0):return {'nonce':n,'certified_wrong_value':False,'candidate_full_fallback_pass':passed,'authoritative_rejection':not passed,'proof_accepted':True,'witnesses_tried':0,'exact_early_kind':kind,'exact_early_shots':shots,'protected_shots':protected}
base=[reject(n) for n in [10,1,9,2]]
def mutate(index,key,value):
 rows=[r.copy() for r in base];rows[index][key]=value;return rows
checks=[]
with tempfile.TemporaryDirectory(prefix='ecdsa-log-audit-',dir=root) as directory:
 assert Path(directory).resolve().is_relative_to(root.resolve())
 path=Path(directory)/'lane.jsonl'
 def run(rows,valid,name,newline=True):
  path.write_text('\n'.join(json.dumps(r) for r in rows)+ ('\n' if newline else ''))
  try:out=module.audit_lane(path,0,4,2,4)
  except (ValueError,KeyError):
   assert not valid,name
  else:
   assert valid,name
   assert out['rows']==4 and out['complete_local_prefix']
  checks.append({'case':name,'expected_accept':valid})
 run(base,True,'unordered complete exact lane')
 for kind in ['classical','phase','ancilla']:
  rows=[r.copy() for r in base];rows[0]=fallback(10,kind=kind);run(rows,True,'exact '+kind+' rejection')
 rows=[r.copy() for r in base];rows[0]=fallback(10,shots=9023);run(rows,True,'excluded raw pair partial final reject')
 rows=[r.copy() for r in base];rows[0]=fallback(10,True,'pass',9024,9024);run(rows,True,'full protected pass')
 rows=[r.copy() for r in base];rows[0]=fallback(10,False,'pass',9024,9024);run(rows,True,'full protected failure after early pass')
 run(base[:-1],False,'missing row')
 run(base+[base[0]],False,'duplicate row')
 for key,value,name in [('nonce',3,'wrong lane'),('nonce',17,'outside complete prefix'),('nonce',True,'boolean nonce'),('authoritative_rejection',False,'unauthoritative wrong bit'),('proof_accepted',False,'disabled proof gate'),('certified_wrong_value',None,'unknown disposition'),('witness_batch',141,'invalid batch'),('witness_shot',64,'invalid shot'),('witnesses_tried',0,'no witness attempt'),('candidate_full_fallback_pass',False,'conflicting dispositions')]:run(mutate(0,key,value),False,name)
 rows=[r.copy() for r in base];rows[0]=fallback(10,True,'pass',9024,0);run(rows,False,'missing protected pass')
 rows=[r.copy() for r in base];rows[0]=fallback(10,True,'pass',9023,9023);run(rows,False,'short protected pass')
 rows=[r.copy() for r in base];rows[0]=fallback(10,kind='unknown');run(rows,False,'unknown exact rejection')
 run(base,False,'truncated final JSONL',False)
report={'status':'TERMINAL_LANE_AUDIT_POSITIVE_AND_ADVERSARIAL_CONTROLS_PASS','checks':checks,'production_log_read':False,'no_nonce_selected':True}
(root/'terminal-audit-tests.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'checks':len(checks)}))
