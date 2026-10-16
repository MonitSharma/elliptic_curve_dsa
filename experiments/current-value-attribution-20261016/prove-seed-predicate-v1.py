from pathlib import Path
import json,hashlib
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016')
s=(r/'prove-seed-bdd.py').read_text().split('m=json.loads')[0]
needle=' return dict(all256_target_bits_match_finite53_formula='
assert s.count(needle)==1
extra='''
 # Derive an exact ENTRY predicate independently from the internal carry wires.
 less=0;equal=1
 for i in range(31,-1,-1):
  if 977>>i&1:less=b.xor(less,b.mul(equal,b.neg(initial[i])));equal=b.mul(equal,initial[i])
  else:equal=b.mul(equal,b.neg(initial[i]))
 pred=b.mul(initial[0],less)
 altered=adjusted.copy();carry=pred
 for i in range(32,53):
  old=altered[i];altered[i]=b.xor(old,carry);carry=b.mul(old,carry)
 inherited_want=altered[1:]+initial[53:]+[initial[0]]
 if ops[142][0]==8:
  assert all(q[w]==inherited_want[i]for i,w in enumerate(target))
  assert all(c==(pred if m==20 else 0)for m,c in phase.items())
 else:assert all(c==0 for c in phase.values())
'''
s=s.replace(needle,extra+needle);exec(compile(s,'independent-seed-entry-predicate','exec'))
m=json.loads((r/'actual-seed-markers.json').read_text());a,e=m['markers'];raw=load(r/'raw-seed-builder.bin');final=load(r.parent/'product-exact-20261015/tip/ops.bin');decode=lambda d,x,y:[struct.unpack_from('<7Q',d,i*56)for i in range(x,y)]
original=decode(raw,a['raw_at'],e['raw_at']);current=decode(final,a['at'],e['at']);good=prove(original,a['target']);bad=prove(current,a['target'])
out=dict(status='EXACT ENTRY-PREDICATE VALUE/PHASE CONTRACT PASS',predicate='D=(A odd) AND ((A mod 2^32)<977)',original_value='V=(A & ~((1<<53)-1)) | ((A-f*(A mod2)) mod2^53); output=(V>>1)|((A mod2)<<255)',inherited_value='V=(A & ~((1<<53)-1)) | ((A-f*(A mod2)+D*2^32) mod2^53); output=(V>>1)|((A mod2)<<255)',original_phase='0',inherited_phase='D * MR[20]',all256_entry_target_bits_arbitrary=True,all96MR_draws_arbitrary=True,required48scratch_zero=True,prefix_zero_proof='seed-prefix-pinned-v1/RECEIPT.json',no_dirty_scratch_promise=True,no_global_correctness_claim=True,proof_source_sha256=hashlib.sha256((r/'prove-seed-predicate-v1.py').read_bytes()).hexdigest(),frozen_BDD_source_sha256=hashlib.sha256((r/'prove-seed-bdd.py').read_bytes()).hexdigest(),original_BDD_nodes=good['BDD_nodes'],inherited_BDD_nodes=bad['BDD_nodes'])
(r/'seed-entry-predicate-v1.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
