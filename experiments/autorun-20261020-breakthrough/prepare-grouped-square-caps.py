from pathlib import Path
import shutil,py_compile
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-grouped-square-ports-20261020';r=root/'experiments/breakthrough-grouped-square-caps-20261020';r.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore','group-tests.rs']:shutil.copyfile(old/p,r/p)
s=(old/'prepare.py').read_text();s=s.replace('["control","groups-safe28-d0","groups-safe28-d8"]','["control","groups-safe28-d8-cap1234","groups-safe28-d8-cap1233"]').replace("['control','groups-safe28-d0','groups-safe28-d8']","['control','groups-safe28-d8-cap1234','groups-safe28-d8-cap1233']").replace('square_mode=="groups-safe28-d8"','square_mode.contains("d8")')
needle='p.write_bytes(raw);assert all(sha(t/p)==h for p,h in sf[\'protected_files\'].items());';assert s.count(needle)==1
extra='''p.write_bytes(raw)
p=t/'src/point_add/mod.rs';raw=p.read_bytes();needle=b'let hard="1536".to_owned();assert!(["1264","1400","1440","1536","1664"].contains(&hard.as_str()));';assert raw.count(needle)==1;raw=raw.replace(needle,b'let hard=match square_mode.as_str(){"groups-safe28-d8-cap1234"=>"1234","groups-safe28-d8-cap1233"=>"1233",_=>"1536"}.to_owned();if square_mode=="control"{assert!(["1264","1400","1440","1536","1664"].contains(&hard.as_str()));}else{assert!(["1234","1233"].contains(&hard.as_str()));}');needle=b'std::env::set_var("LF_SQUARE_CAP", "1408");';assert raw.count(needle)==1;raw=raw.replace(needle,b'std::env::set_var("LF_SQUARE_CAP",if square_mode=="control"{"1408"}else{&hard});');p.write_bytes(raw);assert all(sha(t/p)==h for p,h in sf['protected_files'].items());'''
s=s.replace(needle,extra);(r/'prepare.py').write_text(s)
s=(old/'run.py').read_text();s=s.replace("pins='SQC_G1M='","cap='1408'if mode=='control'else('1234'if mode.endswith('1234')else'1233');hard='1536'if mode=='control'else cap;pins='PEBBLE_HARD_CAP='+hard+';SQC_G1M='").replace("mode.endswith('d8')","('d8' in mode)").replace("params={'G3_UT_PINS':pins,'G3_UT_CAP':'1408'","params={'G3_UT_PINS':pins,'G3_UT_CAP':cap").replace("'G3_UT_PINS':'SQC_G1M=1;","'G3_UT_PINS':'PEBBLE_HARD_CAP=1536;SQC_G1M=1;")
s=s.replace("  if mode!='control':assert rc==0,'New grouped square must pass existing native unit contract before full construction'","  # A failed lower-cap unit remains a failed construction case and is not generated or scored.")
needle=" for mode in f['modes']:\n  dest=r/mode;";assert s.count(needle)==1;s=s.replace(needle," for mode in f['modes']:\n  u=next(x for x in unit if x['mode']==mode)\n  if mode!='control'and u['exit']:\n   results.append({'mode':mode,'exit':u['exit'],'status':'NATIVE_UNIT_CONSTRUCTION_OR_ARITHMETIC_FAILURE_NO_POINT_STREAM'});continue\n  dest=r/mode;")
s=s.replace('native-grouped-square-safe28-20261020-v1','native-grouped-square-lowcaps-20261020-v1');(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Product probe: stronger grouped-square circuit at1234/1233 budgets

The full1536/1408 grouped-safe28-d8 prototype passes native28 plus existing
square units and emits measuredQ1464 with diagnostic746373,2316 lower than its
exacta871 control. This is not scoredT. Test the same exact full259 correction,
28-bit witness, depth8 leaf and exact-square splits with both global and square
budgets1234 and1233. Keep uniform+2,public140,plainpool/native rail/G6 unchanged.
All original primitive cap/live-parent/scope assertions remain. Add two explicit
researchconfiguration cases; the old control's hard-budget admission remains
unchanged. Nominal budgets are not measuredQ and failed construction is no bound.

Fixedcases control(original1536/1408),groups-safe28-d8-cap1234,cap1233. Repeat27
native component controls plus groupedplan control. Each lowcap runs the square
unit at its own actualbudget before fullpoint generation. Preserve failedcases
and skip generating them; fullcontrola871 still mandatory. Independent junction
fault remains at1536/1408 and must fail. Source frozen before native inputs; all
raw/generic records and protected actualQ retained. No finalgate/nonce/score.
''')
for p in['prepare.py','run.py']:py_compile.compile(str(r/p),doraise=True)
print(r)
