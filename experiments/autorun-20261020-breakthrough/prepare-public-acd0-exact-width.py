from pathlib import Path
import ast,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-stackv3-width-plan7-both-20261020';r=ex/'breakthrough-public-acd0-exact-width-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore','additional-tests.rs']:(r/n).write_bytes((old/n).read_bytes())
phase=(a/'phase-compare-compact.rs').read_text().replace('super::phase_fit::cap()','super::pingpong::walk_max_qubits()').replace('// The omitted allocated carry originally consumed BOTH an R and an HMR draw.','// Each omitted carry removes its HMR and its release-time R draw.');(r/'phase-compare-compact.rs').write_text(phase)
s=(old/'prepare.py').read_text();s=s.replace('import hashlib,json,shutil,subprocess','import hashlib,json,shutil,subprocess,time').replace("base='88869d8cc23fb72120dd52533f3e48277e9b36e4'","base='7499c902d7989e5a995ccd2331104a532197851b'")
needle=';assert not t.exists();';assert s.count(needle)==1;s=s.replace(needle,";parent=ws/'breakthrough-public-acd0-reproduction-20261020';deadline=time.time()+7200\nwhile not(parent/'run.exit').exists():assert time.time()<deadline;time.sleep(2)\nassert(parent/'run.exit').read_text().strip()=='0';parent_result=json.loads((parent/'RESULT.json').read_text());assert parent_result['public_source_revision']==base and parent_result['Q']==1234 and parent_result['T']==756265\nassert not t.exists();")
s=s.replace("(ws/'breakthrough-public322-square-final-20261020/SOURCE-FREEZE.json')","(parent/'SOURCE-FREEZE.json')")
needle='"cap1233-t28"=>Some((1233,28)),"cap1232-t28"=>Some((1232,28))';assert s.count(needle)==1;s=s.replace(needle,'"cap1233-t21"=>Some((1233,21)),"cap1232-t21"=>Some((1232,21)),"cap1233-t28"=>Some((1233,28))')
s=s.replace("+needle+b'\\n    if config.is_some(){return ops;}'", "+needle")
assert 'if config.is_some(){return ops;}' not in s
needle="std::env::set_var(\"SQC_T\",top.to_string());}";assert s.count(needle)==1;s=s.replace(needle,'std::env::set_var("SQC_T",top.to_string());std::env::set_var("TAIL_NONCE","0");std::env::set_var("EXACT_CMP_COMPACT","1");}else{std::env::set_var("EXACT_CMP_COMPACT","0");}')
needle="assert all(sha(t/p)==h for p,h in protected.items());prior=";assert s.count(needle)==1
extra='''p=t/'src/point_add/mod.rs';raw=p.read_bytes();raw+=b'\\nmod phase_compare_compact;\\n';p.write_bytes(raw);(t/'src/point_add/phase_compare_compact.rs').write_bytes((r/'phase-compare-compact.rs').read_bytes())
p=t/'src/point_add/compare.rs';raw=p.read_bytes();needle=b'    if super::dirty_boundary_probe::try_tail(circ,u,v,borrow_in){return;}';assert raw.count(needle)==1;raw=raw.replace(needle,b'    if v0cl.is_none() && super::leapfrog::C35_PADS.with(|p|p.get())==0 && super::phase_compare_compact::try_run(circ,u,v,borrow_in){return;}\\n'+needle);p.write_bytes(raw)
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();needle=b'if swap01 { kk1 + Y15_GUARD + kk1 - 1 } else { k0 + Y15_GUARD + k0 - 1 + if close { kwin + Y20_G2 } else { 0 } }';assert raw.count(needle)==1;raw=raw.replace(needle,b'if swap01 { kk1 + Y15_GUARD + kk1 - 1 - if super::super::phase_compare_compact::enabled(){super::super::phase_compare_compact::max_saving(kk1)}else{0} } else { k0 + Y15_GUARD + k0 - 1 - if super::super::phase_compare_compact::enabled(){super::super::phase_compare_compact::max_saving(k0)}else{0} + if close { kwin + Y20_G2 } else { 0 } }');p.write_bytes(raw)
''';s=s.replace(needle,extra+needle)
s=s.replace("['public','cap1234-t21','cap1234-t28','cap1233-t28','cap1232-t28']","['public','cap1234-t21','cap1233-t21','cap1232-t21','cap1233-t28']").replace("'public_exact_sha256':'714c4e4c1c2c5c59544dcc3ade28587663b616d46a168b0fcd22a06c29c0916f'","'public_exact_sha256':parent_result['stream_sha256']").replace("First exact entire public control unchanged, then fixed raw-only width and strengthened28-bit witness probes. No old table/guard modified, no final gate/nonce/score.","Exact entire currentpublicacd0 control unchanged; fixed complete postprocessed width1234/1233/1232 with SAMEparent21bit witness, plus stronger28bit control. No witness/window/round cut lowered. New exactphasecomparator plus independently nativeplan7/originalloan128. Originalallpublicgeneric passes remain and rederivefromnewstream; no frozen_stack inpublicacd0. Own finalgate/nonce/benchmark stillrequired.")
ast.parse(s);(r/'prepare.py').write_text(s)
s=(old/'run.py').read_text();needle="f=json.loads((r/'SOURCE-FREEZE.json').read_text());assert run(";assert s.count(needle)==1;s=s.replace(needle,"f=json.loads((r/'SOURCE-FREEZE.json').read_text());assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','compact_compare_tests','--','--nocapture','--test-threads=1'],'comparator-tests')==0;assert 'test result: ok. 4 passed; 0 failed;'in(r/'comparator-tests.log').read_text();assert run(")
needle="   if mode=='public':assert row['stream_sha256']==f['public_exact_sha256'],'Full public control must reproduce714c4e4c'";assert s.count(needle)==1;s=s.replace(needle,"   if mode=='public':assert row['stream_sha256']==f['public_exact_sha256'],'Every current publicacd0 output byte must reproduce'\n   stats=r.parent/'breakthrough-stackv3-width-stats-20261020/tool/target/release/native_width_stats';assert run([str(stats),str(path),str(r/(mode+'-STATS.json'))],'stats-'+mode,r)==0;st=json.loads((r/(mode+'-STATS.json')).read_text());row.update(qubits=st['qubits_protected_analyzer'],diagnostic_weight=st['fair_guard_depth_proxy'],records_sha3=st['records_sha3'])")
s=s.replace('NEW_PUBLIC_NATIVE_RAW_WIDTH_GRID_NOT_SCORED','CURRENT_PUBLIC_ACD0_EXACT_COMPONENT_COMPLETE_WIDTH_GRID_NOT_SCORED');ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Same-precision exact width adaptation of the actual current product leader

Base exact publicacd0/source7499, unmodifiedparent benchmark mustreproducefirst.
No oldfrozenStack table remains inthispublicsource. Keepentireoriginalgeneric
postprocessing andallwindows/rounds/cuts. Fixedcases beforeinputsampling:
publicexactcontrol, cap1234-t21,cap1233-t21,cap1232-t21,cap1233-t28. T21 is the
UNCHANGEDparent witness; it is not lowered from28. T28 is a predeclared stronger
control. Widthcasesnonce0 only, no nonce search/benchmark atthis stage.

Port exactmeasuredprefix/reversibletail phasecompare withatleastonecleanprefix
carry, minimumneededcut, originalRNGdrawcountvia2kzeroHMRs. Usepublicwalkcap API,
no privatephase_fit dependency. Padsnonzero/v0classical optimization untouched.
y16 need_m reflects certifiedhelpercount; allotheroldguards untouched. Restore
originalexactconsumerloan128 andnative-verifiedbudget7/50bit/drop3 ladderonly
undernewdeclaredselector fwd130..136/rev124..126 forcap<1234. No guardweakened.
Comparator4plusladder/admission/fault4 nativecontrols precede fullpublicstream
bytecontrol andcomplete newpointgenerations/protectedQ/staticdiagnostics.

This targets product resources on originalrecordarithmetic, avoidingtheunneeded
strengtheningcost ofearlierQ1233-t28 line. Neverchoosebycorrectnesspackets or
retunearithmetictoanonce. Anycompetitivefrozenfinishedsource needsownfresh
development/sole32768x64finalgate against exactthen-currentpublicacd0 stream,
qualifiedascendingnonce, unchanged9024benchmark/localmember review beforeauto
GPT-6sol/Codex submission. No new scoredresult here. Preserveallfailedcases.
''');print(r)
