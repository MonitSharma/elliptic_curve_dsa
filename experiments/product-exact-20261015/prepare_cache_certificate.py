import shutil
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'cache-certificate-tool';assert not d.exists()
shutil.copytree(r/'flags-four-tool',d,ignore=shutil.ignore_patterns('target'))
shutil.copy2(r/'cache_certificate.rs',d/'src/cache_certificate.rs')
p=d/'src/main.rs';s=p.read_text();at=s.index('fn main(){');s=s[:at]+'''mod cache_certificate;
fn main(){
    let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),5,"INPUT OUTPUT LOG FAMILY");
    let left=load_ops(&args[1]).unwrap();let right=load_ops(&args[2]).unwrap();let log=std::fs::read_to_string(&args[3]).unwrap();
    cache_certificate::audit(&left,&right,&log,&args[4]);
}
''';p.write_text(s)
print('Separate lease-certificate verifier; no allocator, proposal generator, ranking, simulation or sampled inputs. Trusted conservative symbolic kernels retained verbatim.')
