from pathlib import Path
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-stackv3-plan7-development-20261020';r=root/'experiments/breakthrough-public-e3-cache-development-20261020';r.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore']:(r/p).write_bytes((old/p).read_bytes())
s=(old/'run.py').read_text();s=s.replace('breakthrough-stackv3-plan7-generic-v2-20261020','breakthrough-public-e3-cache-finished-v2-20261020').replace("a['native_tests']==14 and a['qubits']==1233","a['native_tests']==20 and a['qubits']==1234").replace('generic1233','cache1234').replace('stackv3-plan7-28-generic-development-20261020-v1','public-e3-exact-context53-development-20261020-v1').replace('fixed1233/t28 nativeplan7+generic once vs exactpublice3','fixed completepublice3 plus53 exactexisting-wire cacheleases vs exactpublice3')
(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Fresh full-output development of the complete public e3 cache

One512x64 fresh-input comparison, four workers and eight protected-scalar
batches/source, labelpublic-e3-exact-context53-development-20261020-v1. Source
and all53 lease rows frozen before sampling; complete parent and cache output
records bound. Exactpublic714c comparator. All original19 native tests plus
guardedcache test and9 independent proof controls precede generation. Preserve
all value/phase/dirty/full-output differences and actual executedstreamT.
No finalgate, nonce, benchmark or score. Resource means are developmental.
''');print(r)
