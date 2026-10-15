from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parent;up=root.parent/'toffoli';base='5a7c390233c72133df9b591c92e43422c5892142'
for cap in [1792,2048]:
 tree=root/f'cap{cap}';assert not tree.exists()
 subprocess.run(['git','-C',str(up),'worktree','add','--detach',str(tree),base],check=True)
 p=tree/'src/point_add/leapfrog.rs';s=p.read_text();old='("HEO_PIN_PP_WALK_MAX_QUBITS", "1536"),';assert s.count(old)==1
 p.write_text(s.replace(old,f'("HEO_PIN_PP_WALK_MAX_QUBITS", "{cap}"),'))
 patch=subprocess.check_output(['git','-C',str(tree),'diff','HEAD']);(root/f'cap{cap}.patch').write_bytes(patch)
 protected={}
 for rel in subprocess.check_output(['git','-C',str(tree),'ls-files'],text=True).splitlines():
  if rel.startswith('src/point_add/'):continue
  data=(tree/rel).read_bytes();assert data==subprocess.check_output(['git','-C',str(tree),'show','HEAD:'+rel]),rel
  protected[rel]=hashlib.sha256(data).hexdigest()
 (root/f'cap{cap}-protected.json').write_text(json.dumps(protected,indent=2)+'\n')
(root/'DECLARATION.json').write_text(json.dumps({'base':base,'caps':[1792,2048],'original_cap':1536,'objective':'independent minimum Toffolis; width is free','predicted_effect':'possibly fewer carry recomputations; may already saturate at1536','failure_policy':'no weakening arithmetic/cuts; fresh paired failure rate <=parent and18; dirty0','census_label':'wider-cap-fixed-20261016','batches_each':4096,'shots_each':262144,'nonce_search_performed':False},indent=2)+'\n')
