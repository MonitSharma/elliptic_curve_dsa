"""Collect actual-prefix phase/ownership evidence and diagnostic component cost."""
from pathlib import Path
import collections, hashlib, json, re
out=Path(__file__).parent
e=out.parents[2]/'research-output/overnight-20261014/product/h45-prefix-proof'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
log=(e/'run.log').read_text();assert(e/'run.exit').read_text().strip()=='0'
assert'PRODUCT_H45_ORIGINAL_SLICES all105_byte_equal=true'in log
line=next(l for l in log.splitlines()if l.startswith('PRODUCT_H45_ACTUAL_PREFIX_TOTAL'))
fields=dict(re.findall(r'(\w+)=(\w+)',line))
totals={k:int(v)if v.isdigit()else v for k,v in fields.items()}
data=collections.defaultdict(list);family=collections.defaultdict(list)
for l in(e/'component-cost.tsv').read_text().splitlines():
 if l.startswith('#'):continue
 f,b,t,old,new,*_=l.split();delta=float(new)-float(old);data[int(t)].append(delta);family[(f,int(b))].append(delta)
assert len(data)==105 and all(len(v)==8 for v in data.values())
changes=[{'tick':k,'sample_delta_mean':sum(v)/len(v),'sample_delta_min':min(v),'sample_delta_max':max(v)}for k,v in sorted(data.items())if any(v)]
receipt={'status':'completed_source_bound_actual_prefix_allMR_proof','qualified_score':None,
 'baseline_revision':'c5bb1ec876db859a3f9f8a9052c140a145df834e',
 'raw_stream_sha256':'eca53f6002583b148973ec0ebfb453839038b92984e3356bec8e24e6c662e683',
 'source_original_components_all105_byte_equal_raw_slices':True,'proof_totals':totals,
 'scope':'256independent+256structured original-source native prefixes;105exact physicalfold contexts;old/new ALLMR componentproof plusnative liveclass/incomingphase comparison.',
 'free_classical_stale_patterns':['actual complete prefix slots','allunregistered>=512/free slots setall1','allunregistered>=512/free slots set0xa5a5a5a5a5a5a5a5'],
 'ownership':'actualfreeQ zero atentry;allfinalq equal independent integer model;everyliveclassslot unchanged;phase delta0forALLMR onfixedactualprefix;unused/freeclassslots need notretain values.',
 'summed_component_native_sample_delta_mean':sum(sum(v)/len(v)for v in data.values()),
 'summed_component_native_sample_delta_per_prefix_batch':{f'{f}:{b}':sum(v)for(f,b),v in sorted(family.items())},
 'changed_component_sample_deltas':changes,
 'cost_scope':'Diagnostic native samples on512fixedpoints andonecomponentMRdomain, noofficialmean/wholebodycost orscore;old/new mayconsumeMRs differently.',
 'native_sha256':(e/'native.sha256').read_text().split()[0],
 'export_receipt_sha256':sha(out/'h45-production-export-receipt.json'),
 'files_sha256':{p.name:sha(p)for p in e.iterdir()if p.is_file()},
 'limitations':['Finite fixedpoint allMR and fourhigher-word low-domain results do not prove global arbitraryhigher exactness.','Noallocatoradapter applied, nofullboundcandidate, noofficialscore.']}
(out/'h45-prefix-proof-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',newline='\n')
print(json.dumps({'totals':totals,'cost_delta':receipt['summed_component_native_sample_delta_mean'],'changes':changes},indent=2))
