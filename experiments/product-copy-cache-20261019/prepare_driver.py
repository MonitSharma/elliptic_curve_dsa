from pathlib import Path
import json
r=Path(__file__).resolve().parent;old=r.parent/'product-anf-witness-20261019'
assert not (r/'run.pid').exists()
s=(old/'run.py').read_text()
s=s.replace("ANF_WITNESSES='1'","COPY_CACHE='1'").replace(".get('ANF_WITNESSES')",".get('COPY_CACHE')").replace("ANF_WITNESSES='0'","COPY_CACHE='0'")
s=s.replace("'witness'","'copy-cache'").replace("'witness.log'","'copy-cache.log'").replace("'witness.json'","'copy-cache.json'").replace("'witness.ops.bin'","'copy-cache.ops.bin'")
s=s.replace('EXACT_CURRENT_WIRE_ANF_WITNESS_SOURCE_SCREEN_COMPLETED','REVERSIBLE_COPY_CACHE_SOURCE_SCREEN_COMPLETED')
s=s.replace("'current_wire_witness_sites':sum(x.get('kind')=='exact_current_wire_product' for x in result['sites'])","'cache_pairs':result['sites_count']")
s=s.replace("(r/'RESULT.json').write_text","if changed:\n    control=json.loads((r/'CONTROL.json').read_text());assert control['saved_executed_Toffolis_total_on_512_control_shots']==512*result['sites_count']\n(r/'RESULT.json').write_text")
(r/'run.py').write_text(s,newline='\n')
s=(old/'launch.py').read_text().replace('product-anf256-20261019/run.exit','product-anf-witness-20261019/run.exit').replace('Local exact current-wire witness job','Local reversible copy-cache job');(r/'launch.py').write_text(s,newline='\n')
s=(old/'run.sh').read_text().replace('product-anf-witness-20261019','product-copy-cache-20261019');(r/'run.sh').write_text(s,newline='\n')
(r/'DRIVER-PREPARATION-FAILURE.json').write_text(json.dumps({'status':'INITIAL_NESTED_SHELL_QUOTING_FAILED_BEFORE_PYTHON_PREPARATION','launcher_compiler_scan_gate_nonce_started':False,'repair':'Preparation now uses this saved Python file, without nested shell quoting.'},indent=2)+'\n')
