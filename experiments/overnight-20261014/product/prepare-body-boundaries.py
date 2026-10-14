"""Gate-inert coordinate/scalar boundaries with actual signed T6 wire frame."""
from pathlib import Path
import sys
base,output,evidence=map(Path,sys.argv[1:4])
output.mkdir(parents=True,exist_ok=True)
mod=(base/'src/point_add/mod.rs').read_text()
start=mod.index('    if leapfrog::enabled() {',mod.index('pub(crate) fn build_point_add'))
end=mod.index('        return circ.take_ops();',start)
part=mod[start:end]
def mark(label,r0='None'):
 return '        product_body_observer::mark(circ,"'+label+'",x,y,ox,oy,seams,'+r0+');\n'
needles=[('        circ.set_phase("divide");',mark('coord-y-sub')),
 ('        circ.set_phase("square");',mark('divide-seamed')),
 ('        circ.set_phase("multiply");',mark('sub-square','leapfrog::product_observe_preseed().as_deref()')),
 ('        leapfrog::c35_widen_check();',mark('multiply-seamed')),
 ('        leapfrog::prof_dump();',mark('final-coordinates'))]
for needle,insert in needles:
 assert part.count(needle)==1,needle
 part=part.replace(needle,insert+needle)
needle='        circ.finalize_records();'
assert part.count(needle)==1
part=part.replace(needle,mark('before-finalize-records')+needle+'\n'+mark('after-finalize-records').rstrip())
mod=mod[:start]+part+mod[end:]
needle='    let mut ops = build_point_add();'
assert mod.count(needle)==1
mod=mod.replace(needle,needle+'\n    product_body_observer::save_raw(&ops);')
mod+='\nmod product_body_observer;\n'
(output/'mod.rs').write_text(mod,newline='\n')
builder=(base/'src/point_add/builder.rs').read_text()
needle='    pub fn op_count(&self) -> usize { self.ops.len() }'
assert builder.count(needle)==1
builder=builder.replace(needle,needle+'\n    pub(crate) fn product_observation_ops(&self)->&[Op]{&self.ops}')
(output/'builder.rs').write_text(builder,newline='\n')
leap=(base/'src/point_add/leapfrog.rs').read_text()
assert 'static T6_PRESEED:' in leap
leap+='\npub(crate) fn product_observe_preseed()->Option<Vec<QubitId>>{T6_PRESEED.with(|s|s.borrow().clone())}\n'
(output/'leapfrog.rs').write_text(leap,newline='\n')
protected=(base/'src/bin/build_circuit.rs').read_text()
serializer=protected[protected.index('const MAGIC:'):protected.index('fn main()')]
observer='''use crate::circuit::Op;use super::{Builder,BitId,QubitId};
use std::fs::{self,File,OpenOptions};use std::io::{BufWriter,Write};use std::path::Path;
'''+serializer+'''
pub(super) fn save_raw(ops:&[Op]){write_ops(ops,&Path::new(DIRECTORY).join("raw-body.bin")).unwrap();}
pub(super) fn mark(c:&Builder,label:&str,x:&[QubitId],y:&[QubitId],ox:&[BitId],oy:&[BitId],seams:bool,r0:Option<&[QubitId]>){
 use sha3::{Digest,Sha3_256};let mut h=Sha3_256::new();let ops=c.product_observation_ops();
 for o in ops{h.update((o.kind as u32).to_le_bytes());h.update([0u8;4]);for id in[o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(id.to_le_bytes());}}
 let digest=format!("{:x}",h.finalize());let ids=|qs:&[QubitId]|qs.iter().map(|q|q.0.to_string()).collect::<Vec<_>>().join(",");
 let bits=|bs:&[BitId]|bs.iter().map(|b|b.0.to_string()).collect::<Vec<_>>().join(",");
 let r0=r0.map(ids).unwrap_or_else(||"-".into());let(nq,nb)=c.i13_dims();let offset=super::square::sub_square_offset();
 let path=Path::new(DIRECTORY).join("boundaries.tsv");let mut file=OpenOptions::new().append(true).create(true).open(&path).unwrap();
 writeln!(file,"{label}\\t{}\\t{digest}\\t{nq}\\t{nb}\\t{seams}\\t{offset:#x}\\t{}\\t{}\\t{}\\t{}\\t{r0}",ops.len(),ids(x),ids(y),bits(ox),bits(oy)).unwrap();
 eprintln!("PRODUCT_BODY_BOUNDARY label={label} ops={} prefix_sha3={digest} dims=({nq},{nb}) seams={seams} r0={r0} square_offset={offset:#x} path={} score=NONE",ops.len(),path.display());
}
'''
observer='const DIRECTORY:&str="'+str(evidence.resolve()).replace('\\','/')+'";\n'+observer
(output/'product_body_observer.rs').write_text(observer,newline='\n')
