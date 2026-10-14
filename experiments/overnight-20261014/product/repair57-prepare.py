"""Isolated finite correctness prototype: all forward folds57, reverse unchanged."""
from pathlib import Path
import subprocess,sys
base,output,evidence=map(Path,sys.argv[1:4])
subprocess.run([sys.executable,str(Path(__file__).with_name('prepare-body-boundaries-v2.py')),str(base),str(output),str(evidence)],check=True)
s=(base/'src/point_add/y15_onefold.rs').read_text();needle='    if PAYLOAD_FOLD_PREFIX && !rev && t <= 99 { 57 } else { Y15_WIN }';assert s.count(needle)==1
s=s.replace(needle,'    if !rev { 57 } else { Y15_WIN } // repair57 finite prototype; not a universal field repair')
(output/'y15_onefold.rs').write_text(s,newline='\n')
observer=(output/'product_body_observer.rs').read_text()
needle='pub(super) fn save_raw(ops:&[Op]){';assert observer.count(needle)==1
observer=observer.replace(needle,needle+'product_raw_cost(ops);')
observer+=r'''
fn product_raw_cost(ops:&[Op]){
 use std::collections::BTreeMap;use crate::circuit::{analyze_ops,OperationType as K,NO_BIT};
 let(mut kinds,mut conditioned,mut depth)=(BTreeMap::<String,u64>::new(),BTreeMap::<String,u64>::new(),0usize);
 for op in ops{let key=format!("{:?}",op.kind);*kinds.entry(key.clone()).or_default()+=1;if depth>0||op.c_condition!=NO_BIT{*conditioned.entry(key).or_default()+=1;}match op.kind{K::PushCondition=>depth+=1,K::PopCondition=>depth-=1,_=>{}}}assert_eq!(depth,0);
 let(nq,nb,_,_)=analyze_ops(ops.iter());let text=format!("{{\"status\":\"COMPLETE_RAW_GENERATED_DIAGNOSTIC\",\"qualified_score\":null,\"ops\":{},\"physical_wire_count\":{nq},\"classical_slots\":{nb},\"kinds\":{kinds:?},\"syntactically_conditioned_kinds\":{conditioned:?}}}",ops.len());
 std::fs::write(std::path::Path::new(DIRECTORY).join("raw-cost.json"),text+"\n").unwrap();eprintln!("REPAIR57_RAW_COST ops={} nq={nq} nb={nb} score=NONE complete_scored_cost=NONE",ops.len());
}
'''
(output/'product_body_observer.rs').write_text(observer,newline='\n')
