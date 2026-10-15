"""Port the structurally selected 128/density cache; no nonce search or tuning."""
import re, subprocess
from pathlib import Path
root=Path(__file__).resolve().parent
tree=root/'candidate-split128'
assert not tree.exists()
subprocess.run(['git','-C',str(root.parent/'toffoli'),'worktree','add','--detach',str(tree),'4b2ec52fc55da796aa8f5ef851290297e8706424'],check=True)
dest=tree/'src/point_add'
cache=(root/'analyzer/src/lazy_cache.rs').read_text()
cache=cache.replace('super::interned_witness::Support','super::exact_cache_support::Support').replace('super::control_predicates::','super::exact_control_predicates::')
cache=cache.replace('let split=std::env::var("CACHE_SPLIT").ok().map_or(false,|v|v=="1");','let split=true;')
cache=cache.replace('let conditional=std::env::var("CACHE_CONDITIONAL_DONOR").ok().map_or(false,|v|v=="1");','let conditional=false;')
cache=cache.replace('if std::env::var("CACHE_SEMANTIC_END").ok().map_or(false,|v|v=="1")','if false')
cache=cache.replace('let rank=std::env::var("CACHE_RANK").unwrap_or("start".into());','let rank="density".to_string();')
support=(root/'analyzer/src/interned_witness.rs').read_text()
support=re.sub(r'^fn atom_cap\(\).*$', 'fn atom_cap()->usize {128}',support,flags=re.M)
support=re.sub(r'^fn product_cap\(\).*$', 'fn product_cap()->usize {1000000}',support,flags=re.M)
(dest/'exact_cache.rs').write_text(cache)
(dest/'exact_cache_support.rs').write_text(support)
(dest/'exact_control_predicates.rs').write_text((root/'analyzer/src/control_predicates.rs').read_text())
p=dest/'mod.rs';s=p.read_text();needle='    let nonce: u64 = required_env("TAIL_NONCE");'
assert s.count(needle)==1
s=s.replace(needle,'    ops = exact_cache::optimize(ops);\n'+needle)
s+='\nmod exact_cache;\nmod exact_cache_support;\nmod exact_control_predicates;\n'
p.write_text(s)
subprocess.run(['git','-C',str(tree),'add','--intent-to-add','src/point_add/exact_cache.rs','src/point_add/exact_cache_support.rs','src/point_add/exact_control_predicates.rs'],check=True)
patch=subprocess.check_output(['git','-C',str(tree),'diff','--','src/point_add'])
(root/'candidate-split128.patch').write_bytes(patch)
print(subprocess.check_output(['git','-C',str(tree),'diff','--stat'],text=True))
