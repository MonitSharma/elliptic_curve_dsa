from pathlib import Path
import ast
a=Path(__file__).parent;ex=a.parent;r=ex/'breakthrough-public-best-drop-final-20261020';s=(ex/'breakthrough-depth12-final-20261020/seal.py').read_text();s=s[:s.index("proof=ws/'breakthrough-depth12-context-20261020'")]
s=s.replace('breakthrough-depth12-finished-20261020','breakthrough-public-best-drop-finished-20261020').replace('breakthrough-depth12-final-gate-20261020','breakthrough-public-best-drop-final-gate-20261020').replace('breakthrough-depth12-nonce-20261020','breakthrough-public-best-drop-nonce-continuation-20261020').replace('28e443bcc2f3dc0793c6a416a496b07cfbeb4c4f','7499c902d7989e5a995ccd2331104a532197851b').replace("==205","==177").replace("'source_files':205","'source_files':177")
s=s.replace("g['label']=='depth12-context-final-20261020-v1'","g['label']=='public-best-drop-product-final-20261020-v1'").replace("g['batches']==32768 and g['candidate_minus_parent_mean_executed_toffoli']<0","g['batches']==131072")
start=s.index('rows=[json.loads(x)for x in(search/');end=s.index("assert b['status']",start)
s=s[:start]+'''from verify_search import verify_search
passes=verify_search(sr);k=sr['selected_nonce'];assert k==f['nonce'];assert json.loads((ws/'breakthrough-public-best-drop-nonce-v2-20261020/QUALIFICATION.json').read_text())['status']=='PASS';assert f'SELECTED_OFFICIAL_REPLAY nonce={k} ok=true shots=9024 classical=0 phase=0 ancilla=0'in(search/'selected-search.log').read_text()
assert b['product']<933231010,'Lowest passing packet does not improve product; never choose another nonce by cost'
''' +s[end:]
s=s.replace("f'Exactdepth12 square andfreshly proved230 contextcaches at nonce{k}'","f'Exact Q1233 carry schedule and113proved caches at nonce{k}'").replace("'production_screens':len(rows)","'production_screens':sr['production_screens']").replace("'additional_partial_packet_controls':'1..8 repeated in production;24 protected full-state scalar batches at0,70,140'","'additional_partial_packet_controls':{'attempts':sr['control_partial_packet_attempts'],'distinct_nonces':8,'protected_full_state_batches':sr['protected_full_state_control_batches'],'scope':'Every qualification repeats1..8; additional to production.'}")
s=s.replace('Complete unchanged benchmark of exactdepth12 plus freshly proved230existing-wire caches on strong grouped arithmetic; Q1464. Targets independentT versus current71, no globalproduct claim.','Complete unchanged benchmark of exact carry-schedule/reversible-comparator/113freshcache Q1233 candidate; complete product target versus exact publicacd0. IndependentT orwidth record not claimed.')
tail=(a/'product-best-sealer-tail.py').read_text();s+=tail;ast.parse(s);(r/'seal.py').write_text(s)
watch='''import subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent
try:
 subprocess.run(['python3',str(r/'finalize.py')],cwd=r,check=True)
 subprocess.run(['python3',str(r/'seal.py')],cwd=r,check=True)
 (r/'review.exit').write_text('0\\n')
except BaseException:
 (r/'review.exit').write_text('1\\n');raise
''';ast.parse(watch);(r/'watch.py').write_text(watch);print('Product finalizer, immutable sealer and local-verification-gated upload prepared.')
