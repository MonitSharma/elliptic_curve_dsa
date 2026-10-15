"""Separate the helper proof, failed integrated candidates, and oracle counterexample."""
from pathlib import Path
import re,json
root=Path(__file__).resolve().parent
result={'score':None,'official_benchmark_run':False,'status':'wrapper integration fails; helper proof passes','expected_exits':{'control':0,'wrapped':101,'observer':0},'candidates':{}}
for mode,rc in result['expected_exits'].items():assert int((root/(mode+'.exit')).read_text())==rc
for mode in ['control','wrapped']:
 generation=(root/(mode+'-generation.log')).read_text();families={}
 for family in ['independent','structured','candidate']:
  text=(root/(mode+'-'+family+'.log')).read_text();line=next(l for l in text.splitlines() if l.startswith('FIXED_DIAGNOSTIC'));data={k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',line)};data['wrong_indices']=list(map(int,re.findall(r'FINAL_BAD shot=(\d+)',text)));families[family]=data
 result['candidates'][mode]={'peak_diagnostic_only':int(re.search(r'HEO_TOTAL .*? peak=(\d+)',generation)[1]),'families':families,'stream_sha256':(root/(mode+'-stream.sha256')).read_text().split()[0]}
lines=(root/'observer.log').read_text().splitlines();result['interface_evidence']=[l for l in lines if l.startswith(('PAYLOAD_INTERFACE','PAYLOAD_OBSERVATION'))]
assert len(result['interface_evidence'])==11
result['diagnosis']='Injected divide input y=x returns a value other than1; retained zero flag remains1 after attempted uncomputation. Final clean-ancilla counts alone do not establish intermediate cleanup correctness.'
result['helper_proof']=[l for l in (root/'wrapped-tests.log').read_text().splitlines() if 'ZERO_EQUALITY_PROOF' in l or l.startswith('test result:')]
result['wrapped_phase_limit']='Exact BDD reports nonzero phase; native witness runner aborts on wrong point values before completing its certificate. Do not label this a native-verified phase counterexample.'
result['limitations']=['One fixed zero-slope input with all-zero measurements for interface observation.','Small-width helper proof is not a proof of the arithmetic oracle or complete wrapper.','Changing held flags can alter allocator-dependent arithmetic plans; an equal-input control without flags is still needed.','Diagnostic counts are not scored results.']
(root/'analysis.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'helper_proof':result['helper_proof']}))
