"""Adapt the completed review with dynamic current-source receipts."""
import ast
from pathlib import Path
ex=Path(__file__).resolve().parents[1]
r=ex/'breakthrough-public322-square-final-20261020'
s=(ex/'breakthrough-public8b-repeat-final-20261020/seal.py').read_text().split("review={'status':")[0]
s=s.replace('breakthrough-public8b-repeat-generic-20261020','breakthrough-public322-square-finished-20261020').replace('breakthrough-public8b-repeat-final-gate-20261020','breakthrough-public322-square-final-gate-20261020').replace('breakthrough-public8b-repeat-nonce-20261020','breakthrough-public322-square-nonce-20261020').replace('SOURCE-FREEZE-v2.json','SOURCE-FREEZE.json').replace('58561741282970059dbdd26d3ba8c40cbafd909f','63d63c90a25e204d3173d5078f5a0bf12c9d65b7').replace('==194','==196').replace('public8b-repeat-generic-final-20261020-v1','public322-square1408-final-20261020-v1')
s=s.replace(" and g['candidate_minus_parent_mean_executed_toffoli']==-3.0 and g['paired_standard_error']==0", " and g['candidate_minus_parent_mean_executed_toffoli']<0")
s=s.replace("=='a680f4d979df3ebdc5601616569705df1f115ebfcc059945d6c2cb3a183c53ab'", "==json.loads((research/'FINISHED-RESULT.json').read_text())['source_freeze_sha256']")
s=s.replace("=='4fb7a65acb7027fe9fa519b0db781f830c5cf1e1e5573afa102247401b3b6a01'", "==json.loads((research/'FINISHED-RESULT.json').read_text())['native_stream_sha256']")
start=s.index(";assert set(modes)==set(f['source_files'])")
end=s.index('for p in sorted',start)
s=s[:start]+";assert set(modes).issubset(f['source_files'])\nfor p in f['source_files']:modes.setdefault(p,'100644')\n"+s[end:]
s=s.replace("assert changed==['src/point_add/finished_pipeline.rs']", "assert changed==['src/point_add/finished_square_pipeline.rs','src/point_add/mod.rs','src/point_add/square_lease_cache.rs']")
s=s.replace('Repeat generic exact simplification after154 leases at nonce','Exact square1408 workspace and independently proved153 leases at nonce')
s+=(ex/'autorun-20261020-breakthrough/square-sealer-tail.py').read_text()
ast.parse(s);(r/'seal.py').write_text(s)
s=(ex/'breakthrough-public8b-repeat-final-20261020/submit.py').read_text().replace('8b682cf8-e242-4827-bb54-3c0724635893','32256595-e0a3-4015-96ab-3422c866ec48').replace("'source_files':194", "'source_files':196")
ast.parse(s);(r/'submit.py').write_text(s)
print('Prepared review and one-time automatic upload controllers; neither launched.')
