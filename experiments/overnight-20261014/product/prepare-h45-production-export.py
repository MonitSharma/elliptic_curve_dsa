"""Append an observational exporter to the independently passing exact contexts."""
from pathlib import Path
import hashlib, sys
base, dest, evidence = map(Path, sys.argv[1:4])
dest.mkdir(parents=True,exist_ok=True)
test=(base/'src/point_add/product_h45_actual_context_tests.rs').read_text()
protected=(base/'src/bin/build_circuit.rs').read_text()
serializer=protected[protected.index('const MAGIC:'):protected.index('fn main()')]
serializer=serializer.replace('fn write_ops(', 'pub(super) fn write_ops(')
module='mod product_serialize {\nuse crate::circuit::Op;use std::fs::{self,File};use std::io::{BufWriter,Write};use std::path::Path;\n'+serializer+'}\n'
export='''
#[test]fn product_h45_export_actual_fold_variants(){
 prepare();let directory=std::path::Path::new(DIRECTORY);let mut admitted=0;
 for ctx in CONTEXTS{for on in[false,true]{let(ops,hits)=circuit(ctx,on);if on&&hits!=0{admitted+=1;}let path=directory.join(format!("tick{}-{}.bin",ctx.tick,if on{"new"}else{"old"}));product_serialize::write_ops(&ops,&path).unwrap();eprintln!("PRODUCT_H45_EXPORT tick={} new={} ops={} path={} score=NONE",ctx.tick,on,ops.len(),path.display());}}
 assert_eq!(admitted,104);
}
'''
test += '\nconst DIRECTORY:&str="'+str(evidence.resolve()).replace('\\','/')+'";\n'+module+export
(dest/'product_h45_actual_context_tests.rs').write_text(test,newline='\n')
for name in['y15_onefold.rs','toffoli_carry_cleanup_v1.rs','product_h45_phase_kernel.rs']:
 (dest/name).write_bytes((base/'src/point_add'/name).read_bytes())
 print(name+' '+hashlib.sha256((dest/name).read_bytes()).hexdigest())
