from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-public-e3-cache-finished-20261020';r=root/'experiments/breakthrough-native-context-finished-20261020';r.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore','cache-tests.rs']:shutil.copyfile(old/p,r/p)
s=(old/'run.py').read_text();s=s.replace("proof=ws/'breakthrough-public-e3-context-clean-20261020';parent=ws/'breakthrough-stackv3-width-plan7-both-20261020'","proof=ws/'breakthrough-native-both-context16-20261020';parent=ws/'breakthrough-native-both-final-20261020'")
s=s.replace("a['native_controls']==9 and a['input_qubits']==1234 and a['output_qubits']<=1234","a['native_controls']==7 and a['input_qubits']==1464 and a['output_qubits']<=1480").replace("parent/'public/ops.bin'","parent/'candidate/ops.bin'").replace('714c4e4c1c2c5c59544dcc3ade28587663b616d46a168b0fcd22a06c29c0916f','cec71544f16da5598921a8a04e3b1416bda6f28d01878b1101ac724157a6f536').replace('==11602990','==10597028').replace('x[2]<1234','x[2]<1480')
start=s.index(" base='88869d8cc23fb72120dd52533f3e48277e9b36e4';");end=s.index("path=t/'src/point_add/mod.rs';",start)
s=s[:start]+''' pfsource=json.loads((parent/'SOURCE-FREEZE.json').read_text());assert all(sha(parent/'candidate'/p)==h for p,h in{**pfsource['source_files'],**pfsource['protected_files']}.items());base=pfsource['base'];assert not t.exists();subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),base],check=True)
 for p in pfsource['source_files']:dest=t/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(parent/'candidate'/p,dest)
 protected=pfsource['protected_files'];assert len(protected)==17 and all(sha(t/p)==h for p,h in protected.items());original=pfsource['source_files'];'''+s[end:]
s=s.replace('public_e3_parent_build','native_context_parent_build').replace('public_e3_cache','native_context_cache').replace('PUBLIC_E3_CACHE','NATIVE_CONTEXT_CACHE').replace('assert!(nq<=1234)','assert!(nq<=1480)').replace("'public_parent':'e3b5c51f-74e6-480a-82bf-5543fb1ba555'","'public_parent':'d182a53e-be3d-4119-8298-303a9a9de07a'").replace("'extra_quantum_wires':0","'extra_quantum_wires':16").replace("'Entire originalpublice3 constructor and all boundpasses unchanged, fullparent/input/cache-output canonical bindings, independent exactzero donor proofs, same exact rewritebody, checked historicaltail removed, nonce0. No approximation/precision/window change, no generic repass, pending ownfinalgate/nonce/benchmark.'","'Entire officially reproducedT748691 parent constructor and all boundpasses unchanged, fullparent/input/cache-output canonical bindings,499 independently exactcontext leases,16 additional donor wires permitted for independentT objective, same exact rewritebody, checked historicalnonce95 tail removed, nonce0. No approximation/precision/window change or generic repass; pending ownfinalgate/nonce/benchmark.'")
s=s.replace("str(parent/'observer/target')","str(parent/'candidate/target')")
needle="run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','--','--nocapture','--test-threads=1'],'tests',env=env)";assert s.count(needle)==1;s=s.replace(needle,"run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','build_circuit','native_context_cache::cache_tests','--','--nocapture','--test-threads=1'],'tests',env=env)");s=s.replace("assert counts==['20']","assert counts==['1']").replace("st['qubits_protected_analyzer']<=1234","st['qubits_protected_analyzer']<=1480").replace("'native_tests':20,'independent_proof_controls':9","'native_tests':1,'independent_proof_controls':7").replace('PUBLIC_E3_CACHE_FINISHED_NONCE0_NOT_GATED_OR_SCORED','NATIVE_CONTEXT499_FINISHED_NONCE0_NOT_GATED_OR_SCORED')
(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Finish499 exact context leases on officialT748691

Parentd182a53e/sourcefb2d03e8, completecec715 and source9cb5de5f. The fresh fixed
context16384/16-donor proof scan accepts499 leases of2031 nominees, rejects1532,
after all7 native proof/guard/phase/fault controls. Extra16 quantum wires are
permitted for the independentT record. Preserve the entire parent constructor
and all existing source-bound passes, rename only entrypoint, bind every parent
record, check/strip its historicalnonce95 identity tail, apply the literal proof
rewriter and499 rows, bind every output prefix to independent proof output,
appendnonce0. No generic repass or new approximation/window/correctness cut.

All17 protected files unchanged. One new fullbasis guardedcache/phase/fault
native control, inherited27 previously verified exact native controls unchanged,
and independent7 proof controls. Freeze fullsource before generation. Fresh full
development and own sole32768x64 finalgate vs exact then-current officialT record
before any qualified ascendingnonce, unchangedbenchmark and automatic submission.
No product claim, nonce screening or scored result here.
''')
print(r)
