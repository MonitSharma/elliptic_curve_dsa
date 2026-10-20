from pathlib import Path
import ast
root=Path(__file__).resolve().parents[2];ex=root/'experiments';old=ex/'breakthrough-native-context-finished-v3-20261020';r=ex/'breakthrough-groups-context-finished-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore','cache-tests.rs']:(r/n).write_bytes((old/n).read_bytes())
s=(old/'run.py').read_text();changes={'breakthrough-native-both-context16-20261020':'breakthrough-groups-safe-context16-20261020','breakthrough-native-both-final-20261020':'breakthrough-groups-safe-final-20261020',"a['native_controls']==7":"a['native_controls']==9",'cec71544f16da5598921a8a04e3b1416bda6f28d01878b1101ac724157a6f536':'ccdef4d636680d5d3be83169760a223278662e4f38b9efff2fb3cc6a58dff5bb','==10597028':'==10981008','native_context_cache':'groups_context_cache',"'independent_proof_controls':7":"'independent_proof_controls':9",'d182a53e-be3d-4119-8298-303a9a9de07a':'8d0fef2b-a7f6-40a7-9b3c-f800073cf2c5','Entire officially reproducedT748691 parent constructor and all boundpasses unchanged, fullparent/input/cache-output canonical bindings,499 independently exactcontext leases,16 additional donor wires permitted for independentT objective, same exact rewritebody, checked historicalnonce95 tail removed, nonce0. No approximation/precision/window change or generic repass; pending ownfinalgate/nonce/benchmark.':'Entire officially reproducedT747453 grouped-safe parent constructor and all boundpasses unchanged; fullparent/input/cacheoutput canonical bindings; independently exactcontextzero productleases,16 additional donor wires for independentT objective, same literal exactproof rewritebody, checked historicalnonce282 tail removed, nonce0. No new approximation/window/cut/precision or generic repass. Own freshdevelopment/finalgate/nonce/benchmark required.'}
for a,b in changes.items():assert a in s,a;s=s.replace(a,b)
ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Freeze exactcontext16 wrapper on officialgroupedT747453

Wait completedfixed16-donor scan and all9 exactnativeproofcontrols. If no
provenleases, preserve/no candidate. Otherwise preserve entire public8d0fef2b
source204/17, complete selectedstreamccdef4d6. Renameentrypoint only, append
literalindependent proofrewriter andnewtable in groups_context_cache. Bind
everyparentrecord, removecheckedhistoricalnonce282 identitytail, applyproved
leases, bindallnewprefixrecords, appendnonce0.205source/17protected. Atmost1480Q;
16additionaldonors allowedonly for independentT. No genericrepass, approximation,
precision/window/round/cut change or oldtabletransport. Existing donorzero must
be exactlyprovedforarbitrarycut variables. Repeatfullbasis guard/measurement/
phase-fault runtimecontrol onfinishedsource; prior9proof +29parentnative controls
retained. Ownfreshdevelopment andsole final32768x64/sourcegate versus exactthen-
currentpublic8dstream, qualifiedascendingnonce andunchangedfullbenchmark/local
review before autoGPT-6sol/Codex submission. No scoredresult fromthis stage.
''');print(r)
