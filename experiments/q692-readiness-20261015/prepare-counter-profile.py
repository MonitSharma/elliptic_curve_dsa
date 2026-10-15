"""Make an external counting sink; keep all gate construction/cancellation intact."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
source,library,dest=map(Path,sys.argv[1:4])
tree=dest/'source/point_add'
assert not tree.exists()
shutil.copytree(source/'src/point_add',tree)
p=tree/'builder.rs';s=p.read_text(encoding='utf8')
a=s.index('struct Stream {');z=s.index('\n#[cfg(test)]',a)
s=s[:a]+'''struct Stream { count:u64, kinds:[u64;18] }
'''+s[z:]
a=s.index('impl Stream {');z=s.index('\n#[derive(Clone)]',a)
s=s[:a]+'''impl Stream {
    fn new()->Option<Self>{Some(Self{count:0,kinds:[0;18]})}
    fn at(_path:&std::path::Path)->Self{Self{count:0,kinds:[0;18]}}
    fn push(&mut self,op:&Op){self.count+=1;self.kinds[op.kind as usize]+=1;}
    fn finish(self)->u64{eprintln!("COUNT_SINK {}",serde_json::json!({"physical_ops":self.count,"kinds":self.kinds}));self.count}
}
'''+s[z:]
p.write_text(s,encoding='utf8')
(dest/'src').mkdir(parents=True)
(dest/'src/main.rs').write_text('use quantum_ecc::{circuit,sim,weierstrass_elliptic_curve};\n#[allow(dead_code)]\n#[path='+json.dumps((tree/'mod.rs').as_posix())+']mod point_add;\nfn zstd_level()->i32{3}\nfn main(){point_add::build();}\n',encoding='utf8')
(dest/'Cargo.toml').write_text('[package]\nname="q692_counter"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nquantum_ecc={path='+json.dumps(library.as_posix())+'}\nalloy-primitives="1.5"\nruint="1.12"\nsha3="0.10"\nzstd="0.13"\nserde_json="1"\n',encoding='utf8')
binding=dict(scope='emission diagnostic only, no serialized circuit or benchmark',source=str(source),source_sha256={p.relative_to(source/'src/point_add').as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((source/'src/point_add').rglob('*'))if p.is_file()},counter_builder_sha256=hashlib.sha256((tree/'builder.rs').read_bytes()).hexdigest())
(dest/'source-binding.json').write_text(json.dumps(binding,indent=2)+'\n',encoding='utf8')
