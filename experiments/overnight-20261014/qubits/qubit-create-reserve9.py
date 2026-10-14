"""Integrate two admitted SZ donors into crossing reserve, in a clean checkout.

Only point_add changes. QB23 and preserved nonce remain fixed. Component
validation required; no full benchmark or record claim.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

source,dest=map(lambda x:Path(x).resolve(),sys.argv[1:3])
assert not subprocess.check_output(['git','-C',str(dest),'status','--porcelain'],text=True).strip()
for name in ['frogdrop.rs','midg.rs','tests_midg_k24.rs']:
    shutil.copyfile(source/'src/point_add'/name,dest/'src/point_add'/name)
path=dest/'src/point_add/midg.rs';text=path.read_text()
text=text.replace('cp.sz.0 >= 65 && cp.sz.1 <= 256','cp.sz.0 >= 101 && cp.sz.1 <= 256')
start=text.index('pub(crate) fn stage1_v_compact_partitioned(')
end=text.index('// A V-form whose quotient reserve',start)
part=text[start:end];assert part.count('if szr.1 + j >= 257 {')==1
part=part.replace('if szr.1 + j >= 257 {','if small && szr.1 + j >= 257 {')
text=text[:start]+part+text[end:]
old='let prot = rec(b, |b| rot_by_range_care(b, &ring, &sc.sz, cp.sz.0, cp.sz.1, true, &dirty, &dest_r));'
assert text.count(old)==1
text=text.replace(old,'let prot = if precision25 { care_borrowed_sz(b,&ring,&sc.sz,&fd.sy,&dest_r,true,&dirty) } else { rec(b, |b| rot_by_range_care(b, &ring, &sc.sz, cp.sz.0, cp.sz.1, true, &dirty, &dest_r)) };')
text=text.replace('let nres = park_reserve();','let nres = if precision25 { assert_eq!(park_reserve(),7); 9 } else { park_reserve() };')
old='let mut reserve: Vec<QubitId> = vec![c0, pzero, sx[6], sx[7]];'
assert text.count(old)==1
text=text.replace(old,old+'\n        if precision25 { reserve.extend([sc.sz[6],sc.sz[7]]); }')
old='let rz = rotz(b, &(0..kmax).collect::<Vec<_>>());'
assert text.count(old)==1
text=text.replace(old,'let rz = if precision25 { let dest=(0..kmax).collect(); care_borrowed_sz(b,&ring,&sc.sz,&fd.sy,&dest,true,&dirty) } else { rotz(b, &(0..kmax).collect::<Vec<_>>()) };')
old='let sy7_normal = borrowed_sy_normal(b, &fd.sy, &dirty);'
assert text.count(old)==1
text=text.replace(old,old+'\n    let norm_act = if precision25 {normalize_sz_donors(b,&sc.sz,&fd.sy,act,&dirty)} else {vec![]};\n    let norm_sw = if precision25 {normalize_sz_donors(b,&sc.sz,&fd.sy,sc.sw,&dirty)} else {vec![]};')
old='b.play(&sy7_normal, false);\n        b.play(&park, false);'
assert text.count(old)==2
text=text.replace(old,'b.play(&sy7_normal, false);\n        b.play(&norm_act,false);\n        b.play(&park, false);')
old='b.play(&park, false);\n        b.play(&sy7_normal, false);'
assert text.count(old)==2
text=text.replace(old,'b.play(&park, false);\n        b.play(&norm_act,true);\n        b.play(&sy7_normal, false);')
old='b.x(ph);\n            if let Some(p) = &pre19 { b.play(p, false); }'
assert text.count(old)==1
text=text.replace(old,'b.x(ph);\n            b.play(&norm_sw,false);\n            if let Some(p) = &pre19 { b.play(p, false); }')
old='if let Some(p) = &pre19 { b.play(p, false); }\n            b.x(ph);'
assert text.count(old)==1
text=text.replace(old,'if let Some(p) = &pre19 { b.play(p, false); }\n            b.play(&norm_sw,true);\n            b.x(ph);')
path.write_text(text)
print(json.dumps(dict(scope='Reserve9 SZ6/7 donors integrated, K25/K32 QB23; component validation pending',
                     base_revision=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip(),
                     source_sha256={f'src/point_add/{name}':hashlib.sha256((dest/'src/point_add'/name).read_bytes()).hexdigest() for name in ['frogdrop.rs','midg.rs','tests_midg_k24.rs']}),indent=2))
