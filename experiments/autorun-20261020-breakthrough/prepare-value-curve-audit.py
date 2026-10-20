"""Check exact value certificates on valid curve points, separately from gates/nonces."""
import ast,hashlib,json,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[2];ex=root/'experiments';old=ex/'breakthrough-value-guard-fusion-audit-20261020';r=ex/'breakthrough-value-curve-audit-20261020';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
for n in ['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
for n in ['io.rs','Cargo.lock']:shutil.copyfile(old/'local-tool'/n,t/n)
s=(old/'audit.rs').read_text();pos=s.index('struct AuditWords')
source='''fn audit_curve()->quantum_ecc::weierstrass_elliptic_curve::WeierstrassEllipticCurve{quantum_ecc::weierstrass_elliptic_curve::WeierstrassEllipticCurve{modulus:"0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F".parse().unwrap(),a:0u64.into(),b:7u64.into(),gx:"0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798".parse().unwrap(),gy:"0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8".parse().unwrap(),order:"0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141".parse().unwrap()}}
fn curve_abstract_audit(p:&Program,ops:&[Op],outputs:&[usize])->serde_json::Value{
 use quantum_ecc::sim::Simulator;use quantum_ecc::circuit::QubitOrBit;use sha3::digest::{Update,ExtendableOutput,XofReader};
 let curve=audit_curve();let(_,_,_,regs)=analyze_ops(ops.iter());assert_eq!(regs.len(),4);assert!(regs.iter().all(|r|r.len()==256));let mut h=sha3::Shake256::default();h.update(b"value-valid-curve-source-audit-20261020-v1");let mut xof=h.finalize_xof();let mut noise=0xa8d7135f23649b01u64;let mut rows=vec![];
 for batch in 0..32{let mut init_rng=AuditWords{v:vec![],at:0};let mut init=Simulator::new(p.nq,p.nb,&mut init_rng);let mut expected_q=vec![0u64;p.nq];let mut inputs=vec![];
  while inputs.len()<64{let mut rb=[[0u8;32];2];xof.read(&mut rb[0]);xof.read(&mut rb[1]);let hex=|b:&[u8]|format!("0x{}",b.iter().rev().map(|v|format!("{v:02x}")).collect::<String>());let k1=hex(&rb[0]).parse().unwrap();let k2=hex(&rb[1]).parse().unwrap();let a=curve.mul(curve.gx,curve.gy,k1);let b=curve.mul(curve.gx,curve.gy,k2);if a.0==b.0||(a.0.is_zero()&&a.1.is_zero())||(b.0.is_zero()&&b.1.is_zero()){continue;}assert!(curve.is_on_curve(a.0,a.1)&&curve.is_on_curve(b.0,b.1));let e=curve.add(a.0,a.1,b.0,b.1);let lane=inputs.len();for(i,value)in[a.0,a.1,b.0,b.1].into_iter().enumerate(){init.set_register(&regs[i],value,lane);}for(i,value)in[e.0,e.1].into_iter().enumerate(){for(bit,item)in regs[i].iter().enumerate(){match item{QubitOrBit::Qubit(id)=>expected_q[id.0 as usize]|=(value.bit(bit)as u64)<<lane,_=>panic!("Expected quantum outputs")}}}inputs.push(serde_json::json!({"k1_le":rb[0].iter().map(|v|format!("{v:02x}")).collect::<String>(),"k2_le":rb[1].iter().map(|v|format!("{v:02x}")).collect::<String>()}));}
  let q=init.qubits.clone();let bits=init.bits.clone();drop(init);let abstract_q=abstract_eval(p,&q,&bits);let known:u64=outputs.iter().map(|&q|(abstract_q[q].z|abstract_q[q].o).count_ones()as u64).sum();let mut certified_wrong=0u64;for &q in outputs{certified_wrong|=(abstract_q[q].o^expected_q[q])&(abstract_q[q].z|abstract_q[q].o);}let mut concrete_wrong=vec![];
  for pattern in 0..3{let words:Vec<u64>=(0..p.rng).map(|_|if pattern==0{0}else if pattern==1{u64::MAX}else{noise=noise.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);noise}).collect();let mut rng=AuditWords{v:words.iter().flat_map(|x|x.to_le_bytes()).collect(),at:0};let mut sim=Simulator::new(p.nq,p.nb,&mut rng);sim.qubits.copy_from_slice(&q);sim.bits.copy_from_slice(&bits);sim.apply_iter(ops.iter());let mut exact_ir=q.clone();eval(p,&mut exact_ir,&bits,&words);let mut wrong=0u64;for &q in outputs{assert_eq!(exact_ir[q],sim.qubits[q],"Validcurve IR/protected mismatch batch{batch} pattern{pattern}");wrong|=sim.qubits[q]^expected_q[q];}verify_abstract(&abstract_q,&sim.qubits,outputs);assert_eq!(certified_wrong&!wrong,0,"Unsound wrongpoint certificate");concrete_wrong.push(serde_json::json!({"pattern":pattern,"wrong_shot_mask":format!("{wrong:016x}"),"wrong_shots":wrong.count_ones()}));drop(sim);assert_eq!(rng.at,p.rng*8);}
  eprintln!("VALID_CURVE_PROTECTED_PASS batch={batch} known_bits={known} certified_wrong_shots={}",certified_wrong.count_ones());rows.push(serde_json::json!({"batch":batch,"inputs":inputs,"known_output_bits":known,"total_output_bits":outputs.len()*64,"certified_wrong_mask":format!("{certified_wrong:016x}"),"certified_wrong_shots":certified_wrong.count_ones(),"concrete_patterns":concrete_wrong}));
 }
 serde_json::json!({"label":"value-valid-curve-source-audit-20261020-v1","input_batches":32,"shots":2048,"protected_fullstream_value_comparisons":96,"batches":rows,"nonce_screens":0,"scope":"Verification-only fixtures on valid secp256k1 points using protected reference/set_register. Not a statistical gate, nonce search, acceptance certificate or resource score. Exact abstract semantics over all RNG outcomes; concrete controls test implementation only. Earlier arbitrary-bit fixtures establish no conclusion about valid-curve filter usefulness."})
}
'''
s=s[:pos]+source+s[pos:];needle='let abstract_result=full_abstract_audit(&p,&ops,&outputs);';assert s.count(needle)==1;s=s.replace(needle,needle+'let curve_result=curve_abstract_audit(&p,&ops,&outputs);').replace('"abstract_audit":abstract_result,','"curve_audit":curve_result,"abstract_audit":abstract_result,')
pos=s.rfind('\n}');s=s[:pos]+'''\n #[test]fn valid_curve_fixture_reference_checks_group_and_distinct_points(){let c=audit_curve();c.verify();let p=c.mul(c.gx,c.gy,2u64.into());assert!(c.is_on_curve(p.0,p.1));assert_ne!(p.0,c.gx);assert_eq!(c.add(c.gx,c.gy,c.gx,c.gy),p);}\n'''+s[pos:]
(r/'audit.rs').write_text(s);(t/'audit.rs').write_text(s)
manifest=(old/'local-tool/Cargo.toml').read_text().replace('../local-protected','../../breakthrough-value-guard-fusion-audit-20261020/local-protected').replace('name="value_ir_audit"','name="value_curve_audit"');assert 'name="value_curve_audit"'in manifest;(t/'Cargo.toml').write_text(manifest)
protected=json.loads((old/'LOCAL-TEST-FREEZE.json').read_bytes())['protected_files'];(r/'SOURCE-FREEZE.json').write_text(json.dumps({'source_files':{n:sha((t/n).read_bytes())for n in ['Cargo.toml','Cargo.lock','io.rs','audit.rs']},'protected_files':protected,'expected_stream_sha256':'6192778816154b713a714446b3e7d28165a649460173a3e3f17d9de06fa7bb96','native_controls':21,'scope':'Frozen verification tool only, valid-curve fixtures supplement arbitrary bit fixtures. No circuit/gate/nonce change. Exact old stream reproduced locally before audit. Existing local compiler1.99; serverqualification still required for future production.'},indent=2)+'\n')
base='/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments';script='''#!/bin/sh
set -eu
cd BASE/breakthrough-value-curve-audit-20261020
export RUSTC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc
export RUSTDOC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustdoc
export RUSTUP_AUTO_INSTALL=0
export CARGO_HOME=/root/.cargo
export CARGO_BUILD_JOBS=2
export OMP_NUM_THREADS=1
export CARGO_TARGET_DIR=BASE/breakthrough-value-guard-fusion-audit-20261020/local-tool/target
trap 's=$?; printf "%s\\n" "$s" > run.exit' EXIT
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo test --release --locked --manifest-path local-tool/Cargo.toml --bin value_curve_audit -- --nocapture > tests.log 2>&1
grep -q 'test result: ok. 21 passed; 0 failed;' tests.log
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo build --release --locked --manifest-path local-tool/Cargo.toml --bin value_curve_audit > build.log 2>&1
python3 verify-input.py
timeout 2400 "$CARGO_TARGET_DIR/release/value_curve_audit" BASE/breakthrough-local-product-filter-replay-20261020/candidate/ops.bin full-audit.json > full-audit.log 2>&1
'''.replace('BASE',base);(r/'run-local.sh').write_bytes(script.encode())
(r/'verify-input.py').write_text('''import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE-FREEZE.json').read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(r/'local-tool'/p)==h for p,h in f['source_files'].items());deps=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-protected';assert all(sha(deps/p)==h for p,h in f['protected_files'].items());assert sha(r.parent/'breakthrough-local-product-filter-replay-20261020/candidate/ops.bin')==f['expected_stream_sha256']
''')
(r/'launch-local.sh').write_bytes(('''#!/bin/sh
set -eu
cd BASE/breakthrough-value-curve-audit-20261020
test ! -e run.pid
nohup setsid sh run-local.sh > run.log 2>&1 < /dev/null &
printf '%s\\n' "$!" > run.pid
cat run.pid
'''.replace('BASE',base)).encode())
(r/'PLAN.md').write_text('''# Valid curve fixtures for the exact failure-filter audit

Earlier fullsource tests use arbitrary registered bit patterns. Zero knownoutput
bits on those fixtures is not evidence that valid-curve filters cannot work.
Preserve those results. Add32fixed-label validcurve batches of64 shots, generated
using the protected secp256k1 reference and same register ABI/exclusions as scorer.
Compare three concrete RNG patterns in full protected simulator; independently
verify exact IR outputs and any certifiedwrong subset versus reference P+A.
Retain20 native controls and add curve-reference/generator/order/doubling test.
Freeze tool before21 native tests, require exact locally reproduced oldstream6192.
No input from a challenge packet, nonce rejection/search, gate/census verdict,
quantumresource claim or submission. All previous gate verdicts remain final.
''')
print(r.name)
