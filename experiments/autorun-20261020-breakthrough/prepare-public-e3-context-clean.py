from pathlib import Path
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-stackv3-plan7-context-clean-20261020';r=root/'experiments/breakthrough-public-e3-context-clean-20261020';r.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore','patch-tool.py']:(r/p).write_bytes((old/p).read_bytes())
s=(old/'run.py').read_text();s=s.replace("source=ws/'breakthrough-stackv3-plan7-generic-v2-20261020'","source=ws/'breakthrough-stackv3-width-plan7-both-20261020'")
start=s.index(' start=time.time()\n while not(source/');end=s.index('\n of=json.loads',start)
s=s[:start]+''' assert(source/'run.exit').read_text().strip()=='0';sf=json.loads((source/'SOURCE-FREEZE.json').read_text());assert all(sha(source/'observer'/p)==h for p,h in{**sf['source_files'],**sf['protected_files']}.items());input=source/'public/ops.bin';assert sha(input)=='714c4e4c1c2c5c59544dcc3ade28587663b616d46a168b0fcd22a06c29c0916f'
'''.rstrip()+s[end:]
s=s.replace("proof['peak_qubits']==1233","proof['peak_qubits']==1234").replace('x[2]<1233','x[2]<1234').replace("st['qubits_protected_analyzer']<=1233","st['qubits_protected_analyzer']<=1234").replace("'input_qubits':1233","'input_qubits':1234").replace("'EXACT_CONTEXT_PROVED_ZERO_DONORS_COMPONENT_NOT_SCORED'","'PUBLIC_E3_EXACT_CONTEXT_ZERO_DONORS_COMPONENT_NOT_SCORED'")
(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Product route: cache exact complete public e3 without width retuning

Fixed exact public e3b5c51f/source88869 output714c,11602990 records, measuredQ1234.
The complete control reproduces under every width-probe source with flagsOFF.
Apply the same separately controlled exact context-clean donor proof engine
with zero added wires to this full stream, preserving all original source-bound
passes and native circuit choices. This branch changes no witness precision,
window or approximation. It seeks a direct same-width Toffoli/product reduction
without the narrower branch's native scheduling cost. All original failure-rate
evidence and independent final gate rules still apply; public eligibility is
not inherited. Exact cache proofs do not establish a passing final failure rate.

Every accepted lease requires no-touch/nonoverlap and either original exact
clean flag or full arbitrary-cut algebra proving donorzero and effective product
equality. Repeat9 native functional/guard/phase/fault controls before scanning.
No scored record, nonce or finalgate here. If there are leases, reconstruct pure
source from exactGit88869, preserve its constructor, bind every parent record,
remove only its historical identity tail, apply proven rewrites, appendnonce0
and bind the complete new output. Then whole-output development and one final
declared32768x64 gate vs exactpublice3 precede qualified nonce/benchmark/upload.
''');print(r)
