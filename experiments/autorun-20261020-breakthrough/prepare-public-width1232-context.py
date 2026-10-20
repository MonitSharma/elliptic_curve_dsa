from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-public-width1233-context-20261020';r=a.parent/'breakthrough-public-width1232-context-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore','patch-tool.py']:shutil.copyfile(old/n,r/n)
s=(old/'run.py').read_text().replace('breakthrough-public-acd0-exact-width-20261020','breakthrough-public-prefix27-width-v2-20261020');start=s.index(' start=time.time()\n while not(source/');end=s.index('\n of=json.loads',start)
s=s[:start]+''' start=time.time()
 while not(source/'stats-cap1232-t21.exit').exists():assert time.time()-start<7200;time.sleep(2)
 assert(source/'stats-cap1232-t21.exit').read_text().strip()=='0'and(source/'generate-cap1232-t21.exit').read_text().strip()=='0';sf=json.loads((source/'SOURCE-FREEZE.json').read_text());assert all(sha(source/'observer'/p)==h for p,h in{**sf['source_files'],**sf['protected_files']}.items());input=source/'cap1232-t21/ops.bin';assert sha(input)=='2df5a2152647d8a76c6444d17ac5c678e54cccba6775a287bb151c725c41dda5';a=json.loads((source/'cap1232-t21-STATS.json').read_text());assert a['qubits_protected_analyzer']==1232
'''.rstrip()+s[end:]
s=s.replace("proof['peak_qubits']==1233","proof['peak_qubits']==1232").replace('x[2]<1233','x[2]<1232').replace("st['qubits_protected_analyzer']<=1233","st['qubits_protected_analyzer']<=1232").replace("'input_qubits':1233","'input_qubits':1232");ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Exact existing-wire cache proof on complete prefix27 width1232 stream

Frozen source public-prefix27-v2/cap1232-t21, frame2df5a215, protectedQ1232,
native14 plus exact public3d7c/cap1233/52a0 controls. Sameparent21bit witness,
resource-derived replay changes and no fullcurve correctness claim. The complete
case has its own successful generation/stats markers even while independent
fixed grid cases continue. No case file or source is mutated by this tool.
Fixed16384 samelexical arbitrary-cut proof, zero added quantum wires and all9
native guard/phase/RNG/fault controls before scanning. No old table carried.
Component only; fresh pointdevelopment/sole finalgate/nonce/benchmark required
on a finished bound source before any official resource claim or submission.
''');print(r)
