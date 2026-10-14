"""N274 component prototype with explicit SX6 q21 relocation, never scoring."""
from pathlib import Path
import re,shutil,subprocess,sys
source,dest=map(lambda s:Path(s).resolve(),sys.argv[1:3])
assert not subprocess.check_output(['git','-C',str(dest),'status','--porcelain'],text=True).strip()
for relative in subprocess.check_output(['git','-C',str(source),'diff','HEAD','--name-only'],text=True).splitlines():
    assert relative.startswith('src/point_add/');shutil.copyfile(source/relative,dest/relative)
def replace(t,old,new):
    assert old in t,old
    return t.replace(old,new)
p=dest/'src/point_add/pointadd_frogdrop.rs';t=p.read_text();t=replace(t,'pub const N: usize = 275;','pub const N: usize = 274;');t=replace(t,'pub const K: usize = 16;','pub const K: usize = 15;');p.write_text(t)
p=dest/'src/point_add/midg.rs';t=p.read_text()
for old,new in [('n==275','n==274'),('n == 275','n == 274'),('k==16','k==15'),('k == 16','k == 15'),('cp.h==18','cp.h==17'),('cp.h == 18','cp.h == 17'),('q[120..128]','q[119..128]'),('ring[n - 24..n]','ring[n - 23..n]'),('reciprocal_r.len(), 24','reciprocal_r.len(), 23'),('k + 1, 17','k + 1, 16'),('k+1==17','k+1==16'),('&[(127,1),(126,2),(124,4),(120,8),(112,16),(96,32),(96,64),(127,96)]','&[(127,1),(126,2),(124,4),(120,8),(112,16),(96,32),(96,64)]'),('&[(127,0),(127,97),(126,98),(124,100),(120,104),(112,112)]','&[(127,0),(96,96)]')]:t=replace(t,old,new)
# Low-six-bit residues32 and33 both reconstruct SZ bit7 on101..161.
t=replace(t,'literals.extend((0..6).map(|i|(sz[i],i!=5)))','literals.extend((1..6).map(|i|(sz[i],i!=5)))')
t=replace(t,'c.extend((0..6).map(|i|(sz[i],i!=5)))','c.extend((1..6).map(|i|(sz[i],i!=5)))')
t=t.replace('SZ101..160','SZ101..161')
t=replace(t,'else if precision25 && (k+1..=k+5).contains(&kb)','else if precision25 && kb==21 {Some(sx[6])} else if precision25 && (k+1..=k+5).contains(&kb)')
# Both cycles retain9 reserve owners, but SX6 is the dedicated last owner.
old='if cap24 && reserve.contains(&sc.sw) {reserve.retain(|qid|*qid!=sc.sw);reserve.push(sc.sw);}'
new='if precision25 {reserve.retain(|qid|*qid!=sx[6]);reserve.push(sx[6]);}'
t=replace(t,old,new)
t=replace(t,'Some(preposition_qk(b,&q129a,&fd.sy,sc.sw,23,act,','Some(preposition_nonlast_qk(b,&q129a,&fd.sy,sc.sw,23,act,')
needle='let norm_sw = if precision25'
at=t.index(needle)
t=t[:at]+'''let pre21 = if precision25 && cp.sy.0.max(1)<=cp.sy.1.min(116) {Some(preposition_qk(b,&q129a,&fd.sy,sx[6],21,act,(cp.sy.0.max(1),cp.sy.1.min(116)),&dirty))}else{None};
    '''+t[at:]
t=replace(t,'if cap24 && (kb==22||kb==23) && q129.last()==Some(&sc.sw) {continue;}','if precision25 && kb==21 {continue;}\n            if cap24 && (kb==22||kb==23) {continue;}')
# A windows: normalize first; q21 then22/23, and reverse23/22 then21.
t=replace(t,'if let Some(p)=&pre22{b.play(p,false);}','if let Some(p)=&pre21{b.play(p,false);}\n        if let Some(p)=&pre22{b.play(p,false);}')
t=replace(t,'if let Some(p)=&pre22{b.play(p,false);}\n        b.play(&norm_act,true);','if let Some(p)=&pre22{b.play(p,false);}\n        if let Some(p)=&pre21{b.play(p,false);}\n        b.play(&norm_act,true);')
# Previous replacement also insertedpre21 on the return side; undo that
# insertion immediately beforepre22 there, retaining its trailinginverse.
t=t.replace('if let Some(p)=&pre23{b.play(p,false);}\n        if let Some(p)=&pre21{b.play(p,false);}\n        if let Some(p)=&pre22{b.play(p,false);}\n        if let Some(p)=&pre21{b.play(p,false);}','if let Some(p)=&pre23{b.play(p,false);}\n        if let Some(p)=&pre22{b.play(p,false);}\n        if let Some(p)=&pre21{b.play(p,false);}')
# B payload: pre16's existing owner is now non-last; it clearsSX1 before
# q21 can targetit. The inverse order returnsboth outside the parked core.
t=replace(t,'Some(preposition_qk(b, &q129b, &fd.sy, sx[1], k + 1, actl,','Some(preposition_owned_qk(b, &q129b, &fd.sy, sx[1], k + 1, actl,')
needle='super::frogdrop_col::mark(b, 1501);'
t=replace(t,needle,'let pre21b = if precision25 && cp.sy.0.max(1)<=cp.sy.1.min(116) {Some(preposition_qk(b,&q129b,&fd.sy,sx[6],21,actl,(cp.sy.0.max(1),cp.sy.1.min(116)),&dirty))}else{None};\n            '+needle)
t=replace(t,'if let Some(p) = &pre19 { b.play(p, false); }\n            super::frogdrop_col::mark(b, 1502);','if let Some(p) = &pre19 { b.play(p, false); }\n            if let Some(p) = &pre21b { b.play(p, false); }\n            super::frogdrop_col::mark(b, 1502);')
t=replace(t,'super::frogdrop_col::mark(b, 1504);\n            if let Some(p) = &pre19','super::frogdrop_col::mark(b, 1504);\n            if let Some(p) = &pre21b { b.play(p, false); }\n            if let Some(p) = &pre19')
t=replace(t,'!sx[1..=5].contains(q)','!sx[1..=6].contains(q)')
t+='''
// A non-last original q16 owner can share the cycle with the last q21
// owner. Preserve the admitted9-reserve domain; targetvalues must be
// established by normalization/preposition ordering at the callsite.
pub(crate) fn preposition_owned_qk(b:&mut B,cycle:&[QubitId],sy:&[QubitId],owner:QubitId,bit:usize,act:QubitId,range:(usize,usize),dirty:&[QubitId])->Vec<G>{
    assert!(cycle.contains(&owner));
    rec(b,|b|{let lane=|value:usize|{let index=value+bit;if index<cycle.len()&&cycle[index]!=owner{Some(cycle[index])}else{None}};
        super::mid2::dec_swap(b,sy,range.0,range.1,&lane,owner,&[(act,false)],&[],&[],dirty);})
}
''';p.write_text(t)
p=dest/'src/point_add/frogdrop_col.rs';t=p.read_text()
t=replace(t,'let sy_free = lean_park;','let sy_free = lean_park || (extra>=3 && cp.sz!=(0,0));')
t=replace(t,'if nc > 0 { park.push(sc.sw); }','if lean_park && nc > 0 { park.push(sc.sw); }')
t=replace(t,'if extra == 0 && park.len() < nc { park.push(sc.bq); }','if lean_park && extra == 0 && park.len() < nc { park.push(sc.bq); }')
t=replace(t,'while park.len() < nc { park.push(free.pop().unwrap()); }','while park.len() < if lean_park {nc}else{0} { park.push(free.pop().unwrap()); }')
t=replace(t,'if extra>2 {assert_eq!(extra,3);extension.push(q[119]);}','if extra>2 {assert!((3..=4).contains(&extra));extension.push(q[119]);}\n                    if extra>3 {extension.push(q[118]);}')
p.write_text(t)
# Adapt only previously appended current-geometry fixtures; never replace
# digits inside source input hexstrings or historical primitive constructors.
p=dest/'src/point_add/tests_midg_k24.rs';t=p.read_text();start=t.index('#[test]\nfn reserve9_columns_crossing_3713_positive_native');prefix=t[:start];tail=t[start:]
for old,new in [('alloc_n(275)','alloc_n(274)'),('ring[..18]','ring[..17]'),('ring[274]','ring[273]'),('ring[17]','ring[16]'),('ring[17..18+TC]','ring[16..17+TC]'),('ring[17+i]','ring[16+i]'),('q[120..128]','q[119..128]'),('ring[251..275]','ring[251..274]'),('ring[243..275]','ring[242..274]'),('ring[275-k..275]','ring[274-k..274]'),('size<=96','size<=95'),('syvalue<=96','syvalue<=95'),('else{24}','else{23}'),('size>=97','size>=96'),('syv>=97','syv>=96'),('96usize,97,128','95usize,96,128'),('boundaries=96,97,128','boundaries=95,96,128'),('n275_','n274_')]:tail=tail.replace(old,new)
tail=re.sub(r'"(?:\\.|[^"\\])*"|\b692\b',lambda m:m[0]if m[0].startswith('"')else'691',tail)
# Only exact test-boundary source expressions change; inputhexstrings do not.
tail=tail.replace('[101usize,127,128,160][lane%4]','[101usize,127,128,160,161][lane%5]')
tail=tail.replace('SZ_boundaries=101,127,128,160','SZ_boundaries=101,127,128,160,161')
p.write_text(prefix+tail)
p=dest/'src/point_add/tests_frogdrop.rs';t=p.read_text();a=t.index('#[test]\nfn n275_ordinary_three_lane_map_exact');prefix=t[:a];tail=t[a:].replace('n275_','n274_').replace('three_lane','four_lane').replace('cp.n == 275','cp.n == 274').replace('(275, 21, 28,','(274, 21, 28,').replace('b.width(), 692','b.width(), 691');p.write_text(prefix+tail)
