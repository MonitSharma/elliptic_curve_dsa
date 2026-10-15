from pathlib import Path
import json,re
root=Path(__file__).resolve().parent;results=[]
old=root/'native-baseline-comparison.json'
if old.exists() and not (root/'native-baseline-comparison-initial-parser.json').exists():(root/'native-baseline-comparison-initial-parser.json').write_bytes(old.read_bytes())
for name in ['parent-all-tests.log','cap1792-tests.log']:
 s=(root/name).read_text();m=re.search(r'test result: FAILED\. (\d+) passed; (\d+) failed',s);assert m
 names=sorted(set(re.findall(r'^    (point_add::[A-Za-z0-9_:]+)$',s,re.M)));assert len(names)==int(m[2])
 results.append({'log':name,'passed':int(m[1]),'failed':int(m[2]),'failed_test_names':names})
same=results[0]['failed_test_names']==results[1]['failed_test_names']
out={'results':results,'same_failed_test_names':same,'status':'inherited_native_failure_names_identical' if same else 'new_native_failure_requires_investigation','scope_correction':'Broad suite selected initially; retain raw failures. Use six dynamic_pool_tests plus complete fresh source census for the cap-only configuration study.'}
old.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));assert same
