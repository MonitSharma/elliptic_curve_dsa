"""Clean public C95 expected-negative pair, fixed independent input."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
source,template,dest,ev=map(lambda s:Path(s).resolve(),sys.argv[1:5])
assert not subprocess.check_output(['git','-C',str(dest),'status','--porcelain'],text=True).strip()
script=(source.parent/'qubit-add-k32-column-tests.py').read_text();prefix=script[script.index('def states(dx):'):script.index('\n\nselected={}')];ns={'P':2**256-2**32-977};exec(prefix,ns)
dx=int('b99d62d1aa557c0a85f9ea89739eded4eb025ed76459a15b2551efaae60665bd',16);state=ns['states'](dx)[86];assert state['quotient']==22815568
a,z=state['before'],state['after'];case='("shot2379_div2_HT_q25",86,['+','.join('"'+format(v,'x')+'"'for v in a[:3])+'],'+','.join(str(v)for v in a[3:])+',['+','.join('"'+format(v,'x')+'"'for v in z[:3])+'],'+','.join(str(v)for v in z[3:])+')'
text=(template/'src/point_add/tests_midg_k24.rs').read_text();start=text.index('#[test]\nfn qubit_diag2379_full_column_negative_control');test=text[start:]
assert 'Known quotient overflow must be reproduced' in test
test=test.replace('alloc_n(274)','alloc_n(276)').replace('vec![0u64;691]','vec![0u64;693]').replace('run(&forward,691','run(&forward,693').replace('run(&inverse,691','run(&inverse,693').replace('width=691','width=693')
p=dest/'src/point_add/tests_midg_k24.rs';p.write_text(p.read_text()+'\n'+test)
hashes={str(p.relative_to(source/'src/point_add')):hashlib.sha256(p.read_bytes()).hexdigest()for p in (source/'src/point_add').rglob('*')if p.is_file()}
manifest=dict(scope='Expected-negative source-bound cleanC95 primitive pair; not full point equivalence or a score',revision=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip(),source=str(source),source_patch_sha256=hashlib.sha256(subprocess.check_output(['git','-C',str(source),'diff','HEAD','--','src/point_add/'])).hexdigest(),source_sha256=hashes,diagnostic_test_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),dx=hex(dx),column=86,state=state,constructor_width=693)
(ev/'diag2379-base-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
