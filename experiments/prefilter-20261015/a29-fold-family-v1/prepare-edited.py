from pathlib import Path
import json
r=Path(__file__).resolve().parents[1];out=r/'a29-edited-folds-v1';out.mkdir(exist_ok=True)
def put(p,s):p.write_bytes(s.encode())
bounds={129:(4003168,4012206),131:(4063748,4074779),133:(4119372,4130403),134:(4147205,4158236),135:(4175038,4186069),136:(4203115,4214146)}
put(out/'raw-hints.json',json.dumps(dict(status='RAW_BOUNDARIES_ONLY_NOT_ACTUAL_FINAL_REGIONS',hints=[dict(kind='shadow',tick=t,old_start=a,old_end_exclusive=b)for t,(a,b)in bounds.items()]),indent=2)+'\n')
family=json.loads((r.parent/'precision-family-20261016/FAMILY-A.json').read_text())
guide=dict(rows=[dict(hint=dict(old_start=x['raw_begin']),mapping=dict(start=x['final_begin']))for x in family['records']])
put(out/'raw-to-original-guide.json',json.dumps(guide,indent=2)+'\n')
put(out/'prepare-second.py','''from pathlib import Path
import json
r=Path(__file__).parent
p=json.loads((r/'original-candidates.json').read_text())
assert p['mapped_shadow']==p['hints']==6 and p['unmapped']==0
hints=[dict(kind='shadow',tick=x['hint']['tick'],old_start=x['mapping']['start'],old_end_exclusive=x['mapping']['end_exclusive'])for x in p['rows']]
(r/'original-final-hints.json').write_text(json.dumps(dict(status='ACTUAL_ORIGINAL_ENDPOINT_CANDIDATES_REQUIRE_PROOF',hints=hints),indent=2)+'\\n')
''')
put(out/'run.sh','''#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > a29-edited-folds-v1/run.pid
trap 'echo $? > a29-edited-folds-v1/run.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
free -m > a29-edited-folds-v1/run.resources
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -25 >> a29-edited-folds-v1/run.resources
printf '%s  %s\\n' ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69 ../prefilter-macro-20261016/raw-builder.bin 2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e ../product-exact-20261015/tip/ops.bin 1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522 ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin | sha256sum --check || exit $?
timeout 180 /usr/bin/time -v prlimit --as=8589934592 -- tool/target/release/a29_contract_map_v3 ../prefilter-macro-20261016/raw-builder.bin ../product-exact-20261015/tip/ops.bin a29-edited-folds-v1/raw-hints.json a29-edited-folds-v1/raw-to-original-guide.json > a29-edited-folds-v1/original-candidates.json 2> a29-edited-folds-v1/original-map.log || exit $?
python3 a29-edited-folds-v1/prepare-second.py || exit $?
timeout 180 /usr/bin/time -v prlimit --as=8589934592 -- tool/target/release/a29_contract_map_v3 ../product-exact-20261015/tip/ops.bin ../product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin a29-edited-folds-v1/original-final-hints.json a29-mask-v2/candidates-v3.json > a29-edited-folds-v1/a29-candidates.json 2> a29-edited-folds-v1/a29-map.log
''')
