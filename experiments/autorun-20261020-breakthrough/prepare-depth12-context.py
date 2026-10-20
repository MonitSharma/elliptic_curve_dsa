from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-public-width1233-context-20261020';r=a.parent/'breakthrough-depth12-context-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore','patch-tool.py']:shutil.copyfile(old/n,r/n)
s=(old/'run.py').read_text().replace('breakthrough-public-acd0-exact-width-20261020','breakthrough-grouped-exact-resource-grid-v2-20261020');start=s.index(' start=time.time()\n while not(source/');end=s.index('\n of=json.loads',start)
s=s[:start]+''' start=time.time()
 while not(source/'run.exit').exists():assert time.time()-start<14400;time.sleep(2)
 assert(source/'run.exit').read_text().strip()=='0';sf=json.loads((source/'SOURCE-FREEZE.json').read_text());a=next(v for v in json.loads((source/'RESULT.json').read_text())['cases']if v['mode']=='groups-safe28-d12');assert a['exit']==0 and a['qubits']==1464;assert all(sha(source/'observer'/p)==h for p,h in{**sf['source_files'],**sf['protected_files']}.items());input=source/'groups-safe28-d12/ops.bin';assert sha(input)=='f8c83372543408f90dfad942341a03fff81876878af53815bdb7a99f62f7dc84'
'''.rstrip()+s[end:];s=s.replace("proof['peak_qubits']==1233","proof['peak_qubits']==1464").replace('x[2]<1233','x[2]<1464').replace("st['qubits_protected_analyzer']<=1233","st['qubits_protected_analyzer']<=1464").replace("'input_qubits':1233","'input_qubits':1464");ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Regenerate exact existing-wire caches on the fixed depth12 strong square

Fixed native34/fullsquare/fault-controlled depth12 streamf8c83372, Q1464, same
strong public140/uniform+2/witness28/full259tail/exactsplits/native rail/G6.
Predeclared512x64 full-output development of all fixed architectures completed:
no target/other/newvalue mismatches ordirty versuscurrent71, same21valuefails;
depth12 actualT747445.904 versus precachedepth8 747451.782,5.878fewer diagnostics.
Depth16 has no additional measured resource benefit; larger square/walk caps
produce identicaldc1478 stream. Select exact depth12 before any finalgate/nonce.

Regenerate every zero-added-wire lease on the fullnew stream with same fixed
16384samelexical arbitrary-cut proof and9native guard/phase/RNG/fault controls.
No230oldcache rows copied. Component only; new finished bound source and own
fresh finalgate vs exactcurrentT71, qualifiedascendingnonce/unchanged9024benchmark
andlocalreview required before auto official independentT-record submission.
''');print(r)
