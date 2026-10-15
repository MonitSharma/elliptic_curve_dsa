"""Transfer the pre-existing correctness-increasing tail smoothing to4b only."""
import hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent
tree=root/'candidate-product-tail-smooth'
assert not tree.exists()
base='4b2ec52fc55da796aa8f5ef851290297e8706424'
subprocess.run(['git','-C',str(root.parent/'toffoli'),'worktree','add','--detach',str(tree),base],check=True)
relative='src/point_add/leapfrog_data/pack_t0hat_tail0_138_steps_k770_lw2.txt'
path=tree/relative;lines=path.read_text().splitlines();out=[];row=0
for line in lines:
    if not line.strip() or line.startswith('#'):out.append(line);continue
    values=list(map(int,line.split()));assert len(values)==5
    if row==137:
        assert values==[6,6,6,6,5],values;values=[9,9,8,7,6]
    elif row==138:
        assert values==[6,6,6,6,5],values;values=[7,7,6,6,5]
    out.append(' '.join(map(str,values)));row+=1
assert row==140 and out[-1]=='6 6 6 6 5'
path.write_text('\n'.join(out)+'\n')
patch=subprocess.check_output(['git','-C',str(tree),'diff','--',relative])
(root/'candidate-product-tail-smooth.patch').write_bytes(patch)
plan={'base_revision':base,'candidate':tree.name,'change':'Increase tail precision at walk ticks137/138; leave parked rails and all arithmetic cuts unchanged','rows':{'137':[9,9,8,7,6],'138':[7,7,6,6,5]},'patch_sha256':hashlib.sha256(patch).hexdigest(),'label':'product-tail-smooth-20261016','batches_per_source':4096,'shots_per_source':262144,'nonce_search_performed':False,'score':None}
(root/'PRODUCT_SMOOTH_DECLARATION.json').write_text(json.dumps(plan,indent=2)+'\n')
print(patch.decode())
