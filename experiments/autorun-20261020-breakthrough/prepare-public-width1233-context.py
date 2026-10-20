from pathlib import Path
import ast
a=Path(__file__).parent;old=a.parent/'breakthrough-stackv3-plan7-context-clean-20261020';r=a.parent/'breakthrough-public-width1233-context-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore','patch-tool.py']:(r/n).write_bytes((old/n).read_bytes())
s=(old/'run.py').read_text().replace("source=ws/'breakthrough-stackv3-plan7-generic-v2-20261020'","source=ws/'breakthrough-public-acd0-exact-width-20261020'")
start=s.index(' start=time.time()\n while not(source/');end=s.index('\n of=json.loads',start)
s=s[:start]+''' start=time.time()
 while not(source/'run.exit').exists():assert time.time()-start<7200;time.sleep(2)
 assert(source/'run.exit').read_text().strip()=='0';sf=json.loads((source/'SOURCE-FREEZE.json').read_text());a=next(v for v in json.loads((source/'RESULT.json').read_text())['cases']if v['mode']=='cap1233-t21');assert a['exit']==0 and a['qubits']==1233;assert all(sha(source/'observer'/p)==h for p,h in{**sf['source_files'],**sf['protected_files']}.items());input=source/'cap1233-t21/ops.bin';assert sha(input)==a['stream_sha256']=='52a065e97ec0cf5159dd52da0df18b427bd906fbbc588028fe750d82c25e3c54'
'''.rstrip()+s[end:]
ast.parse(s);(r/'run.py').write_text(s);(r/'PLAN.md').write_text('''# Exact zero-added-wire caches on complete public-width1233 source

Fixedinputcap1233-t21 stream52a065e9/source7499-derived exactwidth prototype,
protectedanalyzerQ1233, fullnative8/publicbytecontrolPASS. Not benchmarked or
scored. Preservepublic21bitwitness/windows. Same fixed16,384-op samelexicalscope
exactBoolean proof,9nativecontrols, arbitrarycut donorzero proof,0extraQ.
No oldtableindices, gate, nonce or packet reused. All acceptedproducts/zero
donors provedexactly; fingerprintsnominateonly; strictno-touch/nonoverlap.
Nativequantum/phase/guard/fault tests precede scan. Componentonly. If useful,
finishedsource mustbindwholeinput/newoutput andhaveownfreshcurrentpublicproduct
gate, qualifiednonce, unchangedbenchmark/localreview beforeautoupload.
''');print(r)
