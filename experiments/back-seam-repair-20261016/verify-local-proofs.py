from pathlib import Path
import json,hashlib,shutil
r=Path('/home/hclau/ecdsa_research/back-seam-repair-20261016');sites=json.loads((r/'regions-C.json').read_text());prefix=json.loads((r/'prefix-zero-receipt.json').read_text())['results'];exact=json.loads((r/'prefix-exact-zero-receipt.json').read_text())['results']
for j,s in enumerate(sites):
 for mode in ['old','new']:
  p=json.loads((r/f'{mode}-phase-contract-{j}.json').read_text());assert p['phase_contract_proved']and not p['q_contract_unresolved']and p['outer_caps']==0 and p['mr']==39 and p['n']==20 and p['protected_arbitrary_bitplane_cases']==4096
  assert p['borrow']==(None if mode=='old'else s['target']);assert p['classical_prepend']==(None if mode=='old'else[s['lower_q'],s['lower_classical_bit'],True])
  q=next(row for row in prefix if row['site']==j and row['kind']=='comparator carries');assert sorted(q['qubits'])==p['clean_scratch_preconditions']and not q['unresolved']
 assert(r/f'negative-phase-contract-{j}.exit').read_text().strip()=='101'
 assert json.loads((r/f'middle-interface-{j}.json').read_text())['proved']
 assert len(next(row for row in prefix if row['site']==j and row['kind']=='R5 auxiliary')['unresolved'])==105
 assert len(next(row for row in exact if row['site']==j and row['kind']=='R5 auxiliary')['unresolved'])>0
cases=improved=0
for u in range(256):
 for c in range(256):
  for k in range(2,8):
   hu=u>>(8-k);hc=c>>(8-k);low=7-k;seed=((~u>>low)&1)*((c>>low)&1);carry=(((~hu)&((1<<k)-1))+hc+seed)>>k;pk=int(hu<hc);pk1=int((u>>low)<(c>>low));assert carry==pk1 and pk<=pk1<=int(u<c);cases+=1;improved+=pk1>pk
(r/'precision-ordering-verification.json').write_text(json.dumps(dict(cases=cases,strict_improvements=improved,all_unsigned_reduced_operands_exhaustive=True,relation='P20<=P21<=fullcomparison; never assume comparison==overflow',arbitrary_entry_and_MR_local_contracts_passed=True),indent=2)+'\n')
p=r/'candidate-source.json';shutil.copy2(p,r/'candidate-source-before-guardfix.json');meta=json.loads(p.read_text());meta['files']={str(p.relative_to(r/'candidate')):hashlib.sha256(p.read_bytes()).hexdigest()for p in(r/'candidate/src/point_add').rglob('*')if p.is_file()};meta['guard_negative_test_index_corrected']=True;meta['admission']=json.loads((r/'ADMISSION-D.json').read_text());p.write_text(json.dumps(meta,indent=2)+'\n')
print('ALL_LOCAL_PROOFS_PASS; inherited_R5_unresolved ternary105each, exact104/105 explicitly retained; exhaustive precision ordering',cases)
