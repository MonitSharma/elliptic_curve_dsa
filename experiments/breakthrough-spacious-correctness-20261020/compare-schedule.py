import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;rel='leapfrog_data/pack_t0hat_tail0_138_steps_k770_lw2.txt';paths=[ws/'wide95-703-review-20261018-085419/candidate/src/point_add'/rel,ws/'breakthrough-primed-pool-20261020/observer/src/point_add'/rel]
def parse(p):return[list(map(int,l.split()))for l in p.read_text().splitlines()if l.strip()and not l.startswith('#')]
a,b=map(parse,paths);result={'source_sha256':[hashlib.sha256(p.read_bytes()).hexdigest()for p in paths],'rows':[len(a),len(b)],'changed_rows':[[i,x,y]for i,(x,y)in enumerate(zip(a,b))if x!=y],'scope':'Parsed numeric walk schedule comparison, independent of comments and line endings.'};(r/'SCHEDULE-COMPARISON.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result))
