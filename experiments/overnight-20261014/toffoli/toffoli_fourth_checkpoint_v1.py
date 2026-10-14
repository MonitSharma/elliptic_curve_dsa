"""Freeze completed evidence hashes; new actual lean prototype stays separate."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
here=Path(__file__).parent
receipt={'collected_at_utc':datetime.now(timezone.utc).isoformat(),
         'baseline_revision':'c5bb1ec876db859a3f9f8a9052c140a145df834e',
         'status':'H45 exact native component passed; current full guard zero; actual lean phase factor native pending',
         'qualified_score':None,
         'completed_files_sha256':{file.name:hashlib.sha256(file.read_bytes()).hexdigest() for file in sorted(here.iterdir()) if file.is_file() and file.name!='fourth-checkpoint-receipt.json'},
         'solver_status':'All v2/v3/v4 forward and reverse selected plane sweeps completed with zero witness and zero solver unknown; restricted families only, trusted UNSAT without formal proof dump.',
         'native_H45':{'pid':2533045,'exit':0,'positive_cases':100925440,'patch_sha256':'9bb4b03ab603d93dcf89484335b8fb20d1e63f952fd0b1eb7901235eba85c5bf'},
         'actual_full_c5_H45_guard_occurrences_reported_by_independent_product_census':0,
         'active_prototype':{'status':'preparing fin3/drop0 actual lean C4-swap schedule after independent proof; no job launched',
                             'resource_permission':'16GiB4build1runtime native fixture only; fresh preflight required',
                             'actual_fin4':'unadmitted under E2-only missing model: ESh changes E0/E1 too; separate producer-aware proof required'},
         'scope':'Component/source-bound truth and native evidence; no new full scored record. Current early-expansion full builder belongs to independent product work.'}
(here/'fourth-checkpoint-receipt.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
print(json.dumps({'status':receipt['status'],'completed_files':len(receipt['completed_files_sha256'])}))
