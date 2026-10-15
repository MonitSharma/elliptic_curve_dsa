"""Port the same predetermined four-stage exact pipeline to our public T record."""
import hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent;tree=root/'wide-candidate-final';assert not tree.exists()
base=subprocess.check_output(['git','-C',str(root.parent/'toffoli'),'rev-parse','5a7c3902'],text=True).strip()
subprocess.run(['git','-C',str(root.parent/'toffoli'),'worktree','add','--detach',str(tree),base],check=True)
dest=tree/'src/point_add';new=[];calls=[];mods=[]
for p in sorted((root/'candidate-final/src/point_add').glob('exact_product_stage*.rs')):
    (dest/p.name).write_bytes(p.read_bytes());new.append('src/point_add/'+p.name);mods.append('mod '+p.stem+';')
assert len(new)==8
for i in range(1,5):calls.append(f'    ops = exact_product_stage{i}_cache::optimize(ops);')
p=dest/'mod.rs';s=p.read_text();needle='    let nonce: u64 = required_env("TAIL_NONCE");';assert s.count(needle)==1
s=s.replace(needle,'\n'.join(calls)+'\n'+needle);s+='\n'+'\n'.join(mods)+'\n';p.write_text(s)
subprocess.run(['git','-C',str(tree),'add','--intent-to-add',*new],check=True)
patch=subprocess.check_output(['git','-C',str(tree),'diff','--','src/point_add']);(root/'wide-candidate-final.patch').write_bytes(patch)
freeze=json.loads((root/'FREEZE.json').read_text());freeze.update(base_revision=base,candidate='wide-candidate-final',external_stream_sha256=hashlib.sha256((root/'wide-chain-retained.bin').read_bytes()).hexdigest(),fixed_paired_saving_t=23.03515625,source_patch_sha256=hashlib.sha256(patch).hexdigest(),objective='independent minimum executed Toffolis')
(root/'WIDE_FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n')
print(subprocess.check_output(['git','-C',str(tree),'diff','--stat'],text=True))
