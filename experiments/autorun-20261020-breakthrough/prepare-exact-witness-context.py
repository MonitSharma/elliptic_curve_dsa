from pathlib import Path
import ast,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-depth12-context-20261020';r=ex/'breakthrough-exact-witness-context-20261020';r.mkdir(exist_ok=False)
for n in['.gitattributes','.gitignore','patch-tool.py']:shutil.copyfile(old/n,r/n)
s=(old/'run.py').read_text().replace('breakthrough-grouped-exact-resource-grid-v2-20261020','breakthrough-exact-witness-ripple-v3-20261020')
start=s.index(' start=time.time()\n while not(source/');end=s.index('\n of=json.loads',start)
s=s[:start]+''' start=time.time();development=ws/'breakthrough-exact-witness-development-20261020'
 while not(development/'controller.exit').exists():assert time.time()-start<21600;time.sleep(3)
 assert(development/'controller.exit').read_text().strip()=='0';selection=json.loads((development/'RESOURCE-SELECTION.json').read_text());assert selection['source_freeze_sha256']==sha(source/'SOURCE-FREEZE.json');selected=selection['selected'];mode=selected['mode'];assert mode!='groups-safe28-d12','No new exact architecture beats the control resource diagnostic';sf=json.loads((source/'SOURCE-FREEZE.json').read_text());a=next(v for v in json.loads((source/'RESULT.json').read_text())['cases']if v['mode']==mode);nq=a['qubits'];assert a['exit']==0 and nq==selected['qubits']and nq<=1664;assert all(sha(source/'observer'/p)==h for p,h in{**sf['source_files'],**sf['protected_files']}.items());input=source/mode/'ops.bin';assert sha(input)==selected['stream_sha256']==a['stream_sha256']
''' .rstrip()+s[end:]
s=s.replace("proof['peak_qubits']==1464","proof['peak_qubits']==nq").replace('x[2]<1464','x[2]<nq').replace("st['qubits_protected_analyzer']<=1464","st['qubits_protected_analyzer']<=nq").replace("'input_qubits':1464","'input_qubits':nq")
s=s.replace("'input_source_freeze_sha256':sha(source/'SOURCE-FREEZE.json'),","'input_source_freeze_sha256':sha(source/'SOURCE-FREEZE.json'),'resource_selection_sha256':sha(development/'RESOURCE-SELECTION.json'),'selected_mode':mode,")
ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Fresh zero-added-wire cache proofs on the selected exact arithmetic

Wait for allfixed5native-correct architectures/fullf8c833 control andone fresh
actualresource development. Read immutable RESOURCE-SELECTION; minimummeanT,
tieQthenmode chosen solely byresource acrosspredeclaredexactarchitectures.
Verifyall selectedstream/source/17protected hashes; dynamic actualQ<=1664.

Regenerate same fixed16384same-lexical arbitrary-cut exactBoolean proof with
9native value/phase/capturedguard/mutation/RNG/alias/donor/fault controls. Zero
addedquantumwires; everyliteralcache row regenerated onnewstream, none copied.
Maxdonor andevery endpoint measured/proved, unknown expressions rejected. No
nonce orcorrectnessgate/score. Freshfinishedliteral source/wholebindings/
nonce0/native tests/fullpointdevelopment/ownfinalgate vs exactcurrentT2bd
must precedequalifiedascendingnonce/unchanged9024benchmark/localreview/autoupload.
''');print(r)
