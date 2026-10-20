from pathlib import Path
import ast,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-grouped-resource-development-20261020';r=ex/'breakthrough-exact-witness-development-20261020';r.mkdir(exist_ok=False)
for n in['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
s=(old/'run.py').read_text().replace('breakthrough-grouped-exact-resource-grid-v2-20261020','breakthrough-exact-witness-ripple-v3-20261020').replace("result['native_controls']==34","result['native_components']==5 and result['group_plan_controls']==1 and all(x['exit']==0 for x in result['fullsquare_units'])")
start=s.index(";assert next(x for x in result['cases']if x['mode']=='control')");end=s.index('\n for row in result',start)
s=s[:start]+''';assert next(x for x in result['cases']if x['mode']=='groups-safe28-d12')['stream_sha256']=='f8c83372543408f90dfad942341a03fff81876878af53815bdb7a99f62f7dc84';paths={'public2bd':ws/'breakthrough-depth12-final-20261020/candidate/ops.bin'};assert sha(paths['public2bd'])=='63370be6078a4a80454d5174a5f07bfac094fea6af3dd526f77dc8194012cc29';receipt=json.loads((ws/'breakthrough-depth12-final-20261020/PUBLIC-SOURCE-VERIFICATION.json').read_text());assert receipt['public_source_revision']=='36e37af06d56bade9bfaedc0a252a81bbe3858b8'and receipt['exact_parent_stream_sha256']==sha(paths['public2bd'])''' +s[end:]
s=s.replace("row['exit']==0 and row['mode']!='control'","row['exit']==0").replace('grouped-resource-grid-development-20261020-v1','exact-witness-resource-development-20261020-v1')
s=s.replace('Fresh full-output development of the predeclared exact square-depth/workspace grid.','Fresh full-output actual-resource development of predeclared exact full259 witness consolidation/sharedsum/cap grid. Five nativecomponent controls/group1 andall5fullsquarecaller units pass; exactf8c833control.').replace('currentT71','currentT2bd')
needle="subprocess.run(['python3',str(r/'diagnostic.py')],cwd=r,check=True);(r/'controller.exit').write_text('0\\n')"
replacement="""subprocess.run(['python3',str(r/'diagnostic.py')],cwd=r,check=True);d=json.loads((r/'DIAGNOSTIC.json').read_text());choices=sorted([{'mode':x['mode'],'qubits':x['qubits'],'mean_executed_toffoli':d['summaries'][x['mode']]['mean_executed_stream_toffoli'],'stream_sha256':x['stream_sha256']}for x in result['cases']if x['exit']==0],key=lambda x:(x['mean_executed_toffoli'],x['qubits'],x['mode']));selected=choices[0];(r/'RESOURCE-SELECTION.json').write_text(json.dumps({'status':'FIXED_EXACT_ARCHITECTURE_SELECTED_BY_ACTUAL_RESOURCE_ONLY_NOT_SCORED','choices':choices,'selected':selected,'selection_policy':'minimum measured meanT, thenQ, thenmode; no candidate orcut tuning toinput failures. Alloutcomes preserved; no finalgate/nonce/score. Selected dirty/mismatched source must stop for diagnosis, never quietlychooseanother.','plan_sha256':sha(r/'PLAN.json'),'diagnostic_sha256':sha(r/'DIAGNOSTIC.json'),'source_freeze_sha256':sha(source/'SOURCE-FREEZE.json')},indent=2)+'\\n');assert not d['summaries'][selected['mode']]['dirty_shots'];(r/'controller.exit').write_text('0\\n')"""
assert s.count(needle)==1;s=s.replace(needle,replacement);ast.parse(s);(r/'run.py').write_text(s)
s=(old/'diagnostic.py').read_text().replace('breakthrough-grouped-exact-resource-grid-v2-20261020','breakthrough-exact-witness-ripple-v3-20261020').replace('public71','public2bd');ast.parse(s);(r/'diagnostic.py').write_text(s)
(r/'PLAN.md').write_text('''# Predeclared actual-resource comparison of exact full-width arithmetic grid

After allfixed native5/group1/fullsquarecaller5 controls andcompletegeneration,
verifyeach frozenstream/source/protectedfile andexactf8c833control. Onefreshlabel
exact-witness-resource-development-20261020-v1,512x64/source,4workers and8protected
scalarbatches each, against exactpublishedcurrentT2bd/63370be6. Compareall5fixed
cases includingprecachedcontrol, preserveallvalue/phase/dirty/otherdifferences.
Selectminimum actualmeanT, tieQthenmode, BEFORE freshproof/finalsource/finalgate
andnonce. No precision/cut/round changes, no source selectedbytuning failures.
If selectedsource showsdirty/contradictory values, stopfordiagnosis; neverquietly
selectanother. Diagnostics are notscores. Regeneratecontextproofs/wholebindings,
freeze selectedsource andfreshliteral0, then OWN finalgate vs exactthen-current
Toffolirecord, qualifiednonce/full9024benchmark/localreview beforeautoupload.
''');print(r)
