from pathlib import Path
import ast,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-grouped-square-ports-20261020';caps=ex/'breakthrough-grouped-square-caps-20261020';r=ex/'breakthrough-targeted-ripple-width-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore','group-tests.rs']:(r/n).write_bytes((old/n).read_bytes())
shutil.copyfile(a/'exact-ripple-target.rs',r/'exact-ripple-target.rs')
modes=['control','groups-safe28-d8','groups-safe28-d8-target1234','groups-safe28-d8-target1240','groups-safe28-d8-target1233']
s=(old/'prepare.py').read_text().replace('["control","groups-safe28-d0","groups-safe28-d8"]',repr(modes).replace("'",'"')).replace("['control','groups-safe28-d0','groups-safe28-d8']",repr(modes)).replace('square_mode=="groups-safe28-d8"','square_mode.contains("d8")');ast.parse(s);(r/'prepare-base.py').write_text(s)
s='''import runpy,hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;runpy.run_path(str(r/'prepare-base.py'));t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();original=(r/'SOURCE-FREEZE.json').read_bytes();(r/'BASELINE-PREPARE-FREEZE.json').write_bytes(original);f=json.loads(original)
p=t/'src/point_add/mod.rs';raw=p.read_bytes();raw+=b'\\nmod exact_ripple_target;\\n';needle=b'    let mut ops = build_point_add();';assert raw.count(needle)==1;raw=raw.replace(needle,b'    std::env::set_var("EXACT_RIPPLE_TARGET",match square_mode.as_str(){"groups-safe28-d8-target1234"=>"1234","groups-safe28-d8-target1240"=>"1240","groups-safe28-d8-target1233"=>"1233",_=>"0"});\\n'+needle);p.write_bytes(raw)
(t/'src/point_add/exact_ripple_target.rs').write_bytes((r/'exact-ripple-target.rs').read_bytes())
p=t/'src/point_add/modular.rs';raw=p.read_bytes();needle=b'    ripple_add_proved(circ, addend, acc, carry_in, carry_out, Carry0::Full, Carry1::Full, None, None, None, None);';assert raw.count(needle)==1;extra=b'    if circ.current_phase()=="divide" && carry_out.is_some() && GO_C0.with(|g|g.get()).is_none() && GO_COPY0.with(|g|g.get()).is_none() && !DSQ_KEEP.with(|g|g.get()) && DSQ_BITS.with(|g|g.borrow().is_empty()) && addend.len()==acc.len() && circ.active_qubits() as usize+acc.len().saturating_sub(1)<=walk_max_qubits() {if super::exact_ripple_target::try_run(circ,addend,acc,carry_in,carry_out){return;}}\\n';raw=raw.replace(needle,extra+needle);p.write_bytes(raw)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());f['source_files']={p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()};f['scope']='Fixed wide1536/square1408 grouped28/full259/exactsplits/depth8 circuit; new exact plain vented-ripple target caps onlyin divide. Original pinnedchunks/windows/rounds unchanged. Existing raw bridge algorithm, oneextraT perremovedhelper; zeroHMR padding equalsremovedHMR+releaseR draws. No carryconsumer, GO predictor/copy, deferredsquare, alias or oldcap-fitting branch replaced. Component/prototype, not finalgated or scored.';(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\\n');subprocess.run(['git','-C',str(t),'add','--intent-to-add','src/point_add'],check=True);(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD','--','src/point_add']))
''';ast.parse(s);(r/'prepare.py').write_text(s)
s=(caps/'run.py').read_text();needle="f=json.loads((r/'SOURCE-FREEZE.json').read_text());filters=";assert s.count(needle)==1;s=s.replace(needle,"f=json.loads((r/'SOURCE-FREEZE.json').read_text());assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','exact_ripple_target_tests','--','--nocapture','--test-threads=1'],'exact-ripple-tests')==0;assert 'test result: ok. 5 passed; 0 failed;'in(r/'exact-ripple-tests.log').read_text();filters=")
s=s.replace("cap='1408'if mode=='control'else('1234'if mode.endswith('1234')else'1233');hard='1536'if mode=='control'else cap;","cap='1408';hard='1536';").replace("'native_controls':28","'native_controls':33").replace("'prior_exact_native_controls':27","'prior_exact_native_controls':27,'exact_ripple_controls':5").replace('native-grouped-square-lowcaps-20261020-v1','native-targeted-ripple-widebaseline-20261020-v1')
needle="if mode=='control':assert row['stream_sha256']==f['control_expected_complete_nonce0_sha256'],'Full a871 control must reproduce exactly'";assert s.count(needle)==1;s=s.replace(needle,needle+"\n   if mode=='groups-safe28-d8':assert row['stream_sha256']=='dc1478c1ae14c86e6ab8f94d707599c5c74d5b861bb6dfb7e991a15d2a0d679d','Unchanged grouped baseline must reproduce every byte'")
ast.parse(s);(r/'run.py').write_text(s);(r/'PLAN.md').write_text('''# Target exact arithmetic workspace without changing the surrounding walk

Keep global1536/square1408, strengtheneduniform+2/public140, native rail/G6 and
grouped28/full259/exactsplits/depth8. Fivefixedcases before testinputs: olda871
control, unchangedgroupeddc1478 baseline, newplain-ripple target1234/1240/1233.
Only divide-phase ordinary vented equal-length register+register ripples are
eligible. All original special/result-top/bridge paths run first. Require no
GO_C0/GO_COPY0, no deferredsquare keep/pendingbits, oldfullplain ladderfits original
walkcap, disjointunique operands/cin/cout and at leastonecleanprefixcarry left.
No carryconsumer or approximationwindow/pinnedchunk/round/schedule changes.

Reuse existing exactbridge.raw_add measuredprefix/Cuccarotail with minimum
missinghelpers tofit localtarget, leaving globalrecipewide. Add2kzeroHMRs after
return toreplace omittedHMR+releaseR draws. Native5 checks allsmallbasis inputs,
everycut, arbitrarycinandventedoutput, guards, allquantum/phase/restoration,
strictpeakreduction, exactlyoneextra executedToffoli peromittedhelper, sameRNG
drawcount, everymeasurement/resetoutcome, omittedphasefault, alias/budgetreject
withoutoperations. Thenprior27/group/squarecontract units andfulla871/dc1478
controls before anynewcompletepointresourceinspection. Newprimitiveisexact;
existingoverall approximations stay. Allsources/patches/streams preserved.
No finalgate/nonce/benchmark/score. Anycompetitivecompletecandidate needs own
freshgate against exactcurrentpublicrecord, qualifiednonce, fullbenchmark and
localmember review before authorizedautomaticGPT-6sol/Codex submission.
''');print(r)
