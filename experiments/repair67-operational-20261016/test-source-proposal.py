"""Pure source/in-memory scheduling tests: no prepare, build, launch or search."""
from pathlib import Path
import ast,json,hashlib
r=Path(__file__).resolve().parent
for p in r.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
decl=json.loads((r/'DECLARATION.json').read_text())
assert decl['total_screening_threads_max']==8 and decl['threads_each']*decl['workers']==8
assert not (r/'tool').exists() and not (r/'ACCEPTANCE.json').exists()
assert 'PROPOSAL_DISABLED=True' in (r/'coordinator.py').read_text()
assert 'exit 2' in (r/'run-search.sh').read_text()
assert 'exit 2' in (r/'build.sh').read_text()
# Apply ONLY string edits to a read-only reviewed precursor snapshot in memory.
source=(r.parent/'prefilter-20261015/repair67-composite-review-v1/packed_body.rs').read_text()
ns={'source':source}
tree=ast.parse((r/'prepare.py').read_text());started=False
for node in tree.body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='source' for t in node.targets):
  if isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and node.value.func.attr=='read_text':
   started=True;continue
  if started:exec(compile(ast.Module(body=[node],type_ignores=[]),'<string-edit>','exec'),{},ns)
 elif started and isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='needle' for t in node.targets):
  exec(compile(ast.Module(body=[node],type_ignores=[]),'<needle>','exec'),{},ns)
 elif started and isinstance(node,ast.Assert) and 'source.count' in ast.unparse(node):
  exec(compile(ast.Module(body=[node],type_ignores=[]),'<exact-count>','exec'),{},ns)
result=ns['source']
for required in ['const PROOF_ACCEPTED:bool=false;','assert!(PROOF_ACCEPTED,','guard_safe(&proposed)',
 'if pass{assert_eq!(protected_shots,9024);record_pass(packet.nonce);}',
 'bind_operational_args(first,count,lookahead)','threads<=2','count<=134217728',
 'Some(original.as_ref().unwrap().as_slice())','screened+=stop-window;record_window']:
 assert required in result,required
assert result.count('include!("search.rs");')==1
assert result.count('include!("guard.rs");')==1
cases=[]
for look in [1,9,4096]:
 ranges=sorted((1+(cycle*4+lane)*look,1+(cycle*4+lane+1)*look-1) for cycle in range(5)for lane in range(4))
 assert ranges[0][0]==1 and all(a[1]+1==b[0] for a,b in zip(ranges,ranges[1:]))
 assert ranges[-1][1]==20*look
 for best in [1,look,look+1,4*look,4*look+1,19*look+1]:
  cycle,lane=divmod((best-1)//look,4)
  required=[(cycle+(i<=lane))*look for i in range(4)]
  covered={n for i,rows in enumerate(required)for local in range(rows)for n in [1+(local//look*4+i)*look+local%look]}
  assert set(range(1,best+1)).issubset(covered)
  if required[lane]>0:
   prior=required.copy();prior[lane]-=look
   assert not all(v>=need for v,need in zip(prior,required))
  cases.append({'lookahead':look,'best':best,'required':required})
assert 1+134217728*4<2**48
census=json.loads((r/'FINAL-CENSUS-PLAN.json').read_text())
assert census['batches_per_source']==32768 and census['first_batch']==0
assert census['runner_sha256']=='790e92266ea67ec54ef701b2deed76fe8d0b766b411ca9eab877f82ae2c11a66'
report={'status':'PURE_SOURCE_TRANSFORM_PARTITION_PREFIX_AND_DISABLED_GATES_PASS','generated_body_in_memory_sha256':hashlib.sha256(result.encode()).hexdigest(),'prefix_cases':cases,'all_python_syntax_parse':True,'tool_prepared':False,'build_run_search_performed':False}
(r/'SOURCE-TESTS.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
print(json.dumps({k:v for k,v in report.items()if k!='prefix_cases'}))
