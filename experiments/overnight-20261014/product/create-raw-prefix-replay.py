"""Native raw prefix observer; same protected loader/library and true signed seed contract."""
from pathlib import Path
import subprocess,sys
base=Path(sys.argv[1]).resolve();dest=Path(sys.argv[2]).resolve()
subprocess.run([sys.executable,str(Path(__file__).with_name('create-prefix-replay.py')),str(base),str(dest)],check=True)
s=dest.joinpath('src/main.rs').read_text()
needle='let p=curve.modulus;let mut start=0;let mut depth=0;'
new='let rw:Vec<usize>=a[4].split(",").map(|x|x.parse().unwrap()).collect();assert!(rw.len()>256);'+needle
assert s.count(needle)==1;s=s.replace(needle,new)
needle='   println!("PREFIX_SHOT phase={label}'
at=s.index(needle)
code=r'''
   if label=="square" {
    let low=sim.get_register(&regs[0],lane);let sg=(sim.qubits[*rw.last().unwrap()]>>lane)&1;
    let uniform=rw[256..].iter().all(|&q|((sim.qubits[q]>>lane)&1)==sg);
    let f=U256::from(2u64).pow(U256::from(32))+U256::from(977);
    let rn=quantum_ecc::weierstrass_elliptic_curve::sub_mod(low.reduce_mod(p),if sg==1{f}else{U256::ZERO},p);
    let before=v[0].add_mod(v[2].add_mod(v[2],p),p);let expected=quantum_ecc::weierstrass_elliptic_curve::sub_mod(before,lambda.mul_mod(lambda,p),p);
    let delta=quantum_ecc::weierstrass_elliptic_curve::sub_mod(expected,rn,p);
    println!("R0_SHOT index={lane} family={} low={low:#x} sign={sg} extension_uniform={uniform} odd={} residue={rn:#x} expected={expected:#x} delta={delta:#x} residue_correct={}",families[lane],low.bit(0),rn==expected);
   }
'''
s=s[:at]+code+s[at:]
dest.joinpath('src/main.rs').write_text(s,newline='\n')
t=dest.joinpath('Cargo.toml').read_text().replace('name="product_prefix_replay"','name="product_raw_prefix_replay"')
dest.joinpath('Cargo.toml').write_text(t,newline='\n')
