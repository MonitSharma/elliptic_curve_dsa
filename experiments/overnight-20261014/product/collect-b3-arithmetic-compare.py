"""Finite source-bound ordinary-point comparison; no phase alignment inference."""
from pathlib import Path
import hashlib, json, re
out=Path(__file__).parent;e=out.parents[2]/'research-output/overnight-20261014/product/b3-arithmetic-compare'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert(e/'run.exit').read_text().strip()=='0'
log=(e/'run.log').read_text();results=[];values={};failures={}
for line in log.splitlines():
 if line.startswith('B3_STAGE_DIAGNOSTIC '):
  f=dict(re.findall(r'(\w+)=(\S+)',line));results.append({k:int(v)if v.isdigit()else v for k,v in f.items()})
 elif line.startswith('B3_STAGE_SHOT '):
  f=dict(re.findall(r'(\w+)=(\S+)',line));key=(f['stage'],f['mode'],int(f['index']));values[key]=(f['x'],f['y']);failures[key]=f['x_bad']=='true'or f['y_bad']=='true'
assert len(results)==6
keys={(mode,index)for stage,mode,index in values}
assert len(keys)==271
same=all(values[('c5_raw',m,i)]==values[('positive_bias_raw',m,i)]for m,i in keys)
changed=[{'mode':m,'index':i,'c5':values[('c5_raw',m,i)],'b3':values[('b3_raw',m,i)],'c5_fails':failures[('c5_raw',m,i)],'b3_fails':failures[('b3_raw',m,i)]}for m,i in sorted(keys)if values[('c5_raw',m,i)]!=values[('b3_raw',m,i)]]
receipt={'status':'completed_three_source_native_arithmetic_diagnostics','qualified_score':None,
 'stage_results':results,'all271_C5_original_and_positive_bias_value_pairs_equal':same,
 'B3_value_pairs_differ_from_C5':changed,
 'scope':'Same15known B3 candidateofficial failing pointtuples plus256independent;rawbeforeANYpostpass;curveexpectedvalues recomputed;stages allowed differing nq/nb/R/Hmr.',
 'source_streams':['C5raw eca53f6002583b148973ec0ebfb453839038b92984e3356bec8e24e6c662e683','B3raw ada7ef5264de0d6e600707c2e0672593014006038e454c24e6c74b19b7ca5e10','positivebiasC5raw f6b272fc274c47db4d5a8f135144acd00582b9cf31022d18fb48e1cd262c346a'],
 'measurement_alignment':'NONE;freshfixedstartdomain, varyingMRconsumption. Phase counts are diagnostic and cannot establish introduced/repairedphase.',
 'native_sha256':(e/'native.sha256').read_text().split()[0],
 'files_sha256':{p.name:sha(p)for p in e.iterdir()if p.is_file()},
 'limitations':['Positivebiasrawsource is an unbound arithmetic diagnostic with final101bindingfailure previouslypreserved, Q1238worse;not a candidate record.','Noordinarypointrepair is demonstrated:14knownfails+1independent persist inC5 andpositivebias undertested domain.','No16bitleaf-density inference, nonce/packet tuning, benchmarkrepeat orprotectedfile changes.','Finite values do not proveglobalexactness;phaseallMRproducerproofs remain separate.']}
(out/'b3-arithmetic-compare-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',newline='\n')
print(json.dumps({'C5_positive_equal':same,'B3_C5_differences':changed,'results':results},indent=2))
