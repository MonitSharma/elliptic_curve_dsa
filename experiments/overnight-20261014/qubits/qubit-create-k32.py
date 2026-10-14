"""Isolated K25/K32 partitioned reciprocal candidate, QB23 retained.

Candidate changes are confined to src/point_add. No benchmark or width claim.
The argument for Q121..127 loans is recorded in K32_LOAN_PROOF.md.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

compact, dest = map(lambda x: Path(x).resolve(), sys.argv[1:3])
subprocess.run([sys.executable, str(Path(__file__).with_name('qubit-create-k25.py')),
                str(compact), str(dest)], check=True, stdout=subprocess.DEVNULL)
path = dest/'src/point_add/midg.rs'
text = path.read_text()
start = text.index('pub fn stage1_v_compact(')
end = text.index('// A V-form whose quotient reserve', start)
copy = text[start:end]
copy = copy.replace('pub fn stage1_v_compact(', 'pub(crate) fn stage1_v_compact_partitioned(')
copy = copy.replace('window: bool) -> Vec<G>',
                    'window: bool, sy: &[QubitId], small: bool) -> Vec<G>')
copy = copy.replace('    b.begin();',
                    '    assert_eq!(s.gt.len(), 1);\n    let selectors = size_partition(sy, small);\n    b.begin();',1)
for control in ['&[(act, false), (r[0], false), (g0, true)]',
                '&[(act, false), (r[0], false)]']:
    old=f'inc_with_controls(b, &bits, {control}, &s.dirty);'
    new='for selector in &selectors { let mut controls = '+control[1:]+'.to_vec(); controls.extend(selector.iter().copied()); inc_with_controls(b, &bits, &controls, &s.dirty); }'
    assert copy.count(old)==1
    copy=copy.replace(old,new)
helper=r'''
// Exact disjoint prefix cubes on the low seven SY bits. On active shots
// SY is1..128, where0 encodes128. Inactive aliases retain act separately.
fn size_partition(sy: &[QubitId], small: bool) -> Vec<Vec<(QubitId,bool)>> {
    assert!(sy.len()>=7);
    let cubes: &[(usize,usize)] = if small {
        &[(127,1),(126,2),(124,4),(120,8),(112,16),(96,32),(96,64),(126,96),(127,98)]
    } else { &[(127,0),(127,99),(124,100),(120,104),(112,112)] };
    cubes.iter().map(|&(mask,value)| (0..7).filter(|&i|mask>>i&1!=0)
        .map(|i|(sy[i],value>>i&1==0)).collect()).collect()
}

'''
text=text[:end]+helper+copy+text[end:]
text=text.replace('cp.sz.0 >= 58 && cp.sz.1 <= 256','cp.sz.0 >= 65 && cp.sz.1 <= 256')
text=text.replace('let top_head = if precision25 { 25 } else { k };',
                  'let top_head = if precision25 { 32 } else { k };')
text=text.replace('let p_bank = if p_bank_lo < loan_end { q[p_bank_lo..loan_end].to_vec() } else { vec![] };',
                  'let p_bank = if p_bank_lo < loan_end { q[p_bank_lo..loan_end].iter().copied().filter(|qid| nq < 128 || !q[121..128].contains(qid)).collect::<Vec<_>>() } else { vec![] };')
needle='    // enter / leave the V form on the act shots:'
index=text.index(needle)
extra=r'''
    let k32 = if precision25 {
        let mut rs = s1.r.clone(); rs.extend(&q[121..128]);
        assert_eq!(rs.len(),32);
        assert!(!rs.iter().any(|qid|s1.anc.contains(qid)||s1.chain.contains(qid)||s1.andc.contains(qid)));
        let small_s = S1{r:rs,..s1.clone()};
        let z32 = ring[n-32..n].to_vec();
        let f32 = stage1_v_compact_partitioned(b,&z32,&win,&sc.sz,szr,&small_s,act,true,&fd.sy,true);
        let r32 = stage1_v_compact(b,&z32,&win,&sc.sz,szr,&small_s,act,false);
        let f25 = stage1_v_compact_partitioned(b,&zh,&win,&sc.sz,szr,&s1,act,true,&fd.sy,false);
        Some((f25,f32,r32))
    } else {None};
'''
text=text[:index]+extra+text[index:]
text=text.replace('        b.play(&fv, false);\n        b.play(&fr, true);',
                  '        if let Some((f25,f32,r32)) = &k32 {\n            b.play(f25,false); b.play(&fr,true);\n            b.play(f32,false); b.play(r32,true);\n        } else { b.play(&fv,false); b.play(&fr,true); }')
path.write_text(text)
paths=[dest/'src/point_add'/f for f in ['frogdrop.rs','midg.rs','tests_midg_k24.rs']]
print(json.dumps(dict(base_revision='c95b9325913abacca9c86bdebad10a20633cd04e',
                     scope='K25/K32 SY partition at Q693, QB23 unchanged; component validation pending',
                     nonce_changed=False, borrowed_Q_indices=list(range(121,128)),
                     source_sha256={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}),indent=2))
