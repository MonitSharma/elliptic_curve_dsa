from pathlib import Path
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-public-e3-cache-development-v2-20261020';r=root/'experiments/breakthrough-public-e3-live-development-20261020';r.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore']:(r/p).write_bytes((old/p).read_bytes())
s=(old/'run.py').read_text();s=s.replace('breakthrough-public-e3-cache-finished-v2-20261020','breakthrough-public-e3-live-finished-20261020').replace("source/'resumed.exit'","source/'run.exit'").replace("a['native_tests']==18 and a['inherited_parent_tests_failed']==2","a['native_tests']==2 and a['inherited_parent_tests_failed']==2")
needle="'cache1234':source/'candidate/ops.bin'";assert s.count(needle)==1;s=s.replace(needle,"'cache1234':ws/'breakthrough-public-e3-cache-finished-v2-20261020/candidate/ops.bin','live1234':source/'candidate/ops.bin'")
s=s.replace("sha(paths['cache1234'])==a['stream_sha256']","sha(paths['cache1234'])=='93c7830ef7d19f63d342a9eabef1ec61abf50d12c4189751d09c063a5e4be176'and sha(paths['live1234'])==a['stream_sha256']")
s=s.replace('public-e3-exact-context53-development-20261020-v1','public-e3-cache-live-development-20261020-v1')
needle="subprocess.run(['python3',str(r/'diagnostic.py')],cwd=r,check=True)";assert s.count(needle)==1
s=s.replace(needle,needle+'''
 rows={n:[json.loads(x)for x in(r/(n+'.jsonl')).read_text().splitlines()]for n in['cache1234','live1234']};keys=['shots','value_shots','phase_shots','dirty_shots','failures','target_lane_hashes','other_lane_hashes'];assert len(rows['cache1234'])==len(rows['live1234'])==512;assert all(all(a[k]==b[k]for k in keys)for a,b in zip(rows['cache1234'],rows['live1234'])),'New exact parity pass must preserve full outputs/phase/RNG-relative states against cache53';(r/'EXACT-PAIR-VERIFICATION.json').write_text(json.dumps({'status':'ALL512_BATCHES_FULL_TARGET_OTHER_AND_FAILURE_PHASE_FLAGS_IDENTICAL_TO_CACHE53','compared_fields':keys,'cache53_rows_sha256':sha(r/'cache1234.jsonl'),'live_rows_sha256':sha(r/'live1234.jsonl'),'plan_sha256':sha(r/'PLAN.json')},indent=2)+'\\n');(r/'DEVELOPMENT-CONTROLLER.exit').write_text('0\\n')''')
s=s.replace(" (r/'run.exit').write_text('1\\n');raise"," (r/'run.exit').write_text('1\\n');(r/'DEVELOPMENT-CONTROLLER.exit').write_text('1\\n');raise")
(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Full fresh comparison and exact parity equivalence control

Single512x64 fresh comparison of exactpublice3/714c, cache53/93c783 and frozen
cache-plus-live-parity nonce0 source. Four workers/source, eight protected scalar
batches/source; labelpublic-e3-cache-live-development-20261020-v1. All fullsource,
proofs, output canonicalbindings and nativecontrols precede these inputs.
In addition to retaining all differences vs exactpublice3, require every target/
other quantumlane hash and every value/phase/dirty failure flag to be IDENTICAL
between cache53 and the parity output. These two sources have the same RNG
draws; any such difference blocks progression. Wait DEVELOPMENT-CONTROLLER.exit,
not the diagnostic child's run.exit, before declaring any final gate.
No finalgate/nonce/benchmark/score. Retain earlier512 development and all failed
preflights; no phase/failure label is optimized by circuit selection.
''');print(r)
