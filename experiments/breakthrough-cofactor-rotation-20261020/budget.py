"""Cost the conservative unrestricted-control storage plan, not a circuit score.

The horizon138 is an illustrative comparison horizon. It is not a newly
proved convergence bound for any GCD, nor an admissible iteration cut.
"""
import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent
bounds=[2,1];rows=[]
for tick in range(138):
    ti=tick%2;si=1-ti
    target=bounds[ti]+7*bounds[si]
    source=bounds[si]<<6
    n=max(9,1+max(target,source).bit_length())
    pairs=3*n//2-2 if n%2==0 else 3*(n-1)//2
    ordinary_cost=3*(n-1)+pairs+19
    rows.append({'tick':tick,'signed_equal_word_width':n,'target_bound':str(target),'source_bound':str(source),
                 'reflection_pairs':pairs,'ordinary_component_ccx':ordinary_cost})
    bounds[ti]=target;bounds[si]=source
partial=sum(x['ordinary_component_ccx']for x in rows[1:])
profile=json.loads((r.parent/'breakthrough-domain-profile-20261020/DIRECT-DOMAIN-PROFILE.json').read_bytes())
payload={phase:sum(v for k,v in profile['mean_executed_toffoli'].items()if k.startswith(phase+'/payload_'))for phase in ['divide','multiply']}
result={'status':'CONSERVATIVE_INTEGRATION_PLAN_DEPRIORITIZED_NOT_AN_IMPOSSIBILITY_PROOF',
    'horizon':138,'horizon_is_not_a_convergence_bound':True,
    'bound_proof':'If |C|<=A and |D|<=B, all q in{+-1,+-3,+-5,+-7},e in3..6 satisfy |C+qD|<=A+7B and |2^eD|<=64B, including every signed-add intermediate. Induct from[2,1].',
    'bound_domain':'Unrestricted ordinary component controls, broader than seeded GCD reachable states. A tighter proved reachable-state bound remains possible.',
    'ordinary_forward_component_ccx_excluding_first_exception':partial,
    'ordinary_forward_plus_inverse_component_ccx_excluding_first_exception':2*partial,
    'at_last_tick_equal_width_cofactor_wires':2*rows[-1]['signed_equal_word_width'],
    'existing_raw_payload_diagnostic_mean_toffoli':payload,
    'decision':'Do not integrate this conservative equal-word plan into point addition. Its two-way cofactor arithmetic alone exceeds an existing raw payload pass, and the cofactor words alone already occupy1004 wires before live coordinates, rails, history and scratch.',
    'omitted_costs':['First exceptional macro-step.','Complete GCD endpoint and a valid fixed horizon.','Final variable-power-of-two modular normalization.','Multiplication into the live coordinate and its cleanup.','All rail arithmetic, complete width and final optimized point-add measurement.'],
    'scope':'Analytic partial budget of one specified plan. No complete circuit, full resource lower bound, newly scored result, gate census or nonce search.',
    'rows':rows}
(r/'CONSERVATIVE-BUDGET.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in result.items()if k!='rows'},indent=2))
