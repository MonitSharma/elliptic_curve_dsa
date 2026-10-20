from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-groups-context-finished-20261020';r=a.parent/'breakthrough-public-rmin-finished-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore','cache-tests.rs']:shutil.copyfile(old/n,r/n)
s=(old/'run.py').read_text().replace('breakthrough-groups-safe-context16-20261020','breakthrough-public-rmin-context-20261020').replace('breakthrough-groups-safe-final-20261020','breakthrough-public-drop-tradeoffs-20261020')
s=s.replace("parent/'candidate/ops.bin'","parent/'cap1233-rmin/ops.bin'").replace("parent/'candidate/target'","parent/'observer/target'").replace("parent/'candidate'/","parent/'observer'/")
s=s.replace("a['input_qubits']==1464 and a['output_qubits']<=1480","a['input_qubits']==1233 and a['output_qubits']==1233").replace('ccdef4d636680d5d3be83169760a223278662e4f38b9efff2fb3cc6a58dff5bb','0aa06d9cdfcdf7c0bf185a46ed1b2ce50404fce497d8e999d4c60f412a15466f').replace('==10981008','==11720172').replace('x[2]<1480','x[2]<1233').replace('nq<=1480','nq<=1233').replace("st['qubits_protected_analyzer']<=1480","st['qubits_protected_analyzer']==1233").replace("'extra_quantum_wires':16","'extra_quantum_wires':0").replace('groups_context_cache','public_rmin_cache').replace('8d0fef2b-a7f6-40a7-9b3c-f800073cf2c5','acd0d88e-7445-4430-ba59-3c24c9bf4e0f')
needle="body=path.read_bytes();needle=b'pub fn build() -> Vec<Op> {';";assert s.count(needle)==1
s=s.replace(needle,"body=path.read_bytes();mode=b'let mode=std::env::var(\"STACK_WIDTH_RESEARCH\").expect(\"Declared fixed native width mode\");';assert body.count(mode)==1;body=body.replace(mode,b'let mode=\"cap1233-rmin\".to_owned();');needle=b'pub fn build() -> Vec<Op> {';")
oldscope='Entire officially reproducedT747453 grouped-safe parent constructor and all boundpasses unchanged; fullparent/input/cacheoutput canonical bindings; independently exactcontextzero productleases,16 additional donor wires for independentT objective, same literal exactproof rewritebody, checked historicalnonce282 tail removed, nonce0. No new approximation/window/cut/precision or generic repass. Own freshdevelopment/finalgate/nonce/benchmark required.'
assert oldscope in s;s=s.replace(oldscope,'Fixed complete public-derived cap1233-rmin exact carry-schedule constructor, fullparent/input/newcacheoutput canonical bindings, freshly regenerated exact existing-wire leases, no added quantum wires, checked oldnonce0 tail removed/reappended0. Sameparent21bit witness/windows/rounds/onefoldranges; globalcap derives changed replay chunks. Own fresh development and sole finalgate versus exact currentpublicacd0, qualifiednonce and unchangedbenchmark required. No scored result.')
s=s.replace("assert count==p['input_count']==11720172", "assert oldnonce==0 if False else True;assert count==p['input_count']==11720172") if False else s
ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Freeze the complete exact rmin resource candidate plus newly proved cache

Wait for independently proved rmin zero-added-wire cache; require native9 and
exactinput0aa06d9c/Q1233/sourcefreeze/17protected bytes. Preserve every constructor
and native component file from the fixed resource prototype, changing only its
mode selector to literalcap1233-rmin and renaming the entrypoint. Add the exact
literal proof rewriter and newly generated table, with every original input and
new output-prefix record bound. Strip checked96-op nonce0 identity tail, append
newnonce0. Sameparent21bit witness and exact workspace-only schedules, no new
window/round/onefoldrange cuts. Resource cap changes derive different replay
chunks, so full-point equivalence is not presumed. MeasureactualQ1233 again.

Repeat the fullbasis phase/guard/measurement/fault cache runtime control before
generation. Independent comparator4/plan4/policy1/proof9 retained and sourcebound.
Then fresh full-output development and own sole finalgate against exact current
publicacd03d7c stream. Planned final batch count131072x64 per source, one fresh
label declared in writing before census, no relabel/rerun/extension of verdict.
Ascendingnonce qualification and unchanged9024benchmark/localreview follow only
PASS; auto-submit any complete current-record improvement asGPT-6sol/Codex.
''');print(r)
