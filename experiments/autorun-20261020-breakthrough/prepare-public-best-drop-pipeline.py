from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-public-rmin-context-20261020';r=a.parent/'breakthrough-public-best-drop-context-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore','patch-tool.py']:shutil.copyfile(old/n,r/n)
s=(old/'run.py').read_text();start=s.index(' start=time.time()\n while not(source/');end=s.index('\n of=json.loads',start)
selection=''' start=time.time();names=['breakthrough-public-drop-tradeoffs-20261020','breakthrough-public-drop-tradeoffs-v2-20261020']
 while not all((ws/n/'run.exit').exists()for n in names):assert time.time()-start<7200;time.sleep(2)
 choices=[]
 for name in names:
  src=ws/name;assert(src/'run.exit').read_text().strip()=='0';sf=json.loads((src/'SOURCE-FREEZE.json').read_text());assert all(sha(src/'observer'/p)==h for p,h in{**sf['source_files'],**sf['protected_files']}.items())
  for row in json.loads((src/'RESULT.json').read_text())['cases']:
   if row['exit']==0 and row.get('qubits')==1233:choices.append({'directory':name,'mode':row['mode'],'diagnostic_weight':row['diagnostic_weight'],'stream_sha256':row['stream_sha256'],'operations':row['operations'],'records_sha3':row['records_sha3'],'source_freeze_sha256':sha(src/'SOURCE-FREEZE.json')})
 assert choices;chosen=min(choices,key=lambda x:(x['diagnostic_weight'],x['directory'],x['mode']));assert chosen['diagnostic_weight']<=755911.0;source=ws/chosen['directory'];input=source/chosen['mode']/'ops.bin';assert sha(input)==chosen['stream_sha256'];(r/'RESOURCE-SELECTION.json').write_text(json.dumps({'status':'FIXED_GRID_STATIC_RESOURCE_SELECTION_BEFORE_POINT_INPUTS','choices':choices,'chosen':chosen,'scope':'Pure static resource criterion, no development/census/nonce inputs used. Counts diagnostic, not score.'},indent=2)+'\\n')
'''
s=s[:start]+selection.rstrip()+s[end:]
needle="'input_source_freeze_sha256':sha(source/'SOURCE-FREEZE.json'),";assert s.count(needle)==1;s=s.replace(needle,needle+"'input_constructor_directory':str(source),'input_constructor_mode':chosen['mode'],'input_constructor_operation_count':chosen['operations'],'resource_selection_sha256':sha(r/'RESOURCE-SELECTION.json'),")
ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Select the cheapest complete exact carry schedule before fresh point inputs

Wait for both predeclared fixed exact carry-drop grids. Among successful complete
Q1233 streams, select minimum static guard-depth Toffoli proxy, deterministic
directory/mode tie break. No development/census/nonce data is read. Freeze every
resource candidate, selection list and chosen source/stream before new exact
proofs. All native9/public/oldwidth/priorr1 controls must have passed their drivers.
Regenerate the same zero-wire16384-context proof with9 native controls; no old
cache table is copied. Pure component stage, no point gate/nonce/score.
Rmin source assembly remains preserved as an intermediate, with no gate verdict.
''')
old=a.parent/'breakthrough-public-rmin-finished-20261020';f=a.parent/'breakthrough-public-best-drop-finished-20261020';f.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore','cache-tests.rs']:shutil.copyfile(old/n,f/n)
s=(old/'run.py').read_text().replace('breakthrough-public-rmin-context-20261020','breakthrough-public-best-drop-context-20261020')
needle="pf=json.loads((proof/'SOURCE-FREEZE.json').read_text());";assert s.count(needle)==1;s=s.replace(needle,needle+"parent=Path(pf['input_constructor_directory']);assert parent.parent==ws and parent.name in ['breakthrough-public-drop-tradeoffs-20261020','breakthrough-public-drop-tradeoffs-v2-20261020'];assert sha(parent/'SOURCE-FREEZE.json')==pf['input_source_freeze_sha256'];")
s=s.replace("parent/'cap1233-rmin/ops.bin'","Path(pf['input'])").replace("==pf['input_sha256']=='0aa06d9cdfcdf7c0bf185a46ed1b2ce50404fce497d8e999d4c60f412a15466f'","==pf['input_sha256']").replace("count==p['input_count']==11720172","count==p['input_count']==pf['input_constructor_operation_count']")
needle="body=body.replace(mode,b'let mode=\"cap1233-rmin\".to_owned();');";assert s.count(needle)==1;s=s.replace(needle,"body=body.replace(mode,('let mode='+json.dumps(pf['input_constructor_mode'])+'.to_owned();').encode());")
s=s.replace('public_rmin_cache','public_best_drop_cache').replace("'identity_nonce':0,'public_parent'","'identity_nonce':0,'fixed_resource_mode':pf['input_constructor_mode'],'constructor_source_freeze_sha256':pf['input_source_freeze_sha256'],'resource_selection_sha256':pf['resource_selection_sha256'],'public_parent'")
s=s.replace('Fixed complete public-derived cap1233-rmin exact carry-schedule constructor','Fixed complete public-derived resource-selected Q1233 exact carry-schedule constructor');ast.parse(s);(f/'run.py').write_text(s)
(f/'PLAN.md').write_text('''# Freeze the statically selected exact carry-schedule product candidate

Depend on completed best-drop-context proof and immutableRESOURCE-SELECTION,
chosen solely by complete static resources across the fixed declared grids.
Verify source/17protected/whole-input hashes, set that mode as a literal, rename
entrypoint, add literal exact proof rewriter/new table, and bind every original
and new prefix record. Sameparent21bit witness and original windows/rounds;
resource-derived replay differences disclosed. Sourcefreeze before native
runtime phase/guard/RNG/fault control and full generation/protectedQ1233 audit.
No old cache rows or correctness verdicts transported. Intermediate rmin remains
preserved and ungated; it may be superseded solely by better exact resources.

Fresh full-output development on this final finished source precedes its own
one-shot finalgate against exact currentpublicacd0. Plan final131072x64/source,
one fresh label declared before census; no relabel/rerun/extension of a verdict.
Qualified ascendingnonce and unchanged9024benchmark/localmember review precede
authorized automatic GPT-6sol/Codex submission of any current-record improvement.
No claimed record from proxy counts or component tests.
''');print(r);print(f)
