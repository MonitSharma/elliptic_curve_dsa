from pathlib import Path
import json,hashlib,gzip,re,datetime
p=Path(__file__).parent;d=Path('research-output/overnight-20261014/product/repair57-production-sixteen-r1');s=(d/'product_repair57_body_inverse_probe.log').read_text()
assert int((d/'run.exit').read_text())==0 and 'running 1 test' in s and '1 passed; 0 failed' in s
assert s.count('REPAIR57_SIXTEEN_BDD_PROVED')==3 and s.count('independent_allq_correct=true')==48
assert 'original_slice_equal=true' in s
files={}
for f in sorted(d.glob('*')):
 if f.is_file():
  files[f.name]=hashlib.sha256(f.read_bytes()).hexdigest()
  if f.suffix=='.log':(p/('repair57-sixteen-'+f.name+'.gz')).write_bytes(gzip.compress(f.read_bytes(),mtime=0))
for f in [d/'receipt/receipt.json',d/'receipt/candidate.patch']:(p/('repair57-sixteen-'+f.name)).write_bytes(f.read_bytes());files[str(f.relative_to(d))]=hashlib.sha256(f.read_bytes()).hexdigest()
dataset=json.loads((p/'repair57-sixteen-interface-inputs.json').read_text());prime=2**256-2**32-977
assert len(dataset['cases'])==16
for c in dataset['cases']:
 l=c['letter'];T,B=int(c['T'],16),int(c['B'],16);weights=sum((1 if l[j]=='0' else -1)*(1<<j)for j in range(3));shift=3+int(l[3])+2*int(l[4]);assert (T+weights*B)*pow(1<<shift,-1,prime)%prime==int(c['expected'],16)
oldbad=[c['index']for c in dataset['cases']if int(c['old_native'],16)%prime!=int(c['expected'],16)];assert oldbad==[94]
r={'status':'FINITE_SIXTEEN_PAYLOAD_INTERFACE_PRIMITIVE_PROVED','qualified_score':None,'original_source':'c5bb1ec876db859a3f9f8a9052c140a145df834e','producer_inputs':16,'old_local_wrong_indices':oldbad,'new_local_wrong_indices':[],'dirty_classical_patterns':['all0','all1','A5'],'new_forward_ALLMR_variables':2128,'new_pair_ALLMR_variables':4343,'maximum_phase_size_bounds':[6,10],'original_old_complete_primitive_ops':24451,'original_old_emitted_slice_byte_equal':True,'allocator_entry':'Exact original production1234quantum/1575classical entry free pools/order','native_patterns':3,'kernel_sha256':hashlib.sha256((p/'repair57-frozen-bdd.rs').read_bytes()).hexdigest(),'dataset_sha256':hashlib.sha256((p/'repair57-sixteen-interface-inputs.json').read_bytes()).hexdigest(),'walk_log_sha256':dataset['walk_log_sha256'],'scope':'Actual recorded T/B/letter interfaces; fixed mixed owned passengers and0/1/A5 all-classical initialization. Exact production allocator. Does not load literal whole-prefix quantum/classical snapshots and does not quantify prior MR or arbitrary fields.','log_letter_display':'05b numeric mask is displayed high-bit-first; dataset letter uses physical letter0..4 order. Do not equate the two string conventions.','failed_preparation':'Initial assumed16 adjacent export rows; actual known15 batch plus independent1 broke assertion before compilation/launch. Preserved failed-prepare source; corrected map key(source,mode,index,scope,seq+1).','artifact_hashes':files,'collected_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(p/'repair57-sixteen-evidence.json').write_text(json.dumps(r,indent=2)+'\n',newline='\n');print(json.dumps({k:r[k]for k in ['status','producer_inputs','old_local_wrong_indices','new_local_wrong_indices']},indent=2))
