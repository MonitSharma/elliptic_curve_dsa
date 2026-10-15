"""Freeze the predetermined four-stage exact product cache as point-addition source."""
import hashlib,json,re,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent;tree=root/'candidate-final'
assert not tree.exists()
base='4b2ec52fc55da796aa8f5ef851290297e8706424'
subprocess.run(['git','-C',str(root.parent/'toffoli'),'worktree','add','--detach',str(tree),base],check=True)
dest=tree/'src/point_add';new=[];calls=[];mods=[]
stages=[('interned_anf_retained.rs','lazy_cache_retained.rs','interned_anf_retained',128),('interned_witness.rs','lazy_cache_anf.rs','interned_anf',128),('interned_anf.rs','lazy_cache_anf.rs','interned_anf',512),('interned_anf_retained.rs','lazy_cache_retained.rs','interned_anf_retained',512)]
for i,(support_file,cache_file,old_name,cap) in enumerate(stages,1):
    support_name=f'exact_product_stage{i}_support';cache_name=f'exact_product_stage{i}_cache'
    support=(root/'analyzer/src'/support_file).read_text()
    support=re.sub(r'^fn atom_cap\(\).*$',f'fn atom_cap()->usize {{{cap}}}',support,flags=re.M)
    support=re.sub(r'^fn product_cap\(\).*$','fn product_cap()->usize {1000000}',support,flags=re.M)
    support=support.replace('std::env::var("ANF_PAIR_CAP").ok().and_then(|s|s.parse().ok()).unwrap_or(64)','64')
    cache=(root/'analyzer/src'/cache_file).read_text().replace(f'super::{old_name}::Support',f'super::{support_name}::Support')
    cache=cache.replace('let split=std::env::var("CACHE_SPLIT").ok().map_or(false,|v|v=="1");','let split=true;')
    cache=cache.replace('if std::env::var("CACHE_SEMANTIC_END").ok().map_or(false,|v|v=="1")','if false')
    cache=cache.replace('let rank=std::env::var("CACHE_RANK").unwrap_or("start".into());','let rank="density".to_string();')
    assert 'std::env::' not in support and 'std::env::' not in cache
    for name,text in [(support_name,support),(cache_name,cache)]:
        (dest/(name+'.rs')).write_text(text);new.append('src/point_add/'+name+'.rs');mods.append('mod '+name+';')
    calls.append('    ops = '+cache_name+'::optimize(ops);')
p=dest/'mod.rs';s=p.read_text();needle='    let nonce: u64 = required_env("TAIL_NONCE");';assert s.count(needle)==1
s=s.replace(needle,'\n'.join(calls)+'\n'+needle);s+='\n'+'\n'.join(mods)+'\n';p.write_text(s)
subprocess.run(['git','-C',str(tree),'add','--intent-to-add',*new],check=True)
patch=subprocess.check_output(['git','-C',str(tree),'diff','--','src/point_add']);(root/'candidate-final.patch').write_bytes(patch)
frozen={'base_revision':base,'candidate':'candidate-final','stages':[dict(support=s[0],cap=s[3],product_cap=1000000,pair_cap=64,rank='density',split=True) for s in stages],'scope':'exact zero-width semantic rewrites; inherited failures retained','external_stream_sha256':hashlib.sha256((root/'chain-retained.bin').read_bytes()).hexdigest(),'fixed_paired_saving_t':14.48828125,'fixed_packets':2,'shots_per_fixed_packet':256,'nonce_search_performed':False,'source_patch_sha256':hashlib.sha256(patch).hexdigest()}
(root/'FREEZE.json').write_text(json.dumps(frozen,indent=2)+'\n')
print(subprocess.check_output(['git','-C',str(tree),'diff','--stat'],text=True))
