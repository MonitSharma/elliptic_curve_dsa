"""Factor a virtual size predicate once per rotation using the returned SX0 flag."""
from pathlib import Path
import hashlib,json,subprocess,sys
root=Path(sys.argv[1]);v5=root/'candidate-control-fold-v5';dest=root/'candidate-control-fold-v6'
assert not dest.exists()
subprocess.run(['git','clone','--shared','--no-hardlinks',str(v5),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'apply',str(root/'candidate-control-fold-v5.patch')],check=True)
p=dest/'src/point_add/midg.rs';s=p.read_text(encoding='utf8')
calls=[('care_borrowed_sz(b,&ring,&sc.sz,&fd.sy,&dest_r,true,&dirty)','care_borrowed_sz_flag(b,&ring,&sc.sz,&fd.sy,&dest_r,true,&dirty,sx[0])'),('care_borrowed_sz(b,&ring,&sc.sz,&fd.sy,&dest,true,&dirty)','care_borrowed_sz_flag(b,&ring,&sc.sz,&fd.sy,&dest,true,&dirty,sx[0])')]
for old,new in calls:assert s.count(old)==1;s=s.replace(old,new)
a=s.index('pub(crate) fn care_borrowed_sz(');brace=s.index('{',a);end=s.index('\n}\n',brace)+2
helper=s[a:end].replace('fn care_borrowed_sz(','fn care_borrowed_sz_flag(').replace('inverse:bool,dirty:&[QubitId])->Vec<G>','inverse:bool,dirty:&[QubitId],flag:QubitId)->Vec<G>')
needle='    assert!(sz.len()>=8);';assert helper.count(needle)==1
helper=helper.replace(needle,'''    assert!(!v.contains(&flag)&&!sz.contains(&flag)&&!sy.contains(&flag)&&!dirty.contains(&flag));
    assert!(sz.len()>=8);''')
needle='            virtual_crot_care(b,v,r,&support,&controls,dirty);';assert helper.count(needle)==1
helper=helper.replace(needle,'''            if controls.len()>1 {
                // The cubes are disjoint. Compute their union once in SX0,
                // rotate under that one control, then restore SX0. SZ/SY
                // and the dirty passengers are unchanged by the rotation.
                let select=rec(b,|b|for literals in &controls{mc_xor(b,literals,flag,&[],dirty);});
                b.play(&select,false);
                virtual_crot_care(b,v,r,&support,&[vec![(flag,false)]],dirty);
                b.play(&select,true);
            } else {virtual_crot_care(b,v,r,&support,&controls,dirty);}''')
s+='\n\n'+helper+'\n'
p.write_text(s,encoding='utf8',newline='\n')
patch=subprocess.check_output(['git','-C',str(dest),'diff','HEAD','--','src/point_add/'])
(root/'candidate-control-fold-v6.patch').write_bytes(patch)
manifest=dict(candidate=str(dest),base_revision=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip(),scope='v5 plus exact disjoint virtual-size predicate factorization in returned SX0; no precision/domain change',patch_sha256=hashlib.sha256(patch).hexdigest(),source_sha256={p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((dest/'src/point_add').rglob('*'))if p.is_file()})
(root/'candidate-control-fold-v6-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
print(json.dumps(manifest,indent=2))
