from pathlib import Path
import ast,sys
root=Path(__file__).resolve().parents[2];ex=root/'experiments';extra=int(sys.argv[1]);assert extra in [0,16];old=ex/'breakthrough-stackv3-plan7-context-clean-20261020';r=ex/f'breakthrough-groups-safe-context{extra}-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore','patch-tool.py']:(r/n).write_bytes((old/n).read_bytes())
s=(old/'run.py').read_text().replace("source=ws/'breakthrough-stackv3-plan7-generic-v2-20261020'","source=ws/'breakthrough-groups-safe-final-20261020'")
start=s.index(' start=time.time()\n while not(source/');end=s.index('\n of=json.loads',start)
s=s[:start]+''' assert(source/'run.exit').read_text().strip()=='0';sf=json.loads((source/'SOURCE-FREEZE.json').read_text());a=json.loads((source/'BENCHMARK-RESULT.json').read_text());receipt=json.loads((source/'PUBLIC-SOURCE-VERIFICATION.json').read_text());assert a['qubits']==1464 and a['rounded_mean_executed_toffoli']==747453 and receipt['public_source_revision']=='d289ee2bbde583508993f8beb895a4ec3e2ae26c';assert len(sf['source_files'])==204 and all(sha(source/'candidate'/p)==h for p,h in{**sf['source_files'],**sf['protected_files']}.items());input=source/'candidate/ops.bin';assert sha(input)=='ccdef4d636680d5d3be83169760a223278662e4f38b9efff2fb3cc6a58dff5bb'
'''.rstrip()+s[end:]
s=s.replace("'extra_donors':0",f"'extra_donors':{extra}").replace("RESEARCH_EXTRA_DONORS='0'",f"RESEARCH_EXTRA_DONORS='{extra}'").replace("proof['peak_qubits']==1233",f"proof['peak_qubits']<={1464+extra}").replace('x[2]<1233',f'x[2]<{1464+extra}').replace("st['qubits_protected_analyzer']<=1233",f"st['qubits_protected_analyzer']<={1464+extra}").replace("'input_qubits':1233","'input_qubits':1464").replace('Exact context component using only existing physical quantum wires; no scored result/gate/nonce.',f'Exact context component with {extra} declared additional donor wires, arbitrary-cut zero proof for existing donors, no scored result/gate/nonce.')
ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text(f'''# Exact context caches on new officialT747453

Current official8d0fef2b/source d289ee2b Q1464/T747453, localab071cf3,
204source/17protected verified. Exact complete selectedstreamccdef4d6.
Fixed16,384-op same lexical-scope exact Boolean proof. {extra} extra donor wires,
actual maximumQ{1464+extra}; exact arbitrary-cut zero proof admits originalidle
wires only when symbolic expression is identicallyzero. Fingerprints nominate
only. All9 native phase/guard/value/forbiddenalias/contextzero/fault controls
precede search. Strict clean/no-touch/nonoverlap scopes. No new precision/window,
round/cut/table transport or oldgate/nonce. Componentcounts are not records.
If promising, preserve entire public parent constructor, fullcanonical binding,
checkedhistoricaltail stripping, independently boundnewoutput andnonce0. Own
fresh development/sole finalgate versus exactthen-current publicT, qualified
ascendingnonce, unchangedbenchmark/localmember review before autoGPT6sol upload.
No externalcode/table dependency in candidate; all operations must be counted.
''');print(r)
