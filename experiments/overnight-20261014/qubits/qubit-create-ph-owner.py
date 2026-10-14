"""Isolate pure-HR q22 on PH at unchanged Q693 geometry.

This extends the existing act lifetime rather than reading PH while it
holds quotient data. N275 and all other source geometry remain unchanged.
"""
from pathlib import Path
import shutil
import subprocess
import sys

source,dest=map(lambda s:Path(s).resolve(),sys.argv[1:3])
assert not subprocess.check_output(['git','-C',str(dest),'status','--porcelain'],text=True).strip()
for name in ['frogdrop.rs','midg.rs','pointadd_frogdrop.rs','tests_midg_k24.rs']:
    shutil.copyfile(source/'src/point_add'/name,dest/'src/point_add'/name)
path=dest/'src/point_add/midg.rs';text=path.read_text()
old='let external_q = |kb: usize| if cap24 && kb==23 {Some(sc.sw)}'
assert text.count(old)==1;text=text.replace(old,'let external_q = |kb: usize| if cap24 && kb==22 {Some(ph)} else if cap24 && kb==23 {Some(sc.sw)}')
old='if cap24 && kb==23 && q129.last()==Some(&sc.sw) {continue;}'
assert text.count(old)==1;text=text.replace(old,'if cap24 && (kb==22||kb==23) && q129.last()==Some(&sc.sw) {continue;}')
old='let pre23 = if cap24 {Some(preposition_qk(b,&q129a,&fd.sy,sc.sw,23,act,(cp.sy.0.max(1),cp.sy.1.min(104)),&dirty))}else{None};'
assert text.count(old)==1;text=text.replace(old,old+'\n    let pre22 = if cap24 {Some(preposition_nonlast_qk(b,&q129a,&fd.sy,ph,22,act,(cp.sy.0.max(1),cp.sy.1.min(104)),&dirty))}else{None};')
old='if let Some(p)=&pre23{b.play(p,false);}\n        b.play(&park, false);'
assert text.count(old)==2;text=text.replace(old,'if let Some(p)=&pre22{b.play(p,false);}\n        if let Some(p)=&pre23{b.play(p,false);}\n        b.play(&park, false);')
old='if let Some(p)=&pre23{b.play(p,false);}\n        b.play(&norm_act,true);'
assert text.count(old)==2;text=text.replace(old,'if let Some(p)=&pre23{b.play(p,false);}\n        if let Some(p)=&pre22{b.play(p,false);}\n        b.play(&norm_act,true);')
start=text.index('// ---------------- HR: binary search')
end=text.index('if !stage(b) { return; } // 3',start)
part=text[start:end];call='mc_xor(b, &hr_lits, act, &[], &dirty);';assert part.count(call)==2
last=part.rindex(call);part=part[:last]+'if !cap24 { '+call+' }'+part[last+len(call):];text=text[:start]+part+text[end:]
start=text.index('// D^-1:')
end=text.index('if !stage(b) { return; } // 4',start)
part=text[start:end];assert part.count(call)==2;first=part.index(call);part=part[:first]+'if !cap24 { '+call+' }'+part[first+len(call):];text=text[:start]+part+text[end:]
helper=r'''

pub(crate) fn preposition_nonlast_qk(b:&mut B,cycle:&[QubitId],sy:&[QubitId],
                     owner:QubitId,bit:usize,act:QubitId,range:(usize,usize),dirty:&[QubitId])->Vec<G>{
    assert!(cycle.contains(&owner));assert!(range.1+bit<128);
    super::frogdrop_col::rec(b,|b|{
        let lane=|value:usize|{let index=value+bit;if index<128&&cycle[index]!=owner{Some(cycle[index])}else{None}};
        super::mid2::dec_swap(b,sy,range.0,range.1,&lane,owner,&[(act,false)],&[],&[],dirty);
    })
}
'''
text+=helper;path.write_text(text)
