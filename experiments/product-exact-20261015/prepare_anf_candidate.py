"""Source-native polynomial cache, fixed structural constants only."""
import re,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent;tree=root/'candidate-anf512'
assert not tree.exists()
subprocess.run(['git','-C',str(root.parent/'toffoli'),'worktree','add','--detach',str(tree),'4b2ec52fc55da796aa8f5ef851290297e8706424'],check=True)
dest=tree/'src/point_add'
cache=(root/'analyzer/src/lazy_cache_anf.rs').read_text().replace('super::interned_anf::Support','super::exact_polynomial_support::Support')
cache=cache.replace('let split=std::env::var("CACHE_SPLIT").ok().map_or(false,|v|v=="1");','let split=true;')
cache=cache.replace('if std::env::var("CACHE_SEMANTIC_END").ok().map_or(false,|v|v=="1")','if false')
cache=cache.replace('let rank=std::env::var("CACHE_RANK").unwrap_or("start".into());','let rank="density".to_string();')
support=(root/'analyzer/src/interned_anf.rs').read_text()
support=re.sub(r'^fn atom_cap\(\).*$', 'fn atom_cap()->usize {512}',support,flags=re.M)
support=re.sub(r'^fn product_cap\(\).*$', 'fn product_cap()->usize {1000000}',support,flags=re.M)
support=support.replace('std::env::var("ANF_PAIR_CAP").ok().and_then(|s|s.parse().ok()).unwrap_or(64)','64')
(dest/'exact_polynomial_cache.rs').write_text(cache)
(dest/'exact_polynomial_support.rs').write_text(support)
p=dest/'mod.rs';s=p.read_text();needle='    let nonce: u64 = required_env("TAIL_NONCE");';assert s.count(needle)==1
s=s.replace(needle,'    ops = exact_polynomial_cache::optimize(ops);\n'+needle)
s+='\nmod exact_polynomial_cache;\nmod exact_polynomial_support;\n';p.write_text(s)
subprocess.run(['git','-C',str(tree),'add','--intent-to-add','src/point_add/exact_polynomial_cache.rs','src/point_add/exact_polynomial_support.rs'],check=True)
(root/'candidate-anf512.patch').write_bytes(subprocess.check_output(['git','-C',str(tree),'diff','--','src/point_add']))
print(subprocess.check_output(['git','-C',str(tree),'diff','--stat'],text=True))
