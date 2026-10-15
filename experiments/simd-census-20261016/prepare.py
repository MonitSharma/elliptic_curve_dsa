from pathlib import Path
import shutil
root=Path(__file__).resolve().parent
tool=root/'tool';(tool/'src').mkdir(parents=True,exist_ok=True)
old=root.parent/'zero-mr-20261016/tool'
for name in ['Cargo.toml','Cargo.lock','simd8wide.h']:shutil.copyfile(old/name,tool/name)
census=root.parent/'failure-census-20261015/src/main.rs'
if not census.exists():census=root.parent/'failure-census-20261015/census/src/main.rs'
(tool/'src/prefix.rs').write_text(census.read_text().split('fn main() {')[0])
for name in ['fast_sim_wide.rs','fast_curve_c.rs']:
 shutil.copyfile(root.parent/'prefilter-20261015/tool/src'/name,tool/'src'/name)
kernel=(root.parent/'prefilter-20261015/simd8wide.c').read_text()
kernel=kernel.replace('size_t *used){','size_t *used,uint64_t *toffoli){',1)
kernel=kernel.replace('V x,y,d,w;','''V x,y,d,w;
  if(o.k==13||o.k==14){uint64_t words[8];st(words,0,c);for(unsigned j=0;j<8;j++)toffoli[j]+=(uint64_t)__builtin_popcountll(words[j]);}
''',1)
(tool/'simd8count.c').write_text(kernel)
header=(tool/'simd8wide.h').read_text();assert header.count('size_t,size_t *);')==1
(tool/'simd8wide.h').write_text(header.replace('size_t,size_t *);','size_t,size_t *,uint64_t *);'))
shutil.copyfile(root/'main.rs',tool/'src/main.rs')
shutil.copyfile(root/'build.rs',tool/'build.rs')
