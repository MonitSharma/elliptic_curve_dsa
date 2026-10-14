"""Fund q23 on the unused switch lane in a restricted pure-HR envelope.

The payload digit capacity becomes24; mixed/crossing quotient ownership
remains23. No nonce changes and no Q692/full-record claim.
"""
from pathlib import Path
import shutil
import subprocess
import sys

source,dest=map(lambda s:Path(s).resolve(),sys.argv[1:3])
assert not subprocess.check_output(['git','-C',str(dest),'status','--porcelain'],text=True).strip()
for name in ['frogdrop.rs','midg.rs','tests_midg_k24.rs','pointadd_frogdrop.rs']:
    shutil.copyfile(source/'src/point_add'/name,dest/'src/point_add'/name)
path=dest/'src/point_add/midg.rs';text=path.read_text()
old='let kmax = bmax.min(mt).min(if n == 276 && k == 17 { 23 } else { usize::MAX });'
assert text.count(old)==1
text=text.replace(old,'''// sc.sw is a ninth SZ bit in the wide first column: exclude that
    // envelope, all incoming switched layouts and every mixed/done mode.
    let cap24 = n==276 && k==17 && nq==128 && sx.len()==8 && dirty.len()==259
        && cp.h==19 && cp.sz.0>=101 && cp.hr && !cp.ht && !cp.sw && !cp.dn
        && !cp.dl && !cp.dq && !cp.psw && !cp.tt && cp.sz.1<=255
        && cp.sy.1.checked_add(23).is_some_and(|top|top<128);
    let kmax = bmax.min(mt).min(if n==276 && k==17 {if cap24{24}else{23}}else{usize::MAX});''')
text=text.replace('&[(127,1),(126,2),(124,4),(120,8),(112,16),(96,32),(96,64),(126,96),(127,98)]',
                  '&[(127,1),(126,2),(124,4),(120,8),(112,16),(96,32),(96,64),(126,96)]')
text=text.replace('&[(127,0),(127,99),(124,100),(120,104),(112,112)]',
                  '&[(127,0),(126,98),(124,100),(120,104),(112,112)]')
old='let external_q = |kb: usize| if precision25 && (k + 1..=k + 5).contains(&kb) { Some(sx[kb - k]) } else { None };'
assert text.count(old)==1
text=text.replace(old,'let external_q = |kb: usize| if cap24 && kb==23 {Some(sc.sw)} else if precision25 && (k+1..=k+5).contains(&kb){Some(sx[kb-k])}else{None};')
text=text.replace('assert!(!precision25 || (k + 1 == 18 && kmax <= 23));',
                  'assert!(!precision25 || (k+1==18 && kmax<=if cap24{24}else{23}));')
old='reserve.truncate(nres);'
assert text.count(old)==1
text=text.replace(old,old+'\n        if cap24 && reserve.contains(&sc.sw) {reserve.retain(|qid|*qid!=sc.sw);reserve.push(sc.sw);}')
old='if relocated19 && kb == k + 1 { continue; }'
assert text.count(old)==1
text=text.replace(old,old+'\n            if cap24 && kb==23 && q129.last()==Some(&sc.sw) {continue;}')
old='let norm_act = if precision25 {normalize_sz_donors(b,&sc.sz,&fd.sy,act,&dirty)} else {vec![]};'
assert text.count(old)==1
text=text.replace(old,old+'\n    let pre23 = if cap24 {Some(preposition_qk(b,&q129a,&fd.sy,sc.sw,23,act,(cp.sy.0.max(1),cp.sy.1.min(104)),&dirty))}else{None};')
old='b.play(&norm_act,false);\n        b.play(&park, false);'
assert text.count(old)==2
text=text.replace(old,'b.play(&norm_act,false);\n        if let Some(p)=&pre23{b.play(p,false);}\n        b.play(&park, false);')
old='b.play(&park, false);\n        b.play(&norm_act,true);'
assert text.count(old)==2
text=text.replace(old,'b.play(&park, false);\n        if let Some(p)=&pre23{b.play(p,false);}\n        b.play(&norm_act,true);')
path.write_text(text)
path=dest/'src/point_add/pointadd_frogdrop.rs';text=path.read_text();assert text.count('pub const QB: usize = 23;')==1;path.write_text(text.replace('pub const QB: usize = 23;','// Payload digit capacity24; midg funds quotient q23 only in its guarded pure-HR columns.\npub const QB: usize = 24;'))
