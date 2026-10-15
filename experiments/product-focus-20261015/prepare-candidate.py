"""Create an isolated C5 candidate with only permitted point-addition edits."""
from pathlib import Path
import subprocess

root=Path(__file__).resolve().parent
dest=root/'candidate-lazy-v1'
assert not dest.exists(), 'Never overwrite an existing experiment'
subprocess.run(['git','clone','--shared','--no-checkout','/home/hclau/ecdsa_research/upstream',str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach','c5bb1ec876db859a3f9f8a9052c140a145df834e'],check=True)
assert not subprocess.check_output(['git','-C',str(dest),'status','--porcelain'])
base=dest/'src/point_add'
(base/'lazy_cache.rs').write_bytes((root/'lazy_cache_audit.rs').read_bytes()+(root/'lazy_cache_tests.rs').read_bytes())
query='''
impl Support {
    pub(crate) fn cache_zeros(&self)->Vec<usize> {
        self.qubits.iter().enumerate().filter_map(|(q,v)|v.is_zero().then_some(q)).collect()
    }
    pub(crate) fn cache_product(&mut self,op:&Op)->(bool,Vec<u64>) {
        let a=self.qubits[op.q_control1.0 as usize].clone();
        let b=self.qubits[op.q_control2.0 as usize].clone();
        let p=self.and(&a,&b);(p.constant,p.atoms)
    }
}
'''
p=base/'interned_witness.rs';p.write_text(p.read_text()+query)
p=base/'mod.rs';s=p.read_text();needle='    ops = linear_restore::run(ops);';assert s.count(needle)==1
s='mod lazy_cache;\n'+s.replace(needle,needle+'\n    ops = lazy_cache::optimize(ops);')
p.write_text(s)
print(dest)
