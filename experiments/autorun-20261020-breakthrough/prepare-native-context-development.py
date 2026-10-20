from pathlib import Path
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-stackv3-plan7-development-20261020';r=root/'experiments/breakthrough-native-context-development-20261020';r.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore']:(r/p).write_bytes((old/p).read_bytes())
s=(old/'run.py').read_text();s=s.replace('breakthrough-stackv3-plan7-generic-v2-20261020','breakthrough-native-context-finished-v3-20261020').replace("a['native_tests']==14 and a['qubits']==1233","a['native_tests']==1 and a['independent_proof_controls']==7 and a['qubits']<=1480").replace("'publice3':ws/'breakthrough-stackv3-width-plan7-both-20261020/public/ops.bin'","'publicd182':ws/'breakthrough-native-both-final-20261020/candidate/ops.bin'").replace("paths['publice3']","paths['publicd182']").replace('714c4e4c1c2c5c59544dcc3ade28587663b616d46a168b0fcd22a06c29c0916f','cec71544f16da5598921a8a04e3b1416bda6f28d01878b1101ac724157a6f536').replace('generic1233','context499').replace('stackv3-plan7-28-generic-development-20261020-v1','native-context499-development-20261020-v1').replace("records['publice3']","records['publicd182']").replace("name=='publice3'","name=='publicd182'").replace('fixed1233/t28 nativeplan7+generic once vs exactpublice3','fixedexactcontext499 on complete officialT748691 parent')
# The inner copied diagnostic starts with publica4ee, and must target our named parent directly.
s=s.replace("records['publice3']","records['publicd182']").replace("name=='publice3'","name=='publicd182'")
needle="subprocess.run(['python3',str(r/'diagnostic.py')],cwd=r,check=True)";assert s.count(needle)==1;s=s.replace(needle,needle+";d=json.loads((r/'DIAGNOSTIC.json').read_text());assert d['summaries']['context499']['dirty_shots']==0;(r/'DEVELOPMENT-CONTROLLER.exit').write_text('0\\n')")
s=s.replace("(r/'run.exit').write_text('1\\n');raise","(r/'run.exit').write_text('1\\n');(r/'DEVELOPMENT-CONTROLLER.exit').write_text('1\\n');raise")
(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Fresh full-output development for context499

One512x64 fresh comparison, labelnative-context499-development-20261020-v1,
four workers/source, eight protectedscalar batches/source. Fixed complete
officiald182/cec715 parent versus frozen context499 nonce0 after sourcebound
generation/nativecache test and7 independent proof controls. Existing stronger
precision/native rail/G6 source retained;16 extra donors allowed for T objective.
Record all wrongvalue/phase/dirty/full-target/other-lane differences and actual
executedstreamT. Requirezero dirty before proceeding. No finalgate/nonce/score.
The original parent-source27 exact controls remain source-byte-identical.
''');print(r)
