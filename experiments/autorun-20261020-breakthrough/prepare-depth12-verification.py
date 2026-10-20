from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-groups-context-development-20261020';dev=a.parent/'breakthrough-depth12-development-20261020';dev.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore']:shutil.copyfile(old/n,dev/n)
s=(old/'diagnostic.py').read_text().replace('breakthrough-groups-context-finished-20261020','breakthrough-depth12-finished-20261020').replace("records['public8d']","records['public71']").replace("name=='public8d'","name=='public71'");ast.parse(s);(dev/'diagnostic.py').write_text(s)
s=(old/'run.py').read_text().replace('breakthrough-groups-context-finished-20261020','breakthrough-depth12-finished-20261020').replace("a['native_tests']==1","a['native_tests']==2").replace("'public8d':ws/'breakthrough-groups-safe-final-20261020/candidate/ops.bin'","'public71':ws/'breakthrough-groups-context-final-20261020/candidate/ops.bin'").replace("paths['public8d']","paths['public71']").replace('ccdef4d636680d5d3be83169760a223278662e4f38b9efff2fb3cc6a58dff5bb','278802f0728d9233297723c88dffef8544bd9c3ce9968d34a2c3f406b383688a').replace('context230','depth12').replace('groups-depth12-development-20261020-v1','depth12-context-development-20261020-v1')
start=s.index(" s=(old/'diagnostic.py').read_text()");end=s.index("subprocess.run(['python3',str(r/'diagnostic.py')]",start);s=s[:start]+' '+s[end:];s=s.replace("(r/'DEVELOPMENT-CONTROLLER.exit')","(r/'controller.exit')");ast.parse(s);(dev/'run.py').write_text(s)
(dev/'PLAN.md').write_text('Fresh depth12-context-development-20261020-v1,512x64/source, fourworkers/eightprotectedscalarbatches each, final bound depth12/newcache/literal0 vs exactcurrent71 stream278802f0. Source/native2/proof9/inherited34 fixed before fresh inputs; full outputs/phase/dirty/T retained. Not a finalgate/nonce/benchmark/score.\n')
old=a.parent/'breakthrough-groups-context-final-gate-20261020';gate=a.parent/'breakthrough-depth12-final-gate-20261020';gate.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore','census.py']:shutil.copyfile(old/n,gate/n)
s=(old/'declare.py').read_text().replace('breakthrough-groups-context-finished-20261020','breakthrough-depth12-finished-20261020').replace('breakthrough-groups-safe-final-20261020','breakthrough-groups-context-final-20261020').replace("a['native_tests']==1","a['native_tests']==2").replace("a['diagnostic_weight']<746373.0","a['diagnostic_weight']<746143.0").replace('groups_context_cache.rs','depth12_context_cache.rs').replace('8d0fef2b-a7f6-40a7-9b3c-f800073cf2c5','71d9dc7e-550b-480d-8d9e-c2af1989c0d7').replace('747453','747226').replace('1094271192','1093938864').replace("pr['source_files']==204","pr['source_files']==205").replace('ccdef4d636680d5d3be83169760a223278662e4f38b9efff2fb3cc6a58dff5bb','278802f0728d9233297723c88dffef8544bd9c3ce9968d34a2c3f406b383688a').replace('groups-context230-final-20261020-v1','depth12-context-final-20261020-v1').replace('breakthrough-groups-context-development-20261020','breakthrough-depth12-development-20261020').replace("dev/'DEVELOPMENT-CONTROLLER.exit'","dev/'controller.exit'")
needle="; (predecessor/'submission-status.json').write_text(json.dumps(data,indent=2)+'\\n')";assert s.count(needle)==1;s=s.replace(needle,'')
needle="if not(predecessor/'PUBLIC-SOURCE-VERIFICATION.json').exists():subprocess.run(['python3',str(predecessor/'verify-official-source.py')],cwd=predecessor,check=True)";assert s.count(needle)==1;s=s.replace(needle,"assert(predecessor/'PUBLIC-SOURCE-VERIFICATION.json').exists(), 'Exact currentparent receipt required; do not mutate sealed predecessor evidence'")
needle="sid='71d9dc7e-550b-480d-8d9e-c2af1989c0d7';api=";assert s.count(needle)==1
tailcheck='''tail=b'';position=0
with(t/'ops.bin').open('rb',buffering=0)as raw:
 header=raw.read(16);assert header[:8]==b'QECCOPSZ';nops=int.from_bytes(header[8:],'little');child=subprocess.Popen(['zstd','-dc'],stdin=raw,stdout=subprocess.PIPE)
 while block:=child.stdout.read(1<<20):tail=(tail+block)[-96*56:];position+=len(block)
 assert child.wait()==0 and position==nops*56
import struct
no=(1<<64)-1;assert all(row==(6,no,no,0,no,no,no)for row in struct.iter_unpack('<7Q',tail));assert len(tail)==96*56
dev=ws/'breakthrough-depth12-development-20261020';assert(dev/'controller.exit').read_text().strip()=='0';development=json.loads((dev/'DIAGNOSTIC.json').read_text());comp=development['comparisons']['depth12'];assert development['summaries']['depth12']['dirty_shots']==0 and not comp['different_other_lanes'];assert comp['candidate_minus_parent_raw_toffoli']+2*comp['paired_standard_error']<0,'No adequate actual T saving before gate declaration'
'''
s=s.replace(needle,tailcheck+needle);s=s.replace("verdict_policy='Sole finalgate for fixed230 exactcontext leases on official8d grouped-safe source. No addedactualQ; all9 exactproof controls and runtimecontrolpass. No new precision/cut/window. Outcome final: no relabel, extension or nonce to reverse failure. All source/proof choices frozen before development.'","verdict_policy='Sole finalgate for fixed exactdepth12 plus newly proved zero-added-wire cache on strong grouped arithmetic. Exact currentT71 parent. Native34/proof9/runtime2 retained. Outcome final: no rerun/relabel/extension/nonce to reverse failure. Final source/cache fixed before fresh development; no prior gate verdict reused.'")
ast.parse(s);(gate/'declare.py').write_text(s)
s=(old/'run.py').read_text().replace('breakthrough-groups-context-finished-20261020','breakthrough-depth12-finished-20261020').replace('breakthrough-groups-context-development-20261020','breakthrough-depth12-development-20261020').replace("d/'DEVELOPMENT-CONTROLLER.exit'","d/'controller.exit'");ast.parse(s);(gate/'run.py').write_text(s)
(gate/'PLAN.md').write_text('''# Sole fresh statistical gate for final exact depth12 plus regenerated caches

Wait finished bound source/native2 and fresh512x64 development; require actual
T saving beyond2SE, zero dirty/otherregister differences. Independently decode
literalzero tail; verify all205source/17protected and exact currentofficial71
source receipt/selectedstream278802f0 without mutating its sealed evidence.
Refresh public independentT leader before declaration. Fixed fresh labeldepth12-
context-final-20261020-v1,32768x64/source, eightworkers/eightprotectedscalarbatches
each, allfour userstatistical criteria. Label/count written before census.
Outcome final, never rerun/relabel/extend/use anothernonce to reverse failure.
Any failed preflight before declaration is preserved as no-gate status.
Only a realPASS allows qualifiedascendingnonce/full9024benchmark/localreview
and automatic officialsubmission of a complete newcurrent-record improvement.
''');print(dev);print(gate)
