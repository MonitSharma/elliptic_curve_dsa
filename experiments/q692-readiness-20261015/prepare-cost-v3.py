"""Replace quadratic multi-control increments with exact dirty modular arithmetic."""
from pathlib import Path
import hashlib,json,subprocess,sys
root=Path(sys.argv[1]);v1=root/'candidate-control-fold-v1';dest=root/'candidate-control-fold-v3'
assert not dest.exists()
subprocess.run(['git','clone','--shared','--no-hardlinks',str(v1),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'apply',str(root/'candidate-control-fold-v1.patch')],check=True)
p=dest/'src/point_add/midg.rs';s=p.read_text(encoding='utf8')
a=s.index('fn inc_with_controls(');z=s.index('\n}\n',a)+2
s=s[:a]+'''fn inc_with_controls(b: &mut B, bits: &[QubitId], ctl: &[(QubitId, bool)], dirty: &[QubitId]) {
    if bits.is_empty() {return;}
    let m=ctl.len();
    let prefix_cost:usize=(0..bits.len()).map(|i|match m+i{0|1=>0,2=>1,k=>4*(k-2)}).sum();
    let linear_cost=4*(m+bits.len()-1)+4*m.saturating_sub(1);
    if prefix_cost<=linear_cost {
        for i in (0..bits.len()).rev() {
            let mut lits=ctl.to_vec();
            lits.extend(bits[..i].iter().copied().map(|q|(q,false)));
            mc_xor(b,&lits,bits[i],&[],dirty);
        }
        return;
    }
    let low:Vec<QubitId>=ctl.iter().map(|&(q,_)|q).collect();
    let mut combined=low.clone();combined.extend_from_slice(bits);
    let mut ids=std::collections::HashSet::new();
    for q in &combined {assert!(ids.insert(q.0),"increment controls/targets must be distinct");}
    let borrowed:Vec<QubitId>=dirty.iter().copied().filter(|q|!ids.contains(&q.0)).collect();
    assert!(borrowed.len()>=combined.len());
    // Adding one to [literal controls | target] carries into the target
    // exactly when every normalized control is one. Subtracting one only
    // from the low control register restores it modulo 2^m. Both dirty
    // adders restore all passengers and contain no phase/measurement gates.
    for &(q,negative) in ctl {if negative {b.x(q);}}
    super::modp_frogdrop::inc_dirty_free(b,&combined,&borrowed);
    if !low.is_empty() {
        let undo=rec(b,|b|super::modp_frogdrop::inc_dirty_free(b,&low,&borrowed));
        b.play(&undo,true);
    }
    for &(q,negative) in ctl {if negative {b.x(q);}}
}'''+s[z:]
p.write_text(s,encoding='utf8',newline='\n')
patch=subprocess.check_output(['git','-C',str(dest),'diff','HEAD','--','src/point_add/'])
(root/'candidate-control-fold-v3.patch').write_bytes(patch)
manifest=dict(candidate=str(dest),base_revision=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip(),scope='joint unclipped predicate plus exact linear controlled increment; no precision/domain change',patch_sha256=hashlib.sha256(patch).hexdigest(),source_sha256={p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((dest/'src/point_add').rglob('*'))if p.is_file()})
(root/'candidate-control-fold-v3-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
print(json.dumps(manifest,indent=2))
