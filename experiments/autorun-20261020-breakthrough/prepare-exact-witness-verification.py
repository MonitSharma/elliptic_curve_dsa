from pathlib import Path
import ast,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-depth12-development-20261020';dev=ex/'breakthrough-exact-witness-finished-development-20261020';dev.mkdir(exist_ok=False)
for n in['.gitattributes','.gitignore']:shutil.copyfile(old/n,dev/n)
s=(old/'run.py').read_text().replace('breakthrough-depth12-finished-20261020','breakthrough-exact-witness-finished-20261020').replace("a['native_tests']==2","a['native_tests']==7").replace("a['qubits']<=1480","a['qubits']<=1664").replace("'public71':ws/'breakthrough-groups-context-final-20261020/candidate/ops.bin'","'public2bd':ws/'breakthrough-depth12-final-20261020/candidate/ops.bin'").replace('public71','public2bd').replace('278802f0728d9233297723c88dffef8544bd9c3ce9968d34a2c3f406b383688a','63370be6078a4a80454d5174a5f07bfac094fea6af3dd526f77dc8194012cc29').replace("'depth12'","'witness'").replace('depth12-context-development-20261020-v1','witness-finished-development-20261020-v1')
s=s.replace('Fresh full-output development512x64/source, fixedexactdepth12 on complete officialT747453 grouped-safe parent.','Fresh full-output development512x64/source on final selectedfull259witness/sharedsum/literal0/freshcache source, compared against exactpublishedT2bd Q1464/T747218. Native7/proof9 andwholebindings passed before inputs. No new approximatewindow/cut/precision/round.');ast.parse(s);(dev/'run.py').write_text(s)
s=(old/'diagnostic.py').read_text().replace('breakthrough-depth12-finished-20261020','breakthrough-exact-witness-finished-20261020').replace('public71','public2bd');ast.parse(s);(dev/'diagnostic.py').write_text(s)
(dev/'PLAN.md').write_text('Finalsource/native7/proof9/fullcanonicalbindings fixed beforefreshlabel witness-finished-development-20261020-v1,512x64/source,4workers/8protectedscalarbatches vs exactpublishedT2bd/63370be6. Preserveallpoint/phase/dirty/other/Toutcomes. No finalgate/nonce/score.\n')
old=ex/'breakthrough-depth12-final-gate-20261020';gate=ex/'breakthrough-exact-witness-final-gate-20261020';gate.mkdir(exist_ok=False)
for n in['.gitattributes','.gitignore','census.py']:shutil.copyfile(old/n,gate/n)
s=(old/'declare.py').read_text().replace('breakthrough-depth12-finished-20261020','breakthrough-exact-witness-finished-20261020').replace('breakthrough-groups-context-final-20261020','breakthrough-depth12-final-20261020').replace('breakthrough-depth12-development-20261020','breakthrough-exact-witness-finished-development-20261020').replace('depth12_context_cache.rs','witness_context_cache.rs').replace('71d9dc7e-550b-480d-8d9e-c2af1989c0d7','2bd0f979-ab55-4f91-8133-68a08febaa67').replace('747226','747218').replace('1093938864','1093927152').replace('278802f0728d9233297723c88dffef8544bd9c3ce9968d34a2c3f406b383688a','63370be6078a4a80454d5174a5f07bfac094fea6af3dd526f77dc8194012cc29').replace("a['native_tests']==2","a['native_tests']==7").replace("a['qubits']==1464 and a['diagnostic_weight']<746143.0","a['qubits']<=1664").replace("len(f['source_files'])==205","set(f['source_files'])=={p.relative_to(t).as_posix()for p in(t/'src/point_add').rglob('*')if p.is_file()}").replace("'candidate_qubits_from_protected_analyzer':1464","'candidate_qubits_from_protected_analyzer':a['qubits']").replace("['depth12']","['witness']").replace('depth12-context-final-20261020-v1','full259-witness-final-20261020-v1').replace('fixed exactdepth12','fixed exactfull259witness/sharedsum').replace('Exact currentT71','Exact currentT2bd').replace('Native34/proof9/runtime2','Native5components/group1/full5caller/proof9/runtime7')
ast.parse(s);(gate/'declare.py').write_text(s)
s=(old/'run.py').read_text().replace('breakthrough-depth12-finished-20261020','breakthrough-exact-witness-finished-20261020').replace('breakthrough-depth12-development-20261020','breakthrough-exact-witness-finished-development-20261020').replace('start<7200','start<21600');ast.parse(s);(gate/'run.py').write_text(s)
(gate/'PLAN.md').write_text('''# Sole final statistical gate for selected exact full259 arithmetic and caches

Waitfinalsource/native7/proof9/wholebindings andfreshfinished512x64development.
Require actualmeanT saving beyond2SE, zero dirty/otherregister differences.
Independentlydecode ALL96literalzero-tail ops; verifyEVERYsource/17protected
file andexactpublicT2bd/63370be6 officialreceipt. RefreshpublicTleader immediately
before declaration; ifchanged stopBEFORE declaration/sampling andpreserveall.

Freshlabel full259-witness-final-20261020-v1,32768batches of64/source,2097152shots,
8workers/8protectedscalarbatches persource. Label/count/source/parent written
beforecensus. Fourusercriteria andexactpaired McNemar. DeclaredverdictFINAL:
no rerun/relabel/extension/newnonce toreverseFAIL; no older verdict reused.
Only ownPASS enablesqualifiedascendingnonce/protected9024/unchangedbenchmark/
localsource/evidence verification/automaticGPT-6sol/Codex recordsubmission.
''');print(dev);print(gate)
