"""Give opaque guard functions derived probability proxies instead of 1/2."""
import shutil
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'guard-cache-weighted-tool'
assert not d.exists()
shutil.copytree(r/'guard-cache-bounded-tool',d,ignore=shutil.ignore_patterns('target'))
p=d/'src/guard_bdd.rs';s=p.read_text()
s=s.replace('next_var:u32,','next_var:u32,var_probs:Vec<f64>,')
s=s.replace('next_var:0,','next_var:0,var_probs:vec![],')
old='let prob=0.5*(self.nodes[low as usize].prob+self.nodes[high as usize].prob);'
assert s.count(old)==1;s=s.replace(old,'let p=self.var_probs[var as usize];let prob=(1.0-p)*self.nodes[low as usize].prob+p*self.nodes[high as usize].prob;')
old='fn fresh(&mut self)->u32 {let v=self.next_var;self.next_var+=1;self.node(v,0,1)}'
assert s.count(old)==1;s=s.replace(old,'''fn fresh(&mut self)->u32 {self.fresh_weighted(0.5)}
    fn fresh_weighted(&mut self,p:f64)->u32 {let v=self.next_var;self.next_var+=1;self.var_probs.push(p.clamp(0.0,1.0));self.node(v,0,1)}''')
s=s.replace('fn opaque_function(&mut self,key:(u8,u32,u32,u32))->u32','fn opaque_function(&mut self,key:(u8,u32,u32,u32),prob:f64)->u32')
s=s.replace('let v=self.fresh();self.opaque_created+=1;','let v=self.fresh_weighted(prob);self.opaque_created+=1;')
old='else {self.opaque_function((kind,a.min(b),a.max(b),0))}'
assert s.count(old)==1;s=s.replace(old,'''else {
            let pa=self.nodes[a as usize].prob;let pb=self.nodes[b as usize].prob;
            let prob=match kind {0=>pa*pb,1=>pa+pb-pa*pb,2=>pa+pb-2.0*pa*pb,_=>unreachable!()};
            self.opaque_function((kind,a.min(b),a.max(b),0),prob)
        }''')
old='else {self.opaque_function((3,g,t,f))}'
assert s.count(old)==1;s=s.replace(old,'''else {
            let pg=self.nodes[g as usize].prob;let pt=self.nodes[t as usize].prob;let pf=self.nodes[f as usize].prob;
            self.opaque_function((3,g,t,f),pg*pt+(1.0-pg)*pf)
        }''')
needle='assert_eq!(b.opaque_created,1);'
assert s.count(needle)==1;s=s.replace(needle,needle+'assert_eq!(b.nodes[x as usize].prob,1.0/32.0);')
s=s.replace('opaque probabilities rank proposals only','derived opaque probability proxies rank proposals only')
p.write_text(s,newline='\n')
print('Opaque probability proxies propagated from operand probabilities under independence; Boolean subfunction identities retained, no quantum changes. Ranking is heuristic; full cache reconstruction mandatory.')
