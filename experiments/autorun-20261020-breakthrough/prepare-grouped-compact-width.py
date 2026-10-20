from pathlib import Path
import ast,shutil,sys
root=Path(__file__).resolve().parents[2];ex=root/'experiments';old=ex/'breakthrough-grouped-square-caps-20261020';r=ex/(sys.argv[1] if len(sys.argv)>1 else 'breakthrough-grouped-compact-width-20261020');assert r.name in ['breakthrough-grouped-compact-width-20261020','breakthrough-grouped-compact-width-v2-20261020'];r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore','group-tests.rs']:(r/n).write_bytes((old/n).read_bytes())
shutil.copyfile(Path(__file__).parent/'phase-compare-compact.rs',r/'phase-compare-compact.rs');(r/'prepare-base.py').write_bytes((old/'prepare.py').read_bytes())
s='''import runpy,hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;runpy.run_path(str(r/'prepare-base.py'));t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();original=(r/'SOURCE-FREEZE.json').read_bytes();(r/'BASELINE-PREPARE-FREEZE.json').write_bytes(original);f=json.loads(original)
p=t/'src/point_add/mod.rs';raw=p.read_bytes();raw+=b'\\nmod phase_compare_compact;\\n';needle=b'    let mut ops = build_point_add();';assert raw.count(needle)==1;raw=raw.replace(needle,b'    std::env::set_var("EXACT_CMP_COMPACT",if square_mode=="control"{"0"}else{"1"});\\n'+needle);p.write_bytes(raw)
(t/'src/point_add/phase_compare_compact.rs').write_bytes((r/'phase-compare-compact.rs').read_bytes())
p=t/'src/point_add/compare.rs';raw=p.read_bytes();needle=b'    if super::dirty_boundary_probe::try_tail(circ,u,v,borrow_in){return;}';assert raw.count(needle)==1;raw=raw.replace(needle,b'    if v0cl.is_none() && super::phase_compare_compact::try_run(circ,u,v,borrow_in){return;}\\n'+needle);p.write_bytes(raw)
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();needle=b'if swap01 { kk1 + Y15_GUARD + kk1 - 1 } else { k0 + Y15_GUARD + k0 - 1 + if close { kwin + Y20_G2 } else { 0 } }';assert raw.count(needle)==1;raw=raw.replace(needle,b'if swap01 { kk1 + Y15_GUARD + kk1 - 1 - usize::from(kk1>=3 && super::super::phase_compare_compact::enabled()) } else { k0 + Y15_GUARD + k0 - 1 - usize::from(k0>=3 && super::super::phase_compare_compact::enabled()) + if close { kwin + Y20_G2 } else { 0 } }');p.write_bytes(raw)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());f['source_files']={p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()};f['change']='New exact n-2 carry terminal phase expansion only when old comparator peak exceeds cap. y16 cost records certified one-helper saving; no old arithmetic admission guard or precision cut weakened. Equal total measurement draws via zero-wire HMR. control disables all new behavior.';(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\\n');subprocess.run(['git','-C',str(t),'add','--intent-to-add','src/point_add'],check=True);(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD','--','src/point_add']))
'''
ast.parse(s);(r/'prepare.py').write_text(s)
s=(old/'run.py').read_text();needle="f=json.loads((r/'SOURCE-FREEZE.json').read_text());filters=";assert s.count(needle)==1;s=s.replace(needle,"f=json.loads((r/'SOURCE-FREEZE.json').read_text());assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','compact_compare_tests','--','--nocapture','--test-threads=1'],'compact-compare-tests')==0;assert 'test result: ok. 4 passed; 0 failed;'in(r/'compact-compare-tests.log').read_text();filters=")
s=s.replace("pins='PEBBLE_HARD_CAP='+hard+';SQC_G1M='","pins='EXACT_CMP_COMPACT='+('0'if mode=='control'else'1')+';PEBBLE_HARD_CAP='+hard+';SQC_G1M='").replace("'native_controls':28","'native_controls':32").replace("'prior_exact_native_controls':27","'prior_exact_native_controls':27,'compact_compare_controls':4").replace('native-grouped-square-lowcaps-20261020-v1','native-grouped-compact-width-20261020-v1')
ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Exact terminal phase expansion at the one-helper width cliff

Before inputs, freeze the same three stronger full259-tail/28-bit witness/exact
split square cases: full control, cap1234 and cap1233, inverseleaf depth8. Only
new behavior in lowcap cases: when the old phase comparison exceeds the cap,
replace penultimate carry by exact GF(2) identity
MAJ(x,y,MAJ(a,b,c))=xy+(x+y)ab+(x+y)(a+b)c. One CZ,two CCZs; one fewer clean
carry, one extra native Toffoli locally. No precision/window/witness/cut changes.
All operands restored and HMR phase repairs retained; two HMRs on knownzero
carry replace the omitted allocationR and HMR to preserve total random draws.
Originalv1 failed at equaldraw assertion before semantic comparisons; its broad
fault panic also caught that fixture failure. V2 retains it and tightens fault
expectation specifically to native compact phase contract. No statistical gate
was declared or run on either. y16 admission need_m uses new exact
helper count (minusone for n>=3), not a relaxed old guard. Other guards untouched.

Four new native controls precede27 inherited andgroupplan/square units: full
basis n3..6, arbitrary wider n7/22/56/128/256, independent/aliased source seed,
classicalguards, each measurement basis outcome, all value/phase/helper lanes,
strict one-qubit peak reduction/equaldrawcount; omitted cubicphase fault must
be detected; invalidaccumulator alias rejected. Control disables newroute and
must reproduce fulla871 stream byte-for-byte. Preserve all constructionfails.
Complete source/protected bindings/patch/native logs/raw+generic stream hashes
retained. No new finalgate, nonce or scoredresult. Finite tests are not proof
of complete universal point-addition correctness. Prior six square-domain edge
exclusions retained/disclosed. Nominal caps are not measured widths.
''')
print(r)
