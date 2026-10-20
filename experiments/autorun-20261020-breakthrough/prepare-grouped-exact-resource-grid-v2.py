from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-grouped-exact-resource-grid-20261020';r=a.parent/'breakthrough-grouped-exact-resource-grid-v2-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore','group-tests.rs','PLAN.md']:shutil.copyfile(old/n,r/n)
s=(old/'prepare.py').read_text();needle="p.write_bytes(raw);assert all(sha(t/p)==h for p,h in sf['protected_files'].items());";assert s.count(needle)==1
extra="p.write_bytes(raw)\np=t/'src/point_add/sqleaf.rs';raw=p.read_bytes();needle=b'        super::super::clear_process_env();';assert raw.count(needle)==1;raw=raw.replace(needle,needle+b'\\n        std::env::set_var(\"PEBBLE_HARD_CAP\",\"1536\");');p.write_bytes(raw);assert all(sha(t/p)==h for p,h in sf['protected_files'].items());"
s=s.replace(needle,extra);needle="if p not in['src/point_add/mod.rs','src/point_add/square.rs']";assert s.count(needle)==1;s=s.replace(needle,"if p not in['src/point_add/mod.rs','src/point_add/square.rs','src/point_add/sqleaf.rs']");ast.parse(s);(r/'prepare.py').write_text(s)
s=(old/'run.py').read_text().replace("'G3_UT_PINS':'SQC_G1M=1;","'G3_UT_PINS':'PEBBLE_HARD_CAP=1536;SQC_G1M=1;");ast.parse(s);(r/'run.py').write_text(s)
(r/'V2-SCOPE.md').write_text('''# Native fixture settings supplied before a new source freeze

V1 original run stopped at deliberate-fault fixture because its pins omitted
PEBBLE_HARD_CAP. A separate resumed driver restored that missing setting on
unchanged source and same fixed inputs: intended fault detected122 wrong outputs
and43 phase failures/128shots. It then stopped at the new leaf roundtrip because
that historical unit clears environment internally and omits the same independent
phase-cap setting before construction. Originalrun.exit1/resumed.exit1/logs stay.
Neither failed fixture reached a leaf arithmetic simulation; no point generation,
statistical gate or nonce ran. All five new full square callers and prior27/group
controls had passed. Original outcomes are not rejudged as passes.

V2 is a new frozen source: add PEBuilder1536 ONLY in cfg(test) sqleaf_unit after
its environment clear; retain all production arithmetic source and every guard.
Correct the fault-driver pins before launch. Repeat all prior controls, six full
square callers, independent deliberate-fault detection and six leaf roundtrips,
then unchanged fulla871/dc1478 controls and fixed grid. No seed/batch/window/round
changes, no packet tuning. Failed setup fixtures do not count as arithmetic or
statistical gate verdicts. No scored result until full independent verification.
''');print(r)
