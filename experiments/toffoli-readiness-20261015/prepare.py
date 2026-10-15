"""One exact cache candidate on B3; no nonce, packet or arithmetic tuning."""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parent
dest=root/'candidate-b3-cache-v1'
assert not dest.exists()
subprocess.run(['git','clone','--shared','--no-checkout','/home/hclau/ecdsa_research/upstream',str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach','b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'],check=True)
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
p=base/'mod.rs';s=p.read_text();needle='    let nonce: u64 = required_env("TAIL_NONCE");';assert s.count(needle)==1
s='mod lazy_cache;\n'+s.replace(needle,'    ops = lazy_cache::optimize(ops);\n'+needle)
p.write_text(s)
print(dest)
