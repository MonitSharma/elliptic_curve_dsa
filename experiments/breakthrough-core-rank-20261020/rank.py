import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;p=r/'CORE-TRUTH.json';d=json.loads(p.read_text());vectors=[sum(v<<(64*i)for i,v in enumerate(words))for words in d['qubit_truth_words']];one=(1<<256)-1
def add(basis,v,coefficient=0):
 while v:
  j=v.bit_length()-1
  if j not in basis:basis[j]=(v,coefficient);return True,coefficient
  old,mask=basis[j];v^=old;coefficient^=mask
 return False,coefficient
inputs=[vectors[q]for q in d['source_qubits']]+[one];basis={};labels=[f'q{q}'for q in d['source_qubits']]+['one']
for i,v in enumerate(inputs):add(basis,v,1<<i)
input_rank=len(basis);outputs=[]
for form in d['output_forms']:
 v=one if form['one']else 0
 for q in form['wires']:v^=vectors[q]
 outputs.append(v)
output_basis=dict(basis)
for v in outputs:add(output_basis,v)
dependencies=[]
for q,v in enumerate(vectors):
 if q in d['source_qubits']:continue
 index=len(labels);independent,mask=add(basis,v,1<<index)
 if independent:labels.append(f'q{q}')
 else:
  mask^=1<<index;dependencies.append({'qubit':q,'xor_of_available_forms':[labels[i]for i in range(len(labels))if mask>>i&1]})
result={'status':'EXACT_NATIVE_EIGHT_BIT_FUNCTION_RANK_ANALYSIS','native_truth_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
 'emitted_core_ccx':d['emitted_ccx'],'input_affine_rank':input_rank,'input_and_output_rank':len(output_basis),'output_nonlinear_dimension':len(output_basis)-input_rank,
 'input_and_all_computed_wire_rank':len(basis),'computed_wire_linear_dependencies':dependencies,'supported_signed_inputs_verified':d['supported_signed_inputs_verified'],
 'outside_promised_range_math_mismatches':d['outside_promised_range_math_mismatches'],
 'scope':'Rank bound concerns the actual full eight-bit truth function in an XOR/AND straight-line model, with inputs independent. Not a general reversible/in-place/multioutput gate lower bound or a point-add lower bound; conditional domain restrictions differ. Any proposed rewrite needs full lifetime, phase and native validation.'}
(r/'CORE-RANK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
