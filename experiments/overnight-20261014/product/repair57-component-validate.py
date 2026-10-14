"""Fail closed on wrong Cargo target/filter, missing markers, or test failure."""
from pathlib import Path
import json,re,sys,hashlib
p=Path(sys.argv[1]);results={}
for name,marker in [('product_repair57_actual104','REPAIR57_TOTAL'),('product_repair57_body_inverse_probe','REPAIR57_BODY_NATIVE')]:
 s=(p/(name+'.log')).read_text();rc=int((p/(name+'.exit')).read_text())
 result=re.search(r'test result: ok\. (\d+) passed;',s)
 valid=rc==0 and result is not None and int(result[1])==1 and 'running 1 test' in s and marker in s and 'product_repair57_tests::'+name in s
 results[name]={'status':'NAMED_TEST_EXECUTED' if valid else 'INVALID_OR_FAILED_VERIFICATION','exit':rc,'expected_test_count':1,'marker':marker,'marker_present':marker in s,'log_sha256':hashlib.sha256((p/(name+'.log')).read_bytes()).hexdigest()}
valid=all(r['status']=='NAMED_TEST_EXECUTED' for r in results.values())
(p/'verification.json').write_text(json.dumps({'status':'INTENDED_TESTS_EXECUTED' if valid else 'INVALID_OR_FAILED_VERIFICATION','qualified_score':None,'note':'Execution validation only; individual arithmetic/inverse/phase outcomes remain separately reported.','results':results},indent=2)+'\n')
print(json.dumps(results,indent=2));sys.exit(0 if valid else 1)
