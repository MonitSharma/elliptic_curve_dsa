import hashlib,json,re,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent
frozen=json.loads((root/'WIDE_COMPOUND_FREEZE.json').read_text())
tree=root/frozen['candidate'];assert not tree.exists()
subprocess.run(['git','-C',str(root.parent/'toffoli'),'worktree','add','--detach',str(tree),frozen['base_revision']],check=True)
dest=tree/'src/point_add';new=[];calls=[];mods=[];modules={};stage_modules=[]
for i,stage in enumerate(frozen['stages'],1):
    family=stage['family'];cap=stage['atom_cap'];pairs=stage['pair_cap'];extra=stage['extra_zero_slots_offered']
    key=(family,cap,pairs,extra)
    if key in modules:
        first=modules[key];calls.append(f'    ops = exact_wide_stage{first}_cache::optimize(ops);');stage_modules.append(first);continue
    modules[key]=i;stage_modules.append(i)
    if family in ['retained','scratch','unfold']:
        support_file='interned_anf_retained.rs';cache_file='lazy_cache_retained.rs';old='interned_anf_retained'
        tool={'retained':'analyzer','scratch':'scratch-tool','unfold':'unfold-tool'}[family]
    elif family=='affine':support_file='interned_witness.rs';cache_file='lazy_cache_anf.rs';old='interned_anf';tool='analyzer'
    else:support_file='interned_anf.rs';cache_file='lazy_cache_anf.rs';old='interned_anf';tool='analyzer'
    support_name=f'exact_wide_stage{i}_support';cache_name=f'exact_wide_stage{i}_cache'
    support=(root/tool/'src'/support_file).read_text()
    support=re.sub(r'^fn atom_cap\(\).*$',f'fn atom_cap()->usize {{{cap}}}',support,flags=re.M)
    support=re.sub(r'^fn product_cap\(\).*$','fn product_cap()->usize {1000000}',support,flags=re.M)
    support=support.replace('std::env::var("ANF_PAIR_CAP").ok().and_then(|s|s.parse().ok()).unwrap_or(64)',str(pairs))
    cache=(root/tool/'src'/cache_file).read_text().replace(f'super::{old}::Support',f'super::{support_name}::Support')
    cache=cache.replace('let split=std::env::var("CACHE_SPLIT").ok().map_or(false,|v|v=="1");','let split=true;')
    cache=cache.replace('if std::env::var("CACHE_SEMANTIC_END").ok().map_or(false,|v|v=="1")','if false')
    cache=cache.replace('let rank=std::env::var("CACHE_RANK").unwrap_or("start".into());','let rank="density".to_string();')
    cache=cache.replace('std::env::var("CACHE_EXTRA_QUBITS").ok().map_or(0,|s|s.parse().unwrap())',str(extra))
    assert 'std::env::' not in support and 'std::env::' not in cache
    for name,text in [(support_name,support),(cache_name,cache)]:
        (dest/(name+'.rs')).write_text(text);new.append('src/point_add/'+name+'.rs');mods.append('mod '+name+';')
    calls.append('    ops = '+cache_name+'::optimize(ops);')
path=dest/'mod.rs';text=path.read_text();needle='    let nonce: u64 = required_env("TAIL_NONCE");';assert text.count(needle)==1
path.write_text(text.replace(needle,'\n'.join(calls)+'\n'+needle)+'\n'+'\n'.join(mods)+'\n')
subprocess.run(['git','-C',str(tree),'add','--intent-to-add',*new],check=True)
patch=subprocess.check_output(['git','-C',str(tree),'diff','--','src/point_add']);(root/'candidate-wide-compound.patch').write_bytes(patch)
frozen['source_patch_sha256']=hashlib.sha256(patch).hexdigest();frozen['stage_module_first_occurrences']=stage_modules
(root/'WIDE_COMPOUND_SOURCE_FREEZE.json').write_text(json.dumps(frozen,indent=2)+'\n')
print(subprocess.check_output(['git','-C',str(tree),'diff','--stat'],text=True))
