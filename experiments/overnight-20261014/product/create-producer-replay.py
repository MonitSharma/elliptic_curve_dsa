"""Read real top-level producer/loan word identities with the protected native simulator."""
from pathlib import Path
import subprocess,sys
folder=Path(__file__).parent;base=Path(sys.argv[1]).resolve();dest=Path(sys.argv[2]).resolve()
subprocess.run([sys.executable,str(folder/'create-consumer-prefix-replay.py'),str(base),str(dest)],check=True)
s=dest.joinpath('src/main.rs').read_text()
needle='let p=curve.modulus;let mut start=0;let mut depth=0;'
# The signed observer prefixes rw immediately before this string, preserving the needle.
assert s.count(needle)==1
new=''' let p=curve.modulus;
 let mut observations=std::collections::HashMap::new();
 for line in std::fs::read_to_string(&a[5]).unwrap().lines(){
  let parts:Vec<_>=line.split_whitespace().collect();
  let off=U256::from_str_radix(parts[1].trim_start_matches("0x"),16).unwrap();
  let parse=|v:&str|v.split(',').map(|x|x.parse::<usize>().unwrap()).collect::<Vec<_>>();
  observations.insert(parts[0].to_string(),(off,parse(parts[2]),parse(parts[3])));
 }
 let mut original_inputs:std::collections::HashMap<String,Vec<U256>>=std::collections::HashMap::new();
 let mut original_phases:std::collections::HashMap<String,u64>=std::collections::HashMap::new();
 let mut start=0;let mut depth=0;'''
s=s.replace(needle,new)
needle='  let mut xb=0;let mut yb=0;let mut joint=0;let mut cb=0;'
new='''  if let Some((off,xw,pw))=observations.get(&label){
   let read=|ids:&[usize],lane:usize|{let mut v=U256::ZERO;let mut weight=U256::from(1);for &q in ids{if ((sim.qubits[q]>>lane)&1)!=0{v=v.add_mod(weight,p);}weight=weight.add_mod(weight,p);}v};
   let (policy,stage)=label.split_once('.').unwrap();
   if stage=="input"{original_inputs.insert(policy.to_string(),(0..vals.len()).map(|lane|read(xw,lane)).collect());original_phases.insert(policy.to_string(),sim.phase);}
   for lane in 0..vals.len(){
    let original=original_inputs[policy][lane];let current=read(xw,lane);let product=read(pw,lane);
    let expected=if stage=="input"||stage=="inverse"{U256::ZERO}else{original.mul_mod(original,p).add_mod(*off,p)};
    let delta=quantum_ecc::weierstrass_elliptic_curve::sub_mod(expected,product,p);
    println!("PRODUCER_SHOT label={label} index={lane} family={} input={original:#x} current_input={current:#x} product={product:#x} offset={off:#x} expected={expected:#x} delta={delta:#x} phase={} phase_delta={} product_correct={} input_restored={}",families[lane],(sim.phase>>lane)&1,((sim.phase^original_phases[policy])>>lane)&1,product==expected,current==original);
   }
  }
'''+needle
assert s.count(needle)==1;s=s.replace(needle,new)
dest.joinpath('src/main.rs').write_text(s,newline='\n')
t=dest.joinpath('Cargo.toml').read_text().replace('name="product_consumer_prefix_replay"','name="product_producer_replay"')
dest.joinpath('Cargo.toml').write_text(t,newline='\n')
