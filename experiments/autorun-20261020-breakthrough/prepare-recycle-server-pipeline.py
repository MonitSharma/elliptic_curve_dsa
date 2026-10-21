from pathlib import Path
import hashlib,json,tarfile,subprocess
a=Path(__file__).resolve().parent;ex=a.parent;r=ex/'breakthrough-recycle-finished-v2-20261021';dev=ex/'breakthrough-recycle-finished-development-20261021';gate=ex/'breakthrough-recycle-final-gate-20261021';dev.mkdir(exist_ok=False);gate.mkdir(exist_ok=False);sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
mapping={'breakthrough-public-semantic-finished-20261021':r.name,'breakthrough-public-semantic-finished-development-20261021':dev.name,'breakthrough-public-semantic-final-gate-20261021':gate.name,'public1829-semantic-finished-development-20261021-v1':'ffe20-recycle-finished-development-20261021-v1'}
def adapt(s):
 for x,y in mapping.items():s=s.replace(x,y)
 return s
s=adapt((a/'run-public-semantic-server.py').read_text()).replace('tarfile,traceback','tarfile,traceback,time')
before="spec=json.loads((r/'SOURCE-SPEC.json').read_text());local=json.loads((r/'LOCAL-GENERATION.json').read_text());assert sha(r/'SOURCE-SPEC.json')==local['source_spec_sha256'];"
assert before in s;s=s.replace(before,"spec=json.loads((r/'SOURCE-SPEC.json').read_text());")
s=s.replace(",local_generation_sha256=sha(r/'LOCAL-GENERATION.json')",'')
s=s.replace('breakthrough-public1829-reproduction-20261020/candidate/target','breakthrough-de8-repeat-final-20261020/candidate/target').replace('breakthrough-public1829-reproduction-20261020/candidate/ops.bin','breakthrough-de8-repeat-final-20261020/candidate/ops.bin')
s=s.replace("'1234'","'1467'").replace('==1234','==1467').replace("'qubits':1234","'qubits':1467").replace('==11682054','==11292532').replace("'point_add::exact_semantic_product::tests'","'point_add::recycle_measurements::'").replace('4 passed;','14 passed;').replace("'native_tests':4","'native_tests':14").replace("'prior_independent_semantic_proof_controls':12","'prior_independent_semantic_proof_controls':11")
before=" assert all(sha(t/p)==h for p,h in{**freeze['source_files'],**freeze['protected_files']}.items());assert sha(t/'ops.bin')==local['stream_sha256'],'Crosscompiler must reproduce exact local frozen stream'"
after=""" deadline=time.monotonic()+10800
 while not(r/'LOCAL-GENERATION.json').exists():assert time.monotonic()<deadline;time.sleep(2)
 local=json.loads((r/'LOCAL-GENERATION.json').read_text());assert sha(r/'SOURCE-SPEC.json')==local['source_spec_sha256'] and local['native_controls']==14
 assert all(sha(t/p)==h for p,h in{**freeze['source_files'],**freeze['protected_files']}.items());assert sha(t/'ops.bin')==local['stream_sha256'],'Crosscompiler must reproduce exact local frozen stream'"""
assert before in s;s=s.replace(before,after).replace("'public1829':parent,'semantic':t/'ops.bin'","'official_ffe20':parent,'recycle':t/'ops.bin'")
s=s.replace('Freeze source-bound exact semantic CCX to CX at nonce zero','Freeze exact original-measurement recycling at nonce zero').replace('FINISHED_EXACT_SEMANTIC_NONCE0_CROSSCOMPILER_NATIVE4_COMPLETE_NOT_GATED_OR_SCORED','FINISHED_EXACT_RECYCLE_NONCE0_CROSSCOMPILER_NATIVE14_COMPLETE_NOT_GATED_OR_SCORED')
(r/'server-run.py').write_text(s)
s=adapt((ex/'breakthrough-public-semantic-finished-development-20261021/diagnostic.py').read_text()).replace("records['public1829']","records['official_ffe20']").replace("name=='public1829'","name=='official_ffe20'");(dev/'diagnostic.py').write_text(s)
s=(ex/'breakthrough-de8-repeat-final-gate-20261020/declare.py').read_text();s=s.replace('breakthrough-de8-repeat-finished-20261020',r.name).replace('breakthrough-de8-repeat-finished-development-20261020',dev.name).replace('breakthrough-exact-witness-final-20261020','breakthrough-de8-repeat-final-20261020').replace('cache-repeat-generic-final-20261020-v1','ffe20-exact-measurement-recycle-final-20261021-v1').replace("a['native_tests']==8","a['native_tests']==14").replace('src/point_add/repeat_generic_cache.rs','src/point_add/recycle_measurements.rs').replace("['comparisons']['generic']","['comparisons']['recycle']").replace("['summaries']['generic']","['summaries']['recycle']").replace('de8bac6a-afff-479e-b716-8cbf2dce6c73','ffe20d35-ecb7-47da-9dde-1b8d80ffde60').replace('746114','746112').replace('1092310896','1092307968').replace("pr['source_files']==205","pr['source_files']==206").replace('131712cc9c79e9ffd3ac60c07d097a29b5252c03afa95c891c5ecdd603c60c2e','9185ad8965bec47212849d3569e2e4ce4ef86a2e15d0248bee392107beac4927')
s=s.replace("assert comp['candidate_minus_parent_raw_toffoli']", "assert not comp['different_target_lanes'] and not comp['new_value_failing_shots'] and not comp['new_value_passing_shots'] and comp['new_failed_batches']==0 and comp['new_passing_batches']==0\nassert comp['candidate_minus_parent_raw_toffoli']",1)
s=s.replace('Sole finalgate for fixed exact2additionalcache plus secondgeneric circuit. Exact currentTde8 parent. Prior independentproof9 and finalnative8 retained.','Sole finalgate for full-prefix exact original-measurement recycling, 3 leases, source207/protected17. Exact current FFE Toffoli parent. Prior independentnative11/fresh48 complete protected phase/RNG/cleanhelper comparisons and finalnative14 retained.')
(gate/'declare.py').write_text(s)
s=adapt((ex/'breakthrough-public-semantic-final-gate-20261021/run.py').read_text());(gate/'run.py').write_text(s);(gate/'census.py').write_bytes((ex/'breakthrough-public-semantic-final-gate-20261021/census.py').read_bytes())
for folder in[dev,gate]:
 (folder/'.gitignore').write_text('*.jsonl\n__pycache__/\n');(folder/'.gitattributes').write_text('* -text\n')
(dev/'PLAN.md').write_text('# Fresh finished-source development\n\nLabel ffe20-recycle-finished-development-20261021-v1,512x64/source,4workers/source,8protectedscalarbatches. Frozen207source/native14/local-official1.93 byteequality first. Exact original FFE9185 comparator; all target/other hashes and failure identities preserved. No gate/nonce/score from development.\n')
(gate/'PLAN.md').write_text('# Prospective sole final gate\n\nLabel ffe20-exact-measurement-recycle-final-20261021-v1,32768x64/source,8workers/source,8protectedscalarbatches. Declare only after finished source207/protected17/native14/crosscompiler equality/fresh512development and refresh exact currentFFE T record. All4criteria, verdictFINAL. No nonce/benchmark beforePASS. Extra width acceptable for independentT objective; no globalproduct claim.\n')
for p in[r/'server-run.py',dev/'diagnostic.py',gate/'declare.py',gate/'run.py',gate/'census.py']:compile(p.read_text(),str(p),'exec')
selected=[r/n for n in ['SOURCE-SPEC.json','point-add-source.tar.gz','source.patch','server-run.py','PLAN.md']]+[p for folder in[dev,gate]for p in folder.iterdir()if p.is_file()]
bundle=a/'recycle-server-pipeline.tar.gz'
with tarfile.open(bundle,'w:gz')as ar:
 for p in selected:ar.add(p,arcname=p.relative_to(ex).as_posix(),recursive=False)
receipt={'archive_sha256':sha(bundle),'members':{p.relative_to(ex).as_posix():sha(p)for p in selected},'scope':'Source frozen before native14/generation/development/gate. Server runs official1.93 native14/generation, then waits for independently verified local receipt before bytecomparison/development/sole gate. Source-freeze immutable; no receipt or gate verdict exists at packaging. No nonce in controller.'};rp=a/'RECYCLE-PIPELINE-TRANSFER.json';rp.write_text(json.dumps(receipt,indent=2)+'\n')
s=adapt((a/'install-public-semantic-server.py').read_text()).replace('native4','native14');installer=a/'install-recycle-server.py';installer.write_text(s)
for p in[bundle,rp,installer]:subprocess.run(['scp','-o','BatchMode=yes',str(p),'smu_server:/home/hclau/ecdsa_research/'+p.name],check=True)
out=subprocess.check_output(['ssh','-o','BatchMode=yes','smu_server','python3','/home/hclau/ecdsa_research/'+installer.name,'/home/hclau/ecdsa_research/'+bundle.name,'/home/hclau/ecdsa_research/'+rp.name],text=True);(r/'SERVER-LAUNCH.json').write_text(out);print(out)
