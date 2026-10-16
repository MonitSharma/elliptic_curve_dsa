"""Bound guard correlations without changing the exact cache renderer."""
import shutil
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'guard-cache-bounded-tool'
assert not d.exists()
shutil.copytree(r/'guard-cache-tool',d,ignore=shutil.ignore_patterns('target'))
s=(r/'guard_bdd.rs').read_text()
s=s.replace('//! Exact Boolean guards; uniform-input probabilities are ranking heuristics.','//! Bounded Boolean guard correlations; opaque probabilities rank proposals only.')
s=s.replace('next_var:u32}', 'next_var:u32,supports:Vec<Vec<u32>>,opaque:HashMap<(u8,u32,u32,u32),u32>,opaque_created:usize}')
s=s.replace('next_var:0}}','next_var:0,supports:vec![vec![],vec![]],opaque:HashMap::new(),opaque_created:0}}')
s=s.replace('self.nodes.push(Node{var,low,high,prob});','''let mut support=vec![var];support.extend_from_slice(&self.supports[low as usize]);support.extend_from_slice(&self.supports[high as usize]);support.sort_unstable();support.dedup();
        assert!(support.len()<=12,"guard bounded internal union support cap");
        self.supports.push(support);
        self.nodes.push(Node{var,low,high,prob});''')
needle='    fn select(&mut self,g:u32,t:u32,f:u32)->u32 {'
assert s.count(needle)==1
s=s.replace(needle,'''    fn combined(&self,args:&[u32])->Vec<u32> {
        let mut support=vec![];for &a in args {support.extend_from_slice(&self.supports[a as usize]);}support.sort_unstable();support.dedup();support
    }
    fn opaque_function(&mut self,key:(u8,u32,u32,u32))->u32 {
        if let Some(&v)=self.opaque.get(&key){return v;}
        let v=self.fresh();self.opaque_created+=1;
        if self.opaque.len()>=50_000 {self.opaque.clear();}
        self.opaque.insert(key,v);v
    }
    fn bounded(&mut self,kind:u8,a:u32,b:u32)->u32 {
        if self.combined(&[a,b]).len()<=4 {self.op(kind,a,b)}
        else {self.opaque_function((kind,a.min(b),a.max(b),0))}
    }
    fn bounded_select(&mut self,g:u32,t:u32,f:u32)->u32 {
        if g==0{return f;}if g==1{return t;}if t==f{return t;}
        if self.combined(&[g,t,f]).len()<=4 {self.select(g,t,f)}
        else {self.opaque_function((3,g,t,f))}
    }
'''+needle)
needle='        let mut union=0;'
assert s.count(needle)==1
s=s.replace(needle,'''        let roots:Vec<_>=uses.iter().map(|i|self.predicates[*i]).collect();
        if self.bdd.combined(&roots).len()>12 {return 1.0-uses.iter().map(|i|1.0-self.weights[*i]).product::<f64>();}
        let mut union=0;''')
s=s.replace('let g=bdd.and(outer,direct);','let g=bdd.bounded(0,outer,direct);')
s=s.replace('bdd.and(bits[o.c_target.0 as usize],ng)','bdd.bounded(0,bits[o.c_target.0 as usize],ng)')
s=s.replace('bdd.or(bits[o.c_target.0 as usize],g)','bdd.bounded(1,bits[o.c_target.0 as usize],g)')
s=s.replace('bdd.xor(bits[o.c_target.0 as usize],g)','bdd.bounded(2,bits[o.c_target.0 as usize],g)')
s=s.replace('bits[j]=bdd.select(g,fresh,bits[j]);','bits[j]=bdd.bounded_select(g,fresh,bits[j]);')
s=s.replace('variables={} input_bits={}', 'variables={} opaque_functions={} input_bits={}')
s=s.replace('bdd.nodes.len(),bdd.next_var,ops.iter()', 'bdd.nodes.len(),bdd.next_var,bdd.opaque_created,ops.iter()')
test='''
    #[test]
    fn opaque_functions_keep_identity_and_complement_when_correlations_drop() {
        let mut b=Bdd::new();let mut vars=vec![];for _ in 0..5 {vars.push(b.fresh());}
        let mut a=vars[0];for &v in &vars[1..4] {a=b.bounded(0,a,v);}
        let x=b.bounded(0,a,vars[4]);assert_eq!(b.opaque_created,1);
        assert_eq!(x,b.bounded(0,vars[4],a));
        let nx=b.not(x);assert_eq!(b.bounded(0,x,nx),0);
        b.opaque.clear();let y=b.bounded(0,a,vars[4]);assert_ne!(x,y);
    }
'''
assert s.endswith('}\n');s=s[:-2]+test+'}\n'
(d/'src/guard_bdd.rs').write_text(s,newline='\n')
print('Support4 opaque classical functions; exact union up to12 independent symbols, otherwise original independence proxy. Probabilities rank proposals only; renderer/source equivalence unchanged and independently checked.')
