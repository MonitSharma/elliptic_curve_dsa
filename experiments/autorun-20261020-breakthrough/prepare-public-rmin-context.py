from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-public-width1233-context-20261020';r=a.parent/'breakthrough-public-rmin-context-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore','patch-tool.py']:shutil.copyfile(old/n,r/n)
s=(old/'run.py').read_text().replace('breakthrough-public-acd0-exact-width-20261020','breakthrough-public-drop-tradeoffs-20261020');start=s.index(' start=time.time()\n while not(source/');end=s.index('\n of=json.loads',start)
s=s[:start]+''' start=time.time()
 while not(source/'stats-cap1233-rmin.exit').exists():assert time.time()-start<7200;time.sleep(2)
 assert(source/'stats-cap1233-rmin.exit').read_text().strip()=='0'and(source/'generate-cap1233-rmin.exit').read_text().strip()=='0';sf=json.loads((source/'SOURCE-FREEZE.json').read_text());assert all(sha(source/'observer'/p)==h for p,h in{**sf['source_files'],**sf['protected_files']}.items());input=source/'cap1233-rmin/ops.bin';assert sha(input)=='0aa06d9cdfcdf7c0bf185a46ed1b2ce50404fce497d8e999d4c60f412a15466f';a=json.loads((source/'cap1233-rmin-STATS.json').read_text());assert a['qubits_protected_analyzer']==1233
'''.rstrip()+s[end:];ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Exact zero-wire context proof on the improved exact carry schedule

Select first successfully constructed fixed rmin schedule by resource result
before any new point-input development: reverse drops1/2/3 versus original3/3/3,
same completeQ1233,17.75 fewer static proxyT, output0aa06d9c. Comparator4/plan4/
policy1 and exactpublic3d7c/old1233/52a0 full controls PASS. No window/witness21/
round/onefold-range change; all existing capacity/primitive guards preserved.
Regenerate every existing-wire lease on this full stream, fixed16384 same-scope
arbitrary-cut exact proof and9 nativecontrols; no113 old rows transported.
No point-input sampling/gate/nonce/score. If resource promising, freeze complete
bound source, own fresh finalgate against exact currentpublicacd0, qualified
ascendingnonce and unchanged9024benchmark/localreview before auto submission.
''');print(r)
