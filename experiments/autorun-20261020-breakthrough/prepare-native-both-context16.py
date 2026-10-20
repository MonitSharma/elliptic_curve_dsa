from pathlib import Path
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-stackv3-plan7-zero-donors-20261020';r=root/'experiments/breakthrough-native-both-context16-20261020';r.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore']:(r/p).write_bytes((old/p).read_bytes())
s=(old/'run.py').read_text();s=s.replace("source=ws/'breakthrough-stackv3-plan7-generic-v2-20261020'","source=ws/'breakthrough-native-both-final-20261020'")
start=s.index(' start=time.time()\n while not(source/');end=s.index('\n of=json.loads',start)
s=s[:start]+''' assert(source/'run.exit').read_text().strip()=='0';sf=json.loads((source/'SOURCE-FREEZE.json').read_text());a=json.loads((source/'BENCHMARK-RESULT.json').read_text());receipt=json.loads((source/'PUBLIC-SOURCE-VERIFICATION.json').read_text());assert a['qubits']==1464 and a['rounded_mean_executed_toffoli']==748691 and receipt['public_source_revision']=='fb2d03e8a70a8b69965710ef46c5cdce828e9ca2';assert all(sha(source/'candidate'/p)==h for p,h in{**sf['source_files'],**sf['protected_files']}.items());input=source/'candidate/ops.bin';assert sha(input)=='cec71544f16da5598921a8a04e3b1416bda6f28d01878b1101ac724157a6f536'
'''.rstrip()+s[end:]
s=s.replace("'extra_donors':0","'extra_donors':16").replace("RESEARCH_EXTRA_DONORS='0'","RESEARCH_EXTRA_DONORS='16'").replace("proof['peak_qubits']==1233","proof['peak_qubits']==1480").replace('x[2]<1233','x[2]<1480').replace("st['qubits_protected_analyzer']<=1233","st['qubits_protected_analyzer']<=1480").replace("'input_qubits':1233","'input_qubits':1464").replace("'ZERO_ADDED_WIRE_EXACT_CONTEXT_COMPONENT_NOT_SCORED'","'NATIVE_BOTH_CONTEXT16_EXACT_COMPONENT_NOT_SCORED'")
(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Independent T objective: exact context16 on official748691

Fixed parent d182a53e/sourcefb2d03e8, locally verified final9cb5de5f and complete
officially reproduced streamcec715, Q1464/T748691. Reuse unchanged exact16,384-op
same-scope context proof engine, declare16 added donor wires (maximumQ1480).
All7 native functional/guard/phase/fault controls precede this component scan.
No window, precision, approximation, source-bound table or old gate changes.
Higher width is explicitly allowed for the independent Toffoli record. Every
accepted product lease requires full algebra proof, clean/no-touch/nonoverlap
and original exact phase repair. Fingerprints nominate only.

If there are leases, preserve the entire current parent constructor and bind
every canonical record, strip its checked historicalnonce95 tail, apply the
proved cache and bind every new output, appendnonce0. Own new finalgate versus
exactthen-current officialT parent, qualifiedascendingnonce, unchangedbenchmark
and local review are mandatory before autonomous GPT-6sol/Codex submission.
This is separate from the product candidate; no statistical verdict is reused.
''');print(r)
