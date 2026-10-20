from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-grouped-square-ports-20261020';r=a.parent/'breakthrough-grouped-exact-resource-grid-20261020';r.mkdir(exist_ok=True);assert not(r/'run.py').exists()
for n in ['.gitattributes','.gitignore','group-tests.rs']:shutil.copyfile(old/n,r/n)
modes=['control','groups-safe28-d8','groups-safe28-d12','groups-safe28-d16','groups-safe28-d8-sq1536','groups-safe28-d8-walk1664']
s=(old/'prepare.py').read_text();s=s.replace('["control","groups-safe28-d0","groups-safe28-d8"]','["control","groups-safe28-d8","groups-safe28-d12","groups-safe28-d16","groups-safe28-d8-sq1536","groups-safe28-d8-walk1664"]').replace("['control','groups-safe28-d0','groups-safe28-d8']",repr(modes))
needle='std::env::set_var("SQC_LEAF_D",if square_mode=="groups-safe28-d8"{"8"}else{"0"});';assert s.count(needle)==1;s=s.replace(needle,'std::env::set_var("SQC_LEAF_D",if square_mode=="control"{"0"}else if square_mode.contains("d12"){"12"}else if square_mode.contains("d16"){"16"}else{"8"});')
needle="p.write_bytes(raw);assert all(sha(t/p)==h for p,h in sf['protected_files'].items());";assert s.count(needle)==1
extra='''p.write_bytes(raw)
p=t/'src/point_add/mod.rs';raw=p.read_bytes();needle=b'let hard="1536".to_owned();';assert raw.count(needle)==1;raw=raw.replace(needle,b'let hard=if square_mode.ends_with("walk1664"){"1664"}else{"1536"}.to_owned();');needle=b'std::env::set_var("LF_SQUARE_CAP", "1408");';assert raw.count(needle)==1;raw=raw.replace(needle,b'std::env::set_var("LF_SQUARE_CAP",if square_mode.ends_with("sq1536"){"1536"}else{"1408"});');p.write_bytes(raw);assert all(sha(t/p)==h for p,h in sf['protected_files'].items());'''
s=s.replace(needle,extra)
ast.parse(s);(r/'prepare.py').write_text(s)
s=(old/'run.py').read_text();needle="pins='SQC_G1M='";assert s.count(needle)==1;s=s.replace(needle,"pins='PEBBLE_HARD_CAP='+('1664'if mode.endswith('walk1664')else'1536')+';SQC_G1M='")
needle="('8'if mode.endswith('d8')else'0')";assert s.count(needle)==1;s=s.replace(needle,"('0'if mode=='control'else'12'if'd12'in mode else'16'if'd16'in mode else'8')")
needle="params={'G3_UT_PINS':pins,'G3_UT_CAP':'1408'";assert s.count(needle)==1;s=s.replace(needle,"params={'G3_UT_PINS':pins,'G3_UT_CAP':('1536'if mode.endswith('sq1536')else'1408')")
needle="assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build')==0;results=[]";assert s.count(needle)==1
s=s.replace(needle,"\n for depth in[8,12,16]:\n  for width in[32,64]:\n   name=f'leaf-unit-d{depth}-m{width}';assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','sqleaf_unit','--','--nocapture','--test-threads=1'],name,extra={'SQC_LEAF_D':str(depth),'SQLEAF_M':str(width),'SQLEAF_BATCHES':'64'})==0;assert'test result: ok. 1 passed; 0 failed;'in(r/(name+'.log')).read_text()\n "+needle)
s=s.replace("'native_controls':28","'native_controls':34");ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Fixed exact square-depth and resource-cap grid on the strong Toffoli circuit

Retain every arithmetic comparison band, public140,28bit wrap witness/full259bit
correction, exact square splits, native rail/G6 and generic-once pipeline.
Fixed cases: olda871 control; exact current precache dc1478 d8 control; deeper
exact inverse-leaf d12/d16; squareworkspace1408->1536; walkresource1536->1664.
Q is free for the independentT objective. No narrower witness/approximation,
round/cut/nonce/packet tuning. Resource caps may change replay chunks, so full
point correctness is not assumed from component equivalence.

Prior27 exact controls and groupedplan1, G3 full square caller unit for each
case, retained six historical edge exclusions, separate junction-fault unit,
and six native inverse-leaf value/phase/cleanup roundtrips (D8/12/16,m32/64,
4096shots each) must pass before complete fixed generations. Controla871 must
be byteexact. New resources are diagnostic only. New stream needs regenerated
exact cache proofs, finished frozen source, own fresh finalgate vs currentT71,
qualified ascendingnonce/unchanged9024benchmark/localreview beforeautoGPT6sol
submission. Do not transport230 oldcache rows onto changed streams.
''');print(r)
