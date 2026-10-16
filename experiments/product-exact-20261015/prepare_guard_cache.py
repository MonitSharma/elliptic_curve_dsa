import shutil
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'guard-cache-tool'
assert not d.exists()
shutil.copytree(r/'flags-four-tool',d,ignore=shutil.ignore_patterns('target'))
shutil.copy2(r/'guard_bdd.rs',d/'src/guard_bdd.rs')
p=d/'src/main.rs';p.write_text(p.read_text()+'\nmod guard_bdd;\n')
p=d/'src/lazy_cache_retained.rs';s=p.read_text()
s=s.replace('let mut weights=vec![0f64;ops.len()];','let mut guards=super::guard_bdd::analyze(&ops);')
line='        if o.kind==K::CCX {weights[i]=0.5f64.powi(depth as i32+if o.c_condition==NO_BIT{0}else{1});}'
assert s.count(line)==1;s=s.replace(line,'')
s=s.replace('weights[*i]','guards.weights[*i]')
for uses in ['us','uses']:
    old=f'let union_proxy=1.0-{uses}.iter().map(|i|1.0-guards.weights[*i]).product::<f64>();'
    assert s.count(old)==1
    s=s.replace(old,f'let union_proxy=guards.union_probability(&{uses});\n                if weight_sum-union_proxy<=1e-12 {{continue;}}')
p.write_text(s)
print('Guard-union proposal ranking/filtering only; original exact cache renderer and retained ANF support unchanged.')
