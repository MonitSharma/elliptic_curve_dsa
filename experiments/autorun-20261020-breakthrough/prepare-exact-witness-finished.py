from pathlib import Path
import ast,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-depth12-finished-20261020';r=ex/'breakthrough-exact-witness-finished-20261020';r.mkdir(exist_ok=False)
for n in['.gitattributes','.gitignore','cache-tests.rs']:shutil.copyfile(old/n,r/n)
shutil.copyfile(old/'base-runtime.rs',r/'base-runtime.rs')
s=(old/'run.py').read_text().replace('breakthrough-depth12-context-20261020','breakthrough-exact-witness-context-20261020').replace('breakthrough-grouped-exact-resource-grid-v2-20261020','breakthrough-exact-witness-ripple-v3-20261020').replace('depth12_resource_base','witness_resource_base').replace('depth12_context_cache','witness_context_cache')
start=s.index(" assert(proof/'run.exit').read_text()");end=s.index('\n count,whole,',start)
s=s[:start]+''' assert(proof/'run.exit').read_text().strip()=='0';a=json.loads((proof/'RESULT.json').read_text());pf=json.loads((proof/'SOURCE-FREEZE.json').read_text());p=json.loads((proof/'zero-donors.json').read_text());mode=pf['selected_mode'];nq=a['input_qubits'];assert a['native_controls']==9 and a['output_qubits']<=nq<=1664;assert all(sha(proof/'tool'/path)==h for path,h in pf['tool_source_files'].items());selection=json.loads((ws/'breakthrough-exact-witness-development-20261020/RESOURCE-SELECTION.json').read_text());assert mode==selection['selected']['mode']and sha(parent/mode/'ops.bin')==pf['input_sha256']==selection['selected']['stream_sha256'];assert sha(proof/'zero-donors.ops.bin')==a['output_stream_sha256']
''' .rstrip()+s[end:]
s=s.replace("parent/'groups-safe28-d12/ops.bin'","parent/mode/'ops.bin'").replace("parent/'groups-safe28-d12/raw.ops.bin'","parent/mode/'raw.ops.bin'").replace("max(x[1]for x in p['leases'])","max((x[1]for x in p['leases']),default=0)").replace('x[2]<1464','x[2]<nq')
needle="body=body.replace(mode,b'let square_mode=\"groups-safe28-d12\".to_owned();')";assert s.count(needle)==1
s=s.replace(";mode=b'let square_mode=std::env::var", ";mode_needle=b'let square_mode=std::env::var",1).replace('assert body.count(mode)==1;'+needle, "assert body.count(mode_needle)==1;body=body.replace(mode_needle,('let square_mode='+json.dumps(mode)+'.to_owned();').encode())")
needle="assert sha(rawfile)=='519806f725616045938c6e75db30efe094f49df3467a218399a8636ec022a19b';";assert s.count(needle)==1;s=s.replace(needle,"gridcase=next(v for v in json.loads((parent/'RESULT.json').read_text())['cases']if v['mode']==mode);assert sha(rawfile)==gridcase['raw_stream_sha256'];")
needle="assert hashlib.sha256(public_chain).hexdigest()==pfsource['upstream_public_files'][chain];group_tests=(parent/'group-tests.rs').read_bytes();";assert s.count(needle)==1;s=s.replace(needle,"origin=ws/'breakthrough-grouped-exact-resource-grid-v2-20261020';origin_f=json.loads((origin/'SOURCE-FREEZE.json').read_text());assert sha(origin/'SOURCE-FREEZE.json')==pfsource['parent_freeze_sha256'];assert hashlib.sha256(public_chain).hexdigest()==origin_f['upstream_public_files'][chain];group_tests=(origin/'group-tests.rs').read_bytes();")
needle="(t/chain).write_bytes(public_chain+b'\\n'+group_tests);";assert s.count(needle)==1
extra="""sqc=t/'src/point_add/sqc.rs';sqcdata=sqc.read_bytes();fault=b' if std::env::var("EXACT_WITNESS_TEST_FAULT").is_ok_and(|v|v=="1"){c.x(prod[0]);}';assert sqcdata.count(fault)==1;sqc.write_bytes(sqcdata.replace(fault,b' #[cfg(test)]\\n'+fault));"""
s=s.replace(needle,needle+extra)
s=s.replace("['src/point_add/mod.rs','src/point_add/sqc/chain_groups.rs']","['src/point_add/mod.rs','src/point_add/sqc/chain_groups.rs','src/point_add/sqc.rs']")
s=s.replace('assert!(nq<=1464);',"assert!(nq<='+str(nq)+');")
s=s.replace("'fixed_resource_mode':'groups-safe28-d12'","'fixed_resource_mode':mode,'public_polynomial_source':'3eefcf216ca37cba0ae3f56212d6b1302844a249','resource_selection_sha256':sha(ws/'breakthrough-exact-witness-development-20261020/RESOURCE-SELECTION.json')").replace("'public_parent':'71d9dc7e-550b-480d-8d9e-c2af1989c0d7'","'public_parent':'2bd0f979-ab55-4f91-8133-68a08febaa67'")
oldscope='Fixed exact depth12 on unchanged strong witness28/full259tail/exactsplits/public140/uniform+2/native rail/G6. Full raw/generic input/output bindings, no research raw dump or fault branch, freshly proved existing-wire cache table and no added quantum wires, checked inherited identity tail normalized to finalnonce0. Native34/proof9 retained and runtimecache/groupplan2 repeated. Own fresh full-output development/finalgate against exact currentT71, qualifiednonce and unchangedbenchmark required. No scored result.'
newscope='Selected fixed exact full259 witness consolidation/sharedsum architecture on strongwitness28/fullgroup tails/exactsplits/public140/uniform+2/native rail/G6. Exact8-value polynomial from public1829 extended from59tofull259 andguarded byoldg>=n. No new approximation/window/cut/round. Whole raw/generic/input/newcacheprefix bindings; new proof rows/no added cache wires; checked inherited identity tail/newliteral0. Production fault branch absent via cfg(test), research rawdump removed. Native5components/group1/full5caller retained; proof9 fresh; finishedruntime7 repeated. Ownfreshdevelopment/finalgate vs exactcurrentT2bd/qualifiednonce/unchanged9024benchmark required. No scored result.'
assert oldscope in s;s=s.replace(oldscope,newscope)
needle="assert counts==['1'];run(['/home/hclau/.cargo/bin/cargo'";assert s.count(needle)==1
replacement="""assert counts==['1'];
 for filt,expected in[('exact_witness_ripple_tests',4),('exact_shared_sum_tests',1)]:
  run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit',filt,'--','--nocapture','--test-threads=1'],'native-'+filt,env=env);assert f'test result: ok. {expected} passed; 0 failed;'in(r/('native-'+filt+'.log')).read_text()
 run(['/home/hclau/.cargo/bin/cargo'"""
s=s.replace(needle,replacement).replace("st['qubits_protected_analyzer']==1464","st['qubits_protected_analyzer']==a['output_qubits']").replace("'native_tests':2","'native_tests':7")
ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Freeze the selected exact full-width arithmetic and fresh cache proof

Waitforindependentproof9 on actual-resource-selected fixed architecture. Copy
entirefrozenconstructorsource, fixliteral mode, bindEVERYraw andgenericprefix
record, checkedinherited tail, everycompletecacheinput/newcacheoutputprefix.
Nevertransportold230rows. Zeroaddedcachewires; actualQ fromprotectedanalyzer.
Retain ALLfull259 witness/correction/fullgroup tails, strong28witness/windows/
rounds/exactsplits. Exactpolynomial creditpublic1829, fullwidthextensionours.

Restoreoriginalfullpublicgroupcode withoutresearchfault; witnessfault only
cfg(test), absentproduction. Originalrawdump pathinactive, privategenericonce.
Decode/removeactualoldnonce thenappendliteral0; no processnonceassumption.
Source/17protected freeze before cachephase/guard/fault1, witness4, sharedsum1,
groupplan1=7runtime nativecontrols. Fullgeneration mustreproduce allbindings/Q.
No finalgate/nonce/benchmark/score. Freshfinisheddevelopment thenOWNsole final
gate vs exactthen-currentT2bd, qualifiedascendingnonce/protected9024/unchanged
benchmark/localsource/evidence verification beforeauthorizedautoupload.
''');print(r)
