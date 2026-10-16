import hashlib,json,re,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent
tree=root/'candidate-product-final25';assert not tree.exists()
base='4b2ec52fc55da796aa8f5ef851290297e8706424'
initial=[('retained',128),('affine',128),('anf',512),('retained',512),('retained',128),('retained',512),('retained',1024),('anf',512),('retained',128),('retained',512),('retained',1024)]
cycle=[('retained',128),('retained',512),('retained',1024),('anf',512),('retained',128),('retained',512),('retained',1024)]
stages=initial+cycle*2;assert len(stages)==25
resources=json.loads((root/'product-continuation-20261016/stage-25-resources.jsonl').read_text());assert resources['u16_physical_ids_supported'] and resources['qubits']==1234
packets={}
for family in ['independent','structured']:
    text=(root/f'product-continuation-20261016/stage-25-{family}.log').read_text()
    line=next(line for line in text.splitlines() if line.startswith('DIAGNOSTIC_ONLY '));row=dict(re.findall(r'(\w+)=(\S+)',line));assert row['unequal_batches']=='0';packets[family]=row
subprocess.run(['git','-C',str(root.parent/'toffoli'),'worktree','add','--detach',str(tree),base],check=True)
dest=tree/'src/point_add';new=[];calls=[];mods=[];modules={};stage_modules=[]
for i,(family,cap) in enumerate(stages,1):
    key=(family,cap)
    if key in modules:
        first=modules[key];stage_modules.append(first);calls.append(f'    ops = exact_product_stage{first}_cache::optimize(ops);');continue
    modules[key]=i;stage_modules.append(i)
    support_file={'retained':'interned_anf_retained.rs','affine':'interned_witness.rs','anf':'interned_anf.rs'}[family]
    support_old=support_file.removesuffix('.rs');cache_file={'retained':'lazy_cache_retained.rs','affine':'lazy_cache_affine.rs','anf':'lazy_cache_anf.rs'}[family]
    support_name=f'exact_product_stage{i}_support';cache_name=f'exact_product_stage{i}_cache'
    support=(root/'flags-four-tool/src'/support_file).read_text()
    support=re.sub(r'^fn atom_cap\(\).*$',f'fn atom_cap()->usize {{{cap}}}',support,flags=re.M)
    support=re.sub(r'^fn product_cap\(\).*$','fn product_cap()->usize {1000000}',support,flags=re.M)
    support=support.replace('std::env::var("ANF_PAIR_CAP").ok().and_then(|s|s.parse().ok()).unwrap_or(64)','64')
    cache=(root/'flags-four-tool/src'/cache_file).read_text().replace(f'super::{support_old}::Support',f'super::{support_name}::Support')
    cache=cache.replace('let split=std::env::var("CACHE_SPLIT").ok().map_or(false,|v|v=="1");','let split=true;')
    cache=cache.replace('if std::env::var("CACHE_SEMANTIC_END").ok().map_or(false,|v|v=="1")','if false')
    cache=cache.replace('let rank=std::env::var("CACHE_RANK").unwrap_or("start".into());','let rank="density".to_string();')
    assert 'std::env::' not in support and 'std::env::' not in cache
    for name,text in [(support_name,support),(cache_name,cache)]:
        (dest/(name+'.rs')).write_text(text);new.append('src/point_add/'+name+'.rs');mods.append('mod '+name+';')
    calls.append('    ops = '+cache_name+'::optimize(ops);')
path=dest/'mod.rs';text=path.read_text();needle='    let nonce: u64 = required_env("TAIL_NONCE");';assert text.count(needle)==1
path.write_text(text.replace(needle,'\n'.join(calls)+'\n'+needle)+'\n'+'\n'.join(mods)+'\n')
subprocess.run(['git','-C',str(tree),'add','--intent-to-add',*new],check=True)
patch=subprocess.check_output(['git','-C',str(tree),'diff','--','src/point_add']);(root/'candidate-product-final25.patch').write_bytes(patch)
frozen={'base_revision':base,'candidate':tree.name,'stages':[dict(family=family,atom_cap=cap,product_cap=1000000,pair_cap=64,rank='density',split=True,flags='three per donor; disjoint top-level lifetimes') for family,cap in stages],'stage_module_first_occurrences':stage_modules,'scope':'Exact width-free rewrites; inherited failures retained. Fixed stage count/configuration declared before continuation measurements.','external_stream':'product-continuation-20261016/product-25-retained-1024.bin','external_stream_sha256':hashlib.sha256((root/'product-continuation-20261016/product-25-retained-1024.bin').read_bytes()).hexdigest(),'packets':packets,'diagnostic_rng_protocol':'Original MR words fixed by original-event ordinal; added cache MR words from separate fixed XOF. Counts describe these packets, not universal means.','resources':resources,'nonce_search_performed':False,'source_patch_sha256':hashlib.sha256(patch).hexdigest(),'score':None}
(root/'PRODUCT25_FREEZE.json').write_text(json.dumps(frozen,indent=2)+'\n')
print(subprocess.check_output(['git','-C',str(tree),'diff','--stat'],text=True))
