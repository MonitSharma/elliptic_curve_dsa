from pathlib import Path
import subprocess
import sys
base,dest,helper=map(Path,sys.argv[1:])
subprocess.run([sys.executable,str(helper),str(base),str(dest)],check=True)
(dest/'src/cache_audit.rs').write_bytes(Path(__file__).with_name('cache_audit.rs').read_bytes())
query='''
impl Support {
    pub(crate) fn cache_product(&mut self,op:&Op)->(bool,Vec<u64>) {
        let a=self.qubits[op.q_control1.0 as usize].clone();
        let b=self.qubits[op.q_control2.0 as usize].clone();
        let p=self.and(&a,&b);(p.constant,p.atoms)
    }
}
'''
(dest/'src/interned_witness.rs').write_text((base/'src/point_add/interned_witness.rs').read_text()+query)
p=dest/'src/main.rs';s=p.read_text().replace('mod affine_simplify;','mod affine_simplify;\nmod cache_audit;\nmod interned_witness;')
s=s.replace('    truth_simplify::audit_zero(&ops,args[2].parse().unwrap());','    cache_audit::audit(&ops);')
p.write_text(s)
p=dest/'Cargo.toml';p.write_text(p.read_text().replace('name="wire_zero_audit"','name="cache_audit"'))
