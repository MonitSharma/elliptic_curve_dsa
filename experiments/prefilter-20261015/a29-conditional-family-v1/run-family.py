from pathlib import Path
import subprocess,json,hashlib
r=Path(__file__).resolve().parents[1];d=r/'a29-conditional-family-v1';f=json.loads((d/'PREDECLARED-FAMILY.json').read_text());rows=[]
for x in f['frames']:
 t=x['tick'];prefix=d/f'tick-{t}.guard';args=[str(r/'tool/target/release/a29_pair_fold_family'),str(d/f'tick-{t}.old.bin'),str(d/f'tick-{t}.new.bin'),str(d/f'tick-{t}.prefix.json'),str(d/f'tick-{t}.interface.json'),str(prefix)]
 out=subprocess.check_output(args,text=True);(d/f'tick-{t}.result.json').write_text(out);p=json.loads(out);rows.append(dict(tick=t,status=p['status'],differences=p.get('all_nonzero_q_differences'),compiled_nodes=p.get('guard_compiled_nodes'),seconds=p['seconds'],required_zero_qids=p['required_A29_prefix_zero_qids']));print(t,p['status'],p.get('guard_compiled_nodes'),flush=True)
(d/'family-summary.json').write_text(json.dumps(dict(status='ALL29_LOCAL_FULL_QUANTUM_INTERFACE_GUARDS_PASS'if all(x['status']=='PAIRED_FULL_QUANTUM_INTERFACE_PASS_INPUT_ONLY_DIFFERENCE_GUARD'for x in rows)else'UNKNOWN_OR_FAILED_PAIR_PRESERVED_NO_COMPOSITION',rows=rows,remaining='Actual-prefix composition, live classical projection review, independent compiled-guard validation and runtime cost gate are still required.'),indent=2)+'\n')
