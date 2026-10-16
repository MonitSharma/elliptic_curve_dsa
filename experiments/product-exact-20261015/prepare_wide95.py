"""Declare a fixed rank-only extension of wide67, preserving its accepted scratch."""
import copy,hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'wide-to95-rank-20261016';d.mkdir(exist_ok=True);assert not (d/'DECLARATION.json').exists()
base=json.loads((r/'WIDE67_FREEZE.json').read_text());cycle=[('retained',128,'start'),('retained',512,'proxy'),('retained',1024,'start'),('anf',512,'proxy'),('retained',128,'proxy'),('retained',512,'start'),('retained',1024,'proxy')]
stages=copy.deepcopy(base['stages'])
for mode,cap,rank in cycle*4:stages.append({'family':mode,'atom_cap':cap,'pair_cap':64,'product_cap':1000000,'rank':rank,'split':True,'extra_zero_slots_offered':0,'flags':'three per donor; disjoint top-level lifetimes'})
assert len(stages)==95
plan={'source_freeze':'WIDE67_FREEZE.json','source_freeze_sha256':hashlib.sha256((r/'WIDE67_FREEZE.json').read_bytes()).hexdigest(),'input_stream':base['external_stream'],'input_stream_sha256':base['external_stream_sha256'],'baseline_stream':'/home/hclau/ecdsa_research/nonce-screen-20261015/final-census/ops.bin','base_revision':base['base_revision'],'stages':stages,'fixed_endpoint':95,'checkpoints':[74,81,88,95],'analysis_threads':1,'address_limit_GiB':24,'scope':'Toffoli objective. Uses existing wide67 quantum scratch; no additional quantum slots offered in these rank cycles. Full original5a-versus-checkpoint anchored512-state/classical/phase/scratch comparisons. Same exact compactflag cache kernel, every lease freshly derived. All four cycles and final95 endpoint fixed before metrics; no packet-selected stopping, nonce or score claim. Preserve resource failures.','nonce_search_performed':False,'score':None}
(d/'DECLARATION.json').write_text(json.dumps(plan,indent=2)+'\n');print('DECLARED_FIXED_WIDE95',flush=True)
