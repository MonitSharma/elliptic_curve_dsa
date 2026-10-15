"""External cache-retention experiment; candidate and protected sources stay untouched."""
from pathlib import Path
import subprocess,hashlib,json
root=Path(__file__).resolve().parent;old=root.parent/'toffoli-readiness-20261015';dest=root/'analyzer';assert not dest.exists();(dest/'src').mkdir(parents=True)
base=old/'candidate-wide-v1/src/point_add'
prefix=(old/'wide-replay/crate/src/main.rs').read_text().split('// Independent reconstruction')[0]
builder=(root.parent/'overnight-20261014/product-b3-baseline/src/bin/build_circuit.rs').read_text()
writer=builder[builder.index('fn zstd_level()'):builder.index('fn main()')]
main='''
use quantum_ecc::{circuit,sim};
use std::{path::Path,io::BufWriter,fs};
const DEFAULT_ZSTD_LEVEL:i32=3;
mod interned_witness;
mod lazy_cache;
fn main(){
    let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),3);
    let ops=load_ops(&args[1]).unwrap();
    println!("CACHE_SCOPE external_exact_rewrite=true score=NONE atom_cap={} product_cap={}",std::env::var("CACHE_ATOM_CAP").unwrap_or("32".into()),std::env::var("CACHE_PRODUCT_CAP").unwrap_or("200000".into()));
    let revised=lazy_cache::optimize(ops);write_ops(&revised,Path::new(&args[2])).unwrap();
}
'''
(dest/'src/main.rs').write_text(prefix+writer+main)
support=(base/'interned_witness.rs').read_text()
for name,default in [('ATOM_CAP',32),('PRODUCT_CAP',200000)]:
    import re
    needle=re.search(r'const '+name+r': usize = [0-9_]+;',support).group(0)
    func=name.lower()
    support=support.replace(needle,f'fn {func}()->usize {{ static V:std::sync::OnceLock<usize>=std::sync::OnceLock::new(); *V.get_or_init(||std::env::var("CACHE_{name}").ok().map(|s|s.parse().unwrap()).unwrap_or({default})) }}')
    support=support.replace('> '+name,'> '+func+'()').replace('>='+name,'>='+func+'()')
(dest/'src/interned_witness.rs').write_text(support)
(dest/'src/lazy_cache.rs').write_bytes((base/'lazy_cache.rs').read_bytes())
(dest/'Cargo.toml').write_bytes((old/'wide-replay/crate/Cargo.toml').read_bytes())
(dest/'Cargo.lock').write_bytes((old/'wide-replay/crate/Cargo.lock').read_bytes())
(root/'manifest.json').write_text(json.dumps({'status':'prepared-external-diagnostic','qualified_score':None,'hypothesis':'Retaining more immutable symbolic expressions may reveal additional exact repeated AND products. Caps affect proof discovery, not circuit arithmetic.','source_revision':subprocess.check_output(['git','-C',str(old/'candidate-wide-v1'),'rev-parse','HEAD'],text=True).strip(),
    'source_sha256':{str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.rglob('*') if p.is_file()},'source_parent':str(base)},indent=2)+'\n')
