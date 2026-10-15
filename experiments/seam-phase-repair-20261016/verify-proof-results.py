from pathlib import Path
import json
r=Path('/home/hclau/ecdsa_research/seam-phase-repair-20261016');a=json.loads((r/'old-phase-contract.json').read_text());b=json.loads((r/'new-phase-contract.json').read_text())
assert a['phase_contract_proved']and b['phase_contract_proved']
assert not a['q_contract_unresolved']and not b['q_contract_unresolved']
assert a['mr']==b['mr']and a['n']==b['n']==20
assert a['borrow']is None and b['borrow']==767
assert a['classical_prepend']is None and b['classical_prepend']==[235,235]
assert a['all_used_entry_classical_bits_arbitrary']and b['all_used_entry_classical_bits_arbitrary']
assert a['all_internal_mr_universally_quantified']and b['all_internal_mr_universally_quantified']
assert int((r/'negative-phase-contract.exit').read_text())!=0
print('UNIVERSAL_OLD_AND_EXPANDED_PHASE_AND_QUANTUM_CONTRACTS_PASS; wrong-Clifford control rejected')
