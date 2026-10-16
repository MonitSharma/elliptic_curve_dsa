"""Declare exactly four further rank cycles before any generated95 source or packets."""
import copy,hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'product-to95-rank-20261016';d.mkdir(exist_ok=True);assert not (d/'DECLARATION.json').exists()
base=json.loads((r/'PRODUCT67_FREEZE.json').read_text());cycle=[('retained',128,'start'),('retained',512,'proxy'),('retained',1024,'start'),('anf',512,'proxy'),('retained',128,'proxy'),('retained',512,'start'),('retained',1024,'proxy')]
stages=copy.deepcopy(base['stages'])
for mode,cap,rank in cycle*4:stages.append({'family':mode,'atom_cap':cap,'pair_cap':64,'product_cap':1000000,'rank':rank,'split':True,'flags':'three per donor; disjoint top-level lifetimes'})
assert len(stages)==95
plan={'source_freeze':'PRODUCT67_FREEZE.json','source_freeze_sha256':hashlib.sha256((r/'PRODUCT67_FREEZE.json').read_bytes()).hexdigest(),'input_stream':base['external_stream'],'input_stream_sha256':base['external_stream_sha256'],'base_revision':base['base_revision'],'stages':stages,'fixed_endpoint':95,'checkpoints':[74,81,88,95],'analysis_threads':1,'address_limit_GiB':24,'priority':'Launch only after67 failure gate; if67 passes, complete universal67 audit first. No95 census or native source port launched by this declaration.','scope':'No additional quantum slots. Full original4b-versus-checkpoint anchored512-state/classical/phase/scratch comparisons. Same exact compactflag cache kernel, all leases freshly derived at each stage. All four cycles and stage95 endpoint fixed before metrics; do not choose an earlier checkpoint based on packets or gate outcome. Preserve resource failures and every proof row.','nonce_search_performed':False,'score':None}
(d/'DECLARATION.json').write_text(json.dumps(plan,indent=2)+'\n');print('DECLARED_FIXED95',flush=True)
