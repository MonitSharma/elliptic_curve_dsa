from pathlib import Path
import shutil,ast
ws=Path(__file__).resolve().parent.parent;r=ws/'product-copy-cache-native-20261020';old=ws/'product-classical-twelve-native-20261019'
s=(old/'qualify.py').read_text().replace("len(freeze['source_files'])==180","len(freeze['source_files'])==182").replace("proof=r.parent/'product-classical-twelve-proof-20261019'","proof=r.parent/'product-copy-cache-proof-20261020'")
s=s.replace("assert (proof/'run.exit').read_text().strip()=='0'","assert json.loads((proof/'SERVER-REPLAY.json').read_text())['status']=='INDEPENDENT_SERVER_SMT2_REPLAY_UNSAT'")
s=s.replace('CLASSICAL_TWELVE_VALUE_PHASE_AND_RNG_TRANSFER_AUDIT_PASS','COPY_CACHE_VALUE_PHASE_AND_PHYSICAL_RNG_TRANSFER_AUDIT_PASS')
s=s.replace('FRESH_VALID_POINT_COMPONENT_SAVING_VERIFIED','UNIVERSAL_ONE_EXECUTED_TOFFOLI_PER_SHOT_SAVING_CERTIFIED')
s=s.replace("assert component['additional_mean_executed_Toffolis_saved']>0 and component['every_paired_value_phase_and_dirty_diagnostic_identical']","assert component['additional_executed_toffoli_saving_per_shot']==1 and component['every_quantum_classical_phase_and_physical_rng_value_equal']")
s=s.replace('pareto-parent4-classical12-gate-20261019-v1','pareto-parent4-copy-cache-gate-20261020-v1').replace('Independent final classical12 gate planned before the classical9 verdict.','Independent final gate on the frozen native reversible-copy-cache circuit.').replace('valid_point_component_sha256','universal_component_cost_sha256')
ast.parse(s);assert not (r/'qualify.py').exists();(r/'qualify.py').write_text(s,newline='\n');shutil.copy2(old/'refresh_record.py',r/'refresh_record.py')
(r/'run-gate.sh').write_text('''#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-copy-cache-native-20261020
cd "$r"
trap 'rc=$?; printf "%s\\n" "$rc" > "$r/gate.exit"' EXIT
export RESEARCH_SLOTS=3 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 RAYON_NUM_THREADS=1
python3 ../autonomous-20261019/preflight_v15.py > gate-preflight.json
sha256sum qualify.py run-gate.sh refresh_record.py GATE-PLAN.md ../autonomous-20261019/preflight_v15.py ../autonomous-20261019/resource_registry.py > GATE_SOURCE.sha256
ulimit -v 33554432
python3 qualify.py
''',newline='\n')
(r/'launch_gate.py').write_text('''import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent
assert (r/'run.exit').read_text().strip()=='0'
assert json.loads((ws/'product-copy-cache-proof-20261020/TRANSFER.json').read_text())['status']=='COPY_CACHE_VALUE_PHASE_AND_PHYSICAL_RNG_TRANSFER_AUDIT_PASS'
assert (ws/'product-classical-twelve-operational-20261019/control.exit').read_text().strip()=='0','Finish the existing qualified source12 control first'
assert not (r/'gate.pid').exists() and not (r/'qualification').exists()
assert b'\\r' not in (r/'run-gate.sh').read_bytes()
with (r/'gate-nohup.log').open('xb') as f:p=subprocess.Popen(['nohup','bash','run-gate.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'gate.pid').write_text(str(p.pid)+'\\n');print(json.dumps({'pid':p.pid,'job':'sole declared reversible-copy-cache failure-rate gate'}))
''',newline='\n')
