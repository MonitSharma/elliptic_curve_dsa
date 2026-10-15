"""Use the existing exact conditional-clean conjunction for quotient reflection."""
from pathlib import Path
import hashlib,json,subprocess,sys
root=Path(sys.argv[1]);v6=root/'candidate-control-fold-v6';dest=root/'candidate-control-fold-v7'
assert not dest.exists()
subprocess.run(['git','clone','--shared','--no-hardlinks',str(v6),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'apply',str(root/'candidate-control-fold-v6.patch')],check=True)
p=dest/'src/point_add/midg.rs';s=p.read_text(encoding='utf8')
for old,new in [
 ('preposition_high_q25(b,&q129a,&fd.sy[..7],act,&dirty)','preposition_high_q25_flag(b,&q129a,&fd.sy[..7],act,&dirty,sx[0])'),
 ('preposition_high_q25(b,&q129b,&fd.sy,actl,&dirty)','preposition_high_q25_flag(b,&q129b,&fd.sy,actl,&dirty,sx[0])')]:
 assert s.count(old)==1;s=s.replace(old,new)
s+='''

// The returned SX0 root retains the conjunction while its original controls
// provide conditional-clean summaries. The callback swaps disjoint data only;
// all SY/ACT controls are restored before measurement uncomputation of SX0.
pub(crate) fn preposition_high_q25_flag(b:&mut B,cycle:&[QubitId],sy:&[QubitId],act:QubitId,dirty:&[QubitId],flag:QubitId)->Vec<G>{
    assert_eq!(cycle.len(),138);assert!(sy.len()==7||sy.len()==8);
    assert!(!cycle.contains(&flag)&&!sy.contains(&flag)&&act!=flag&&!dirty.contains(&flag));
    assert!(!cycle.contains(&act)&&!sy.iter().any(|q|cycle.contains(q)));
    rec(b,|b|{for value in 1usize..=115{
        let mut pairs=std::collections::BTreeSet::new();
        for kb in 22usize..=24{if value>137-kb{continue;}let owner=140-kb;let target=value+kb;if owner!=target{pairs.insert((owner.min(target),owner.max(target)));}}
        let mut literals=vec![(act,false)];literals.extend(sy.iter().enumerate().map(|(i,&wire)|(wire,value>>i&1==0)));
        if pairs.len()<=1 {
            for (a,z) in pairs{super::mid2::mc_swap(b,&literals,cycle[a],cycle[z],&[],dirty);}
        } else {
            for &(q,negative) in &literals{if negative{b.x(q);}}
            let positive:Vec<QubitId>=literals.iter().map(|&(q,_)|q).collect();
            super::mask::with_conjunction_one_clean(b,&positive,flag,|b,roots|{
                let controls:Vec<_>=roots.iter().map(|&q|(q,false)).collect();
                for &(a,z) in &pairs{super::mid2::mc_swap(b,&controls,cycle[a],cycle[z],&[],dirty);}
            });
            for &(q,negative) in &literals{if negative{b.x(q);}}
        }
    }})
}
'''
p.write_text(s,encoding='utf8',newline='\n')
patch=subprocess.check_output(['git','-C',str(dest),'diff','HEAD','--','src/point_add/'])
(root/'candidate-control-fold-v7.patch').write_bytes(patch)
manifest=dict(candidate=str(dest),base_revision=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip(),scope='v6 plus exact conditional-clean factoring of high-quotient reflections; all bounds and nonce unchanged',patch_sha256=hashlib.sha256(patch).hexdigest(),source_sha256={p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((dest/'src/point_add').rglob('*'))if p.is_file()})
(root/'candidate-control-fold-v7-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
print(json.dumps(manifest,indent=2))
