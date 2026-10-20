import hashlib,json,shutil
from pathlib import Path
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-value-aig-audit-20261020';r=ex/'breakthrough-value-aig-cnf-qualification-20261020';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest()
for n in ['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
for n in ['Cargo.toml','Cargo.lock','io.rs','audit.rs','FAILURE-FIXTURES.json']:shutil.copyfile(old/'local-tool'/n,t/n)
core=(old/'local-tool/aig.rs').read_bytes();extra=b'''
#[cfg(test)]mod cnf_exhaustive_tests{use super::*;
 #[test]fn actual_emitted_signed_cnf_equals_full_dag_truth_table(){let mut aig=Aig::default();let x=aig.node(0,0,0);let y=aig.node(0,1,0);let z=aig.node(0,2,0);let xy=aig.and(x^1,y);let xor=aig.xor(xy,z^1);let root=aig.ite(y,xor,x);for output in[0,1,xy,xor,root,root^1]{for expected in[false,true]{let(text,vars,_)=cnf(&aig,&[output],&[expected]);assert!(vars<16);let clauses:Vec<Vec<i64>>=text.lines().skip(1).map(|l|l.split_whitespace().map(|v|v.parse::<i64>().unwrap()).take_while(|&v|v!=0).collect()).collect();let mut live=vec![false;aig.nodes.len()];let mut stack=vec![output];while let Some(v)=stack.pop(){if v<=1{continue;}let i=(v/2-1)as usize;if live[i]{continue;}live[i]=true;let(k,a,b)=aig.nodes[i];if k!=0{stack.push(a);stack.push(b);}}let mut map=vec![None;aig.nodes.len()];let mut at=0;for(i,&yes)in live.iter().enumerate(){if yes{map[i]=Some(at);at+=1;}}assert_eq!(at,vars);for assignment in 0..(1usize<<vars){let mut random=vec![0;3];for(i,&(k,r,_))in aig.nodes.iter().enumerate(){if k==0{if let Some(bit)=map[i]{random[r as usize]=((assignment>>bit)&1)as u64;}}}let actual=aig.evaluate(&random);let consistent=map.iter().enumerate().all(|(i,b)|b.map(|bit|((assignment>>bit)&1!=0)==actual[i]).unwrap_or(true));let semantically=consistent&&literal_value(output,&actual)==expected;let encoded=clauses.iter().all(|c|c.iter().any(|&v|{let value=(assignment>>((v.unsigned_abs()-1)as usize))&1!=0;if v>0{value}else{!value}}));assert_eq!(encoded,semantically,"output{output} expected{expected} assignment{assignment}");}}}}
}
'''
(t/'aig.rs').write_bytes(core+extra);(r/'aig-cnf-qualification.rs').write_bytes(extra)
f=json.loads((old/'SOURCE-FREEZE.json').read_bytes());f.update(source_files={n:sha((t/n).read_bytes())for n in ['Cargo.toml','Cargo.lock','io.rs','audit.rs','aig.rs','FAILURE-FIXTURES.json']},native_controls=24,original_core_aig_sha256=sha(core),original_experiment=old.name,scope='Original AIG/CNF production source byte prefix unchanged; append cfg(test) exhaustive actual emitted signed-CNF qualification only. No new source input, gate, nonce or CNF selection.');(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
base='/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments';script='''#!/bin/sh
set -eu
cd BASE/breakthrough-value-aig-cnf-qualification-20261020
export RUSTC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc
export RUSTDOC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustdoc
export RUSTUP_AUTO_INSTALL=0
export CARGO_HOME=/root/.cargo
export CARGO_BUILD_JOBS=2
export OMP_NUM_THREADS=1
export CARGO_TARGET_DIR=BASE/breakthrough-value-guard-fusion-audit-20261020/local-tool/target
trap 's=$?; printf "%s\\n" "$s" > run.exit' EXIT
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo test --release --locked --manifest-path local-tool/Cargo.toml --bin value_aig_audit -- --nocapture > tests.log 2>&1
grep -q 'test result: ok. 24 passed; 0 failed;' tests.log
'''.replace('BASE',base);(r/'run-local.sh').write_bytes(script.encode())
p=old/'.gitignore';s=p.read_text();p.write_text(s+'*.cnf\n')
print(r.name)
