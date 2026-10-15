import hashlib,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent
name=sys.argv[1];assert name in ['one','two']
tree=root/f'candidate-product-tail-{name}'
assert not tree.exists()
base='4b2ec52fc55da796aa8f5ef851290297e8706424'
subprocess.run(['git','-C',str(root.parent/'toffoli'),'worktree','add','--detach',str(tree),base],check=True)
relative='src/point_add/leapfrog_data/pack_t0hat_tail0_138_steps_k770_lw2.txt'
path=tree/relative;out=[];row=0;changed={}
ticks=[136] if name=='one' else [135,136]
for line in path.read_text().splitlines():
    if not line.strip() or line.startswith('#'):out.append(line);continue
    values=list(map(int,line.split()));assert len(values)==5
    if row in ticks:
        assert values==({135:[10,10,9,8,7],136:[8,8,7,6,5]}[row])
        values=[x+1 for x in values];changed[str(row)]=values
    if row==137:assert values==[6,6,6,6,5]
    out.append(' '.join(map(str,values)));row+=1
assert row==138
path.write_text('\n'.join(out)+'\n')
patch=subprocess.check_output(['git','-C',str(tree),'diff','--',relative]);(root/f'candidate-product-tail-{name}.patch').write_bytes(patch)
metadata={'base_revision':base,'candidate':tree.name,'ticks':ticks,'new_widths':changed,'change':'Increase all five last nonpark row widths by one; keep row count, parity, YP8 anchors, final park and inherited source cuts unchanged. Preserve construction failures; do not bypass source anchors.','patch_sha256':hashlib.sha256(patch).hexdigest(),'label':'product-tail-width-20261016','batches_per_source':4096,'shots_per_source':262144,'nonce_search_performed':False,'score':None}
(root/f'PRODUCT_TAIL_{name.upper()}_DECLARATION.json').write_text(json.dumps(metadata,indent=2)+'\n')
print(patch.decode())
