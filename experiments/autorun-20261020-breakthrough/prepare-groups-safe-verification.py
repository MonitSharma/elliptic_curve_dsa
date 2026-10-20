from pathlib import Path
import shutil,ast
root=Path(__file__).resolve().parents[2];ex=root/'experiments';old=ex/'breakthrough-native-context-development-20261020';dev=ex/'breakthrough-groups-safe-development-20261020';dev.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore']:(dev/p).write_bytes((old/p).read_bytes())
s=(old/'run.py').read_text();s=s.replace('breakthrough-native-context-finished-v3-20261020','breakthrough-groups-safe-finished-20261020').replace("a['native_tests']==1 and a['independent_proof_controls']==7 and a['qubits']<=1480","a['native_tests']==2 and a['inherited_native_controls']==27 and a['qubits']==1464").replace('breakthrough-native-both-final-20261020/candidate/ops.bin','breakthrough-native-context-final-20261020/candidate/ops.bin').replace('publicd182','public38').replace('context499','groupssafe').replace('cec71544f16da5598921a8a04e3b1416bda6f28d01878b1101ac724157a6f536','0e4fcfab22855197075ce69bb8e2b067f7fbf22d4412390707df3944831f0689').replace('native-groupssafe-development-20261020-v1','groups-safe28-full259-development-20261020-v1').replace('fixedexactgroupssafe on complete officialT748691 parent','fixedsafe grouped-square/nativefull259 correction/28bit witness source versus currentofficialT748184')
ast.parse(s);(dev/'run.py').write_text(s)
(dev/'PLAN.md').write_text('''# Fresh full-output grouped-safe development

Fixed source before sampling:groups-safe28-d8, full259-bit correction tails,
28-bit witness, exact square split, inverseleaf depth8, same uniform+2/public140/
native rail/G6 baseline. Labelgroups-safe28-full259-development-20261020-v1,
512x64/source, fourworkers, eight protectedscalar batches/source. Exact public38
stream0e4fcfab comparator (its499 cache is not code-inherited). Retain all wrong
value/phase/dirty/full-target/other quantumlane differences. Requirezero dirty.
Prior27 native controls, groupplan and square caller-contract units/faults plus
complete raw/output binding precede sampling. Historical six square-unit domain
edge diagnostics are preserved separately; no universal correctness claim.
No finalgate/nonce/benchmark/scored result. Next gate is independent and final.
''')
oldgate=ex/'breakthrough-native-context-final-gate-20261020';gate=ex/'breakthrough-groups-safe-final-gate-20261020';gate.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore','census.py']:(gate/p).write_bytes((oldgate/p).read_bytes())
s=(oldgate/'declare.py').read_text();changes={'breakthrough-native-context-finished-v3-20261020':'breakthrough-groups-safe-finished-20261020','breakthrough-native-both-final-20261020':'breakthrough-native-context-final-20261020','breakthrough-native-context-development-20261020':'breakthrough-groups-safe-development-20261020',"len(f['source_files'])==201":"len(f['source_files'])==204","a['native_tests']==1":"a['native_tests']==2","a['qubits']==1480":"a['qubits']==1464","a['diagnostic_weight']<748689.0":"a['diagnostic_weight']<748190.0",'native_context_cache.rs':'groups_safe_finished.rs','d182a53e-be3d-4119-8298-303a9a9de07a':'38a686dd-a2b1-4bdc-899e-81a389d36fd5',"{'qubits':1464,'toffoli':748691}":"{'qubits':1480,'toffoli':748184}",'1096083624':'1107312320',"pr['source_files']==200":"pr['source_files']==201",'cec71544f16da5598921a8a04e3b1416bda6f28d01878b1101ac724157a6f536':'0e4fcfab22855197075ce69bb8e2b067f7fbf22d4412390707df3944831f0689','<748691':'<748184','native-context499-exact-final-20261020-v1':'groups-safe28-full259-final-20261020-v1',"'candidate_qubits_from_protected_analyzer':1480":"'candidate_qubits_from_protected_analyzer':1464",'Sole finalgate for fixed499 exactcontext leases on officiald182.16 extra donor wires for independentT; no new precision/cut/window. Outcome final: no relabel, extension or nonce to reverse failure. All source/proof choices frozen before development.':'Sole finalgate for fixed full259-tail/28bit-witness grouped native square on strengthenedT baseline. Currentofficial38 comparator cache is not inherited. Outcome final: no relabel, extension or nonce to reverse failure. All native/mode/source choices fixed before development.'}
for x,y in changes.items():assert x in s,x;s=s.replace(x,y)
ast.parse(s);(gate/'declare.py').write_text(s)
s=(oldgate/'run.py').read_text().replace('breakthrough-native-context-finished-v3-20261020','breakthrough-groups-safe-finished-20261020').replace('breakthrough-native-context-development-20261020','breakthrough-groups-safe-development-20261020');ast.parse(s);(gate/'run.py').write_text(s)
(gate/'PLAN.md').write_text('''# Sole final grouped-safe gate

Labelgroups-safe28-full259-final-20261020-v1;32768 batches of64/source, fresh
paired inputs, nonce0, exact then-current publicT parent38a686dd/748184/0e4fcfab.
Source/mode/precision/correction tails fixed before native/development inputs.
Refresh publicminimum and verify201 parent source/17 protected bytes before
declaration; stop without sampling if targetchanges. Eight workers/source,16
total after resource check. All four AGENTS criteria; verdict final, no new
label/sample extension/nonce to reverse failure. Only PASS permits qualified
ascendingnonce, unchangedbenchmark/local review/autosubmission. This is a new
native circuit; no context499/earlier gate or nonce is reused. No product claim.
''')
print(dev);print(gate)
