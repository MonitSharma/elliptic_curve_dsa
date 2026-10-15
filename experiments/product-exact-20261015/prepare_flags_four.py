from pathlib import Path
import shutil
root=Path(__file__).resolve().parent
dest=root/'flags-four-tool'
shutil.copytree(root/'flags-tool',dest,ignore=shutil.ignore_patterns('target'),dirs_exist_ok=True)
source=(dest/'src/lazy_cache_anf.rs').read_text().replace('super::interned_anf::Support','super::interned_witness::Support')
(dest/'src/lazy_cache_affine.rs').write_text(source)
path=dest/'src/main.rs';text=path.read_text()
text=text.replace('mod lazy_cache_anf;','mod lazy_cache_anf;\nmod lazy_cache_affine;')
text=text.replace('"cache-anf"=>lazy_cache_anf::optimize(ops),','"cache-anf"=>lazy_cache_anf::optimize(ops),\n        "cache-affine"=>lazy_cache_affine::optimize(ops),')
path.write_text(text)
