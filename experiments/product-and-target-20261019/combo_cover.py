import json
from pathlib import Path
from cover import cover
r=Path(__file__).resolve().parent
old=json.loads((r/'absorbed-tight.json').read_text());profile=json.loads((r/'combo-profile.json').read_text())
assert all(profile[k]==v for k,v in old.items()),[k for k,v in old.items() if profile[k]!=v]
scan=json.loads((r/'combo-scan.json').read_text())
result={'status':'CONTROLLED_AND_ABSORPTION_PLUS_CARRY_COVER_DIAGNOSTIC_NOT_A_SCORE',
        'instrumentation_output_and_all_existing_fields_identical':True,
        'input_full_sha3_256':scan['input_sha3_256'],
        'and_absorbed_Q':profile['recolored_Q'],
        'all_structural_cells':cover(scan['cells'],profile['full_width_regions']),
        'all_top_entry_cells':cover(scan['cells'],profile['full_width_regions'],profile['carry_entry_all_operands_unknown_and_target_zero'])}
(r/'combo-cover.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:{a:b for a,b in v.items() if a not in ('selected_cells','selected_cell_indices')} if isinstance(v,dict) else v for k,v in result.items()},indent=2))
