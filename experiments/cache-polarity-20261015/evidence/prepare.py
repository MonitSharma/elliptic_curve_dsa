"""Exact complemented-control cache experiment; external research crates only."""
from pathlib import Path
import shutil, hashlib, json
root=Path(__file__).resolve().parent
old=root.parent/'cache-retention-20261015/analyzer'
dest=root/'analyzer'
assert not dest.exists()
shutil.copytree(old,dest)
def replace(s,a,b):
    assert s.count(a)==1,(a,s.count(a))
    return s.replace(a,b)
p=dest/'src/interned_witness.rs'
s=p.read_text()+'''
impl Support {
    pub(super) fn normalized_product(&mut self, op:&Op)->((bool,Vec<u64>),(bool,bool)) {
        let mut a=self.qubits[op.q_control1.0 as usize].clone();
        let mut b=self.qubits[op.q_control2.0 as usize].clone();
        let flips=(a.constant,b.constant);a.constant=false;b.constant=false;
        let p=self.and(&a,&b);((p.constant,p.atoms),flips)
    }
}
'''
p.write_text(s)
p=dest/'src/lazy_cache.rs';s=p.read_text()
s=replace(s,'    for (i,o) in ops.iter().enumerate(){\n        if o.kind==K::CCX {groups.entry(symbolic.cache_product(o)).or_default().push(i);}', '''    let mut flips=HashMap::new();
    for (i,o) in ops.iter().enumerate(){
        if o.kind==K::CCX {let (key,f)=symbolic.normalized_product(o);flips.insert(i,f);groups.entry(key).or_default().push(i);}''')
s=replace(s,'render(ops,chosen,nb,width)','render(ops,chosen,nb,width,flips)')
s=replace(s,'nb:u64,nq:usize)->Vec<Op>{','nb:u64,nq:usize,flips:HashMap<usize,(bool,bool)>)->Vec<Op>{')
s=replace(s,'for &i in &w.uses {assert!(uses.insert(i,j).is_none());}', '''for &i in &w.uses {assert!(uses.insert(i,j).is_none());
            let (a,b)=flips[&i];println!("CACHE_POLARITY op={i} ca={} cb={}",u8::from(a),u8::from(b));}''')
s=replace(s,'None,Some(m)));out.push(pop());','''None,Some(m)));
            let (ca,cb)=flips[w.uses.last().unwrap()];
            if ca {out.push(gate(K::Z,None,None,Some(last.q_control2.0),None,Some(m)));}
            if cb {out.push(gate(K::Z,None,None,Some(last.q_control1.0),None,Some(m)));}
            if ca&&cb {out.push(gate(K::Neg,None,None,None,None,Some(m)));}
            out.push(pop());''')
s=replace(s,'            out.push(store(valid,true));out.push(pop());','''            let (ca,cb)=flips[&i];
            linear(&mut out,o,q,ca,cb);
            out.push(store(valid,true));out.push(pop());''')
s=replace(s,'None,None));out.push(store(temp,false));','''None,None));
            linear(&mut out,o,o.q_target.0,ca,cb);out.push(store(temp,false));''')
s+='''
// (a xor ca)(b xor cb) = ab xor ca*b xor cb*a xor ca*cb.
fn linear(out:&mut Vec<Op>,o:Op,target:u64,ca:bool,cb:bool) {
    if ca {out.push(gate(K::CX,Some(o.q_control2.0),None,Some(target),None,None));}
    if cb {out.push(gate(K::CX,Some(o.q_control1.0),None,Some(target),None,None));}
    if ca&&cb {out.push(gate(K::X,None,None,Some(target),None,None));}
}
'''
s+=(root/'polarity_tests.rs').read_text();p.write_text(s)
# Independent emitter reconstructs the complete stream and aligns measurements.
replay=root/'replay';(replay/'src').mkdir(parents=True)
for name in ['Cargo.toml','Cargo.lock']:shutil.copyfile(old/name,replay/name)
s=(root.parent/'toffoli-readiness-20261015/wide-replay/crate/src/main.rs').read_text()
s=replace(s,'    let mut plans=vec![];','''    let mut plans=vec![];let mut polarities=HashMap::new();
    for line in log.lines().filter(|l|l.starts_with("CACHE_POLARITY ")) {
        let v:Vec<usize>=line.split_whitespace().skip(1).map(|x|x.split_once('=').unwrap().1.parse().unwrap()).collect();
        assert_eq!(v.len(),3);assert!(v[1]<=1&&v[2]<=1);assert!(polarities.insert(v[0],(v[1]!=0,v[2]!=0)).is_none());
    }''')
s=replace(s,'None,Some(v+2)),usize::MAX);emit(pop(),usize::MAX);','''None,Some(v+2)),usize::MAX);
            let (a,b)=polarities[p.uses.last().unwrap()];
            if a {emit(newop(K::Z,None,None,Some(o.q_control2.0),None,Some(v+2)),usize::MAX);}
            if b {emit(newop(K::Z,None,None,Some(o.q_control1.0),None,Some(v+2)),usize::MAX);}
            if a&&b {emit(newop(K::Neg,None,None,None,None,Some(v+2)),usize::MAX);}
            emit(pop(),usize::MAX);''')
s=replace(s,'None,None),usize::MAX);emit(store(v,true),usize::MAX);emit(pop(),usize::MAX);','''None,None),usize::MAX);
            let (a,b)=polarities[&i];
            if a {emit(newop(K::CX,Some(o.q_control2.0),None,Some(p.donor),None,None),usize::MAX);}
            if b {emit(newop(K::CX,Some(o.q_control1.0),None,Some(p.donor),None,None),usize::MAX);}
            if a&&b {emit(newop(K::X,None,None,Some(p.donor),None,None),usize::MAX);}
            emit(store(v,true),usize::MAX);emit(pop(),usize::MAX);''')
s=replace(s,'None,None),usize::MAX);emit(store(v+1,false),usize::MAX);','''None,None),usize::MAX);
            if a {emit(newop(K::CX,Some(o.q_control2.0),None,Some(o.q_target.0),None,None),usize::MAX);}
            if b {emit(newop(K::CX,Some(o.q_control1.0),None,Some(o.q_target.0),None,None),usize::MAX);}
            if a&&b {emit(newop(K::X,None,None,Some(o.q_target.0),None,None),usize::MAX);}
            emit(store(v+1,false),usize::MAX);''')
(replay/'src/main.rs').write_text(s)
(root/'manifest.json').write_text(json.dumps({'status':'external-component-only','score':None,'source_revision':'b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7','source_sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for d in [dest,replay] for p in d.rglob('*') if p.is_file()}},indent=2)+'\n')
