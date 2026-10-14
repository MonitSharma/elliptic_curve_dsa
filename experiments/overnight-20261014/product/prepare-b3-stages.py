"""Gate-inert B3 stage dumps using exact protected serializer copied read-only."""
from pathlib import Path
import hashlib, sys

base, output, evidence = map(Path, sys.argv[1:4])
source = (base/'src/bin/build_circuit.rs').read_text()
serializer = source[source.index('const MAGIC:'):source.index('fn main()')]
module = '''use crate::circuit::{Op,OperationType,analyze_ops};
use std::fs::{self,File};
use std::io::{BufWriter,Write};
use std::path::Path;
'''+serializer+'''
pub(super) fn save(ops:&[Op],label:&str){
 let directory=Path::new(DIRECTORY);let path=directory.join(format!("{label}.bin"));
 write_ops(ops,&path).expect("source-bound diagnostic stage serialization");
 let(nq,nb,_,_)=analyze_ops(ops.iter());let mr=ops.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).count();
 eprintln!("PRODUCT_B3_STAGE label={label} ops={} nq={nq} nb={nb} measurements={mr} path={} score=NONE",ops.len(),path.display());
}
'''
module = 'const DIRECTORY:&str="'+str(evidence.resolve()).replace('\\','/')+'";\n'+module
mod = (base/'src/point_add/mod.rs').read_text()
needle = '    ops = square_guard::run(ops);\n    ops = linear_restore::run(ops);'
assert mod.count(needle) == 1
mod = mod.replace(needle, '''    product_b3_stage_observer::save(&ops,"before-square-guard");
    ops = square_guard::run(ops);
    product_b3_stage_observer::save(&ops,"after-square-guard");
    ops = linear_restore::run(ops);
    product_b3_stage_observer::save(&ops,"after-linear-restore");''')
needle = '    ops = apply_tail_nonce(ops, nonce);\n    ops\n}'
assert mod.count(needle) == 1
mod = mod.replace(needle,'    ops = apply_tail_nonce(ops, nonce);\n    product_b3_stage_observer::save(&ops,"final");\n    ops\n}')
mod += '\nmod product_b3_stage_observer;\n'
output.mkdir(parents=True,exist_ok=True)
for name,text in [('mod.rs',mod),('product_b3_stage_observer.rs',module)]:
    (output/name).write_text(text,newline='\n')
    print(name+' '+hashlib.sha256((output/name).read_bytes()).hexdigest())
print('protected_serializer_sha256='+hashlib.sha256(serializer.encode()).hexdigest())
