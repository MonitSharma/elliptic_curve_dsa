import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'tool';old=ws/'breakthrough-truth14-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert not t.exists() and (old/'run.exit').read_text().strip()=='0'
assert all(sha(old/'tool'/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in (old/'tool/src/point_add').rglob('*'):
 if p.is_file():q=t/p.relative_to(old/'tool');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
dest=t/'src/point_add/sparse_polynomial';dest.mkdir()
s=(t/'src/point_add/interned_witness.rs').read_text().replace('\r','');s=s.replace('const ATOM_CAP: usize = 32;','const ATOM_CAP: usize = 32;\nconst DEGREE_CAP: usize = 32;')
s=s.replace('Clone, PartialEq, Eq, Hash','Clone, PartialEq, Eq, PartialOrd, Ord, Hash').replace('atoms: Vec<u64>','atoms: Vec<Vec<u64>>').replace('atoms: vec![id]','atoms: vec![vec![id]]').replace('atoms.push(a.atoms[i]);','atoms.push(a.atoms[i].clone());').replace('atoms.push(b.atoms[j]);','atoms.push(b.atoms[j].clone());').replace('products: std::collections::HashMap<(Vec<u64>,Vec<u64>),u64>','products: std::collections::HashMap<(bool,Affine,Affine),u64>')
s=s.replace('self.fresh()\n        } else {','self.opaque(false,a,b)\n        } else {',1)
start=s.index('    fn and(&mut self, a: &Affine, b: &Affine) -> Affine {');end=s.index('    fn ccx_rewrite',start)
s=s[:start]+'''    fn opaque(&mut self, product:bool, a:&Affine,b:&Affine)->Affine {
        let (left,right)=if a<=b{(a.clone(),b.clone())}else{(b.clone(),a.clone())};
        let key=(product,left,right);
        let id=if let Some(&id)=self.products.get(&key){id}else{
            if self.products.len()>=PRODUCT_CAP{self.products.clear();}
            let id=self.next_atom;self.next_atom=self.next_atom.checked_add(1).unwrap();self.products.insert(key,id);id
        };Affine{constant:false,atoms:vec![vec![id]]}
    }
    fn and(&mut self,a:&Affine,b:&Affine)->Affine {
        if a.is_zero()||b.is_zero()||a.complements(b){return Affine::constant(false);}
        if a.is_one(){return b.clone();}if b.is_one()||a==b{return a.clone();}
        let mut terms=std::collections::BTreeSet::new();
        let mut toggle=|m:Vec<u64>|{if !terms.insert(m.clone()){terms.remove(&m);}};
        if a.constant{for m in &b.atoms{toggle(m.clone());}}
        if b.constant{for m in &a.atoms{toggle(m.clone());}}
        for x in &a.atoms{for y in &b.atoms{
            let mut m=x.clone();m.extend_from_slice(y);m.sort_unstable();m.dedup();
            if m.len()>DEGREE_CAP{return self.opaque(true,a,b);}toggle(m);
        }}
        if terms.len()>ATOM_CAP{return self.opaque(true,a,b);}
        Affine{constant:a.constant&&b.constant,atoms:terms.into_iter().collect()}
    }

'''+s[end:]
s+='\n#[cfg(test)]#[path="tests.rs"]mod tests;\n#[cfg(test)]#[path="stream_audit.rs"]mod stream_audit;\n';(dest/'mod.rs').write_bytes(s.encode())
v=(old/'vector_tests.rs').read_text().replace('\r','');v=v[v.index('#[test]fn rewritten_random_guarded'):];v='use super::*;\n'+v;v=v.replace('truth14-random-circuits-v1','sparse-polynomial-random-circuits-v1').replace('simplify_classical(simplify_products(ops.clone()))','witnesses(simplify(ops.clone()))');v+='\n'+(r/'algebra_tests.rs').read_text();(dest/'tests.rs').write_bytes(v.encode())
(dest/'stream_audit.rs').write_bytes((r/'stream_audit.rs').read_bytes());p=t/'src/point_add/mod.rs';p.write_bytes(p.read_bytes()+b'\nmod sparse_polynomial;\n')
subprocess.run(['cp','-a','--reflink=auto',str(old/'tool/target'),str(t/'target')],check=True);assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in (t/'src/point_add').rglob('*')if p.is_file()},'input_stream':str(old/'optimized-classical14.ops.bin'),'input_stream_sha256':'bc6fec885e7ebfdad405dddc86519d053d6398aa7b2be1c7a2459d8128444a39','scope':'Exact sparse Boolean-ring proof with at most32 monomials of degree32, immutable keyed opaque overflow and no recycled atom IDs. Proofs computed from original stream state. Only proven CCX-to-X/CX/drop and live product witnesses; no new scratch, phase, reset or measurement. Native scalar and guarded circuit controls precede frozen stream audit. No final gate or resource result.'},indent=2)+'\n')
