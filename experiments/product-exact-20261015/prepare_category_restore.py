"""Restore every inherited deletion; retain all original anchor checks."""
import hashlib,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent
family=sys.argv[1] if len(sys.argv)>1 else 'deletions'
assert family in ['deletions','reductions']
tree=root/f'candidate-product-restore-{family}'
assert not tree.exists()
base='4b2ec52fc55da796aa8f5ef851290297e8706424'
subprocess.run(['git','-C',str(root.parent/'toffoli'),'worktree','add','--detach',str(tree),base],check=True)
relative='src/point_add/census_anchored.rs'
path=tree/relative
text=path.read_text()
old='    super::census_cut::run_rows(ops,mapped)'
assert text.count(old)==1
new='''    // Restore one entire inherited structural family, selected before any
    // measurement. Every original source neighbourhood was verified above.
    // The depth-weighted figures below are static proxies, not scored means.
    let families:HashMap<usize,bool>=mapped.iter().map(|(i,f)| {
        assert_ne!(f[0], "B", "family restoration expects single-gate rows");
        (*i,f[6]=="del")
    }).collect();
    let (mut depth,mut deleted,mut reduced)=(0i32,0.0f64,0.0f64);
    for (i,o) in ops.iter().enumerate() {
        match o.kind {
            crate::circuit::OperationType::PushCondition => depth+=1,
            crate::circuit::OperationType::PopCondition => depth-=1,
            _ => {}
        }
        if let Some(is_del)=families.get(&i) {
            let weight=0.5f64.powi(depth+(o.c_condition!=crate::circuit::NO_BIT) as i32);
            if *is_del {deleted+=weight;} else {reduced+=weight;}
        }
    }
    let old_len=mapped.len();
    mapped.retain(|(_,f)|SELECT_RETAIN);
    eprintln!("RESTORE_CATEGORY family=FAMILY restored_rows={} retained_rows={} deletion_static_proxy={} reduction_static_proxy={}",old_len-mapped.len(),mapped.len(),deleted,reduced);
    super::census_cut::run_rows(ops,mapped)'''
new=new.replace('SELECT_RETAIN','f[6]!="del"' if family=='deletions' else 'f[6]=="del"').replace('FAMILY',f'all_{family}')
path.write_text(text.replace(old,new))
patch=subprocess.check_output(['git','-C',str(tree),'diff','--',relative])
(root/f'candidate-product-restore-{family}.patch').write_bytes(patch)
plan={'base_revision':base,'candidate':tree.name,'selection':f'Restore ALL inherited census_cut {family}, after every original content anchor validates; preserve the other complete category and every upstream table/cut. No packet-based row selection.','patch_sha256':hashlib.sha256(patch).hexdigest(),'phase':'construction and whole-category fresh cost/failure measurement; no nonce search','nonce_search_performed':False,'score':None}
(root/('CATEGORY_RESTORE_DECLARATION.json' if family=='deletions' else 'REDUCTION_RESTORE_DECLARATION.json')).write_text(json.dumps(plan,indent=2)+'\n')
print(patch.decode())
