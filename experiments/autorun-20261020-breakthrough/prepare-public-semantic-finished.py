from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,tarfile,re,difflib
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-public1829-reproduction-20261020';proof=ex/'breakthrough-global-semantic-component-20261020';diff=ex/'breakthrough-public-semantic-diff-20261021';r=ex/'breakthrough-public-semantic-finished-20261021';r.mkdir(exist_ok=False);t=r/'candidate';t.mkdir();sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();f=json.loads((old/'SOURCE-FREEZE.json').read_bytes());d=json.loads((diff/'DIFF.json').read_bytes());assert d['record_index']==4189602 and d['before']==[13,212,1089,1088,(1<<64)-1,(1<<64)-1,(1<<64)-1]and d['after']==[8,(1<<64)-1,1089,1088,(1<<64)-1,(1<<64)-1,(1<<64)-1]
assert json.loads((proof/'RESULT.json').read_bytes())['cases']['public1829']['proof']['rewrites']=={'ccx_to_cx':1}
for p,h in f['protected_files'].items():
 source=ex/'breakthrough-value-guard-fusion-audit-20261020/local-protected'/p;assert sha(source)==h;dest=t/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
original={}
with tarfile.open(old/'point-add-source.tar.gz')as ar:
 assert {m.name for m in ar.getmembers()}==set(f['source_files'])
 for m in ar.getmembers():
  assert m.isfile()and m.name.startswith('src/point_add/')and'..'not in Path(m.name).parts;data=ar.extractfile(m).read();assert hashlib.sha256(data).hexdigest()==f['source_files'][m.name];original[m.name]=data;p=t/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
p=t/'src/point_add/mod.rs';s=p.read_text();matches=list(re.finditer(r'pub fn build\s*\(\)\s*->\s*Vec<Op>\s*\{',s));assert len(matches)==1;match=matches[0];s=s[:match.start()]+s[match.start():match.end()].replace('pub fn build','fn exact_semantic_parent_build')+s[match.end():];s+='\nmod exact_semantic_product;\npub fn build()->Vec<Op>{exact_semantic_product::run(exact_semantic_parent_build())}\n';p.write_text(s)
module='''use crate::circuit::{Op,OperationType as K,QubitId};use sha3::{Digest,Sha3_256};
pub(super)const IDENTITY_NONCE:u64=0;
fn fields(o:&Op)->[u64;7]{[o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]}
fn canonical(ops:&[Op])->String{let mut h=Sha3_256::new();for o in ops{for v in fields(o){h.update(v.to_le_bytes());}}format!("{:x}",h.finalize())}
fn strip_identity_tail(mut ops:Vec<Op>)->Vec<Op>{assert!(ops.len()>=96);let n=u64::MAX;let end=ops.len()-96;for pair in ops[end..].chunks_exact(2){assert_eq!(pair[0],pair[1]);let o=pair[0];assert_eq!(o.kind,K::X);assert!(o.q_target.0<2);assert_eq!([o.q_control2.0,o.q_control1.0,o.c_target.0,o.c_condition.0,o.r_target.0],[n;5]);}ops.truncate(end);ops}
pub(super)fn run(mut ops:Vec<Op>)->Vec<Op>{let n=u64::MAX;assert_eq!(ops.len(),11682054);assert_eq!(canonical(&ops),"3000fc9119ca08944ea9f087f1f69d42a149ede69ea6221b8a60e2f23929171b","Exact public1829 original source stream binding");let index=4189602;assert_eq!(fields(&ops[index]),[13,212,1089,1088,n,n,n]);let mut replacement=ops[index];replacement.kind=K::CX;replacement.q_control2=QubitId(n);replacement.validate();assert_eq!(fields(&replacement),[8,n,1089,1088,n,n,n]);ops[index]=replacement;assert_eq!(canonical(&ops),"f09ef07a02790dfc2c80293b0d45f25dae824db4a6a024ad52289ca5889c9a5e","Complete native12-qualified semantic output binding");let mut ops=strip_identity_tail(ops);assert!(IDENTITY_NONCE<(1u64<<48));for bit in 0..48{let mut o=Op::empty();o.kind=K::X;o.q_target=QubitId((IDENTITY_NONCE>>bit)&1);ops.extend([o,o]);}eprintln!("EXACT_SEMANTIC_LITERAL record=4189602 nonce={IDENTITY_NONCE} proof=fullprefix_exact_equality");ops}
#[cfg(test)]mod tests{use super::*;
fn tail(nonce:u64)->Vec<Op>{let mut out=vec![];for bit in 0..48{let mut o=Op::empty();o.kind=K::X;o.q_target=QubitId((nonce>>bit)&1);out.extend([o,o]);}out}
#[test]fn every_actual_tail_pair_is_validated(){for n in[0,261,(1u64<<48)-1]{assert!(strip_identity_tail(tail(n)).is_empty());}}
#[test]#[should_panic]fn asymmetric_pair_is_rejected(){let mut v=tail(0);v[95].q_target=QubitId(1);strip_identity_tail(v);}
#[test]#[should_panic]fn quantum_data_gate_is_not_mistaken_for_nonce_padding(){let mut v=tail(0);v[94].q_target=QubitId(2);v[95].q_target=QubitId(2);strip_identity_tail(v);}
#[test]fn exact_implication_kernel_preserves_values_phase_and_detects_missing_precondition(){use crate::sim::Simulator;use sha3::digest::XofReader;struct NoRng;impl XofReader for NoRng{fn read(&mut self,_:&mut[u8]){panic!("No measurement in implication kernel");}}let mut first=Op::empty();first.kind=K::CCX;first.q_control2=QubitId(0);first.q_control1=QubitId(1);first.q_target=QubitId(2);let mut old=first;old.q_control1=QubitId(2);old.q_target=QubitId(3);let mut new=old;new.kind=K::CX;new.q_control2=QubitId(u64::MAX);let(mut ra,mut rb)=(NoRng,NoRng);let(mut a,mut b)=(Simulator::new(4,0,&mut ra),Simulator::new(4,0,&mut rb));for lane in 0..64{for q in[0,1,3]{a.qubits[q]|=((lane>>(q%3)&1)as u64)<<lane;}}b.qubits.clone_from(&a.qubits);a.phase=0xa55a;b.phase=a.phase;a.apply_iter([&first,&old].into_iter());b.apply_iter([&first,&new].into_iter());assert_eq!(a.qubits,b.qubits);assert_eq!(a.phase,b.phase);let(mut rc,mut rd)=(NoRng,NoRng);let(mut c,mut d)=(Simulator::new(4,0,&mut rc),Simulator::new(4,0,&mut rd));c.qubits[2]=u64::MAX;d.qubits.clone_from(&c.qubits);c.apply_iter([&old].into_iter());d.apply_iter([&new].into_iter());assert_ne!(c.qubits,d.qubits);}
}
''';(t/'src/point_add/exact_semantic_product.rs').write_text(module)
files={p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()};assert len(files)==187;patch=[]
for path,h in files.items():
 before=original.get(path,b'');after=(t/path).read_bytes()
 if before!=after:patch.extend(difflib.unified_diff(before.decode('utf-8').splitlines(True),after.decode('utf-8').splitlines(True),fromfile='a/'+path,tofile='b/'+path))
(r/'source.patch').write_text(''.join(patch));
with tarfile.open(r/'point-add-source.tar.gz','w:gz')as ar:
 for path in sorted(files):ar.add(t/path,arcname=path,recursive=False)
spec={'declared_at_utc':datetime.now(timezone.utc).isoformat(),'base':'3eefcf216ca37cba0ae3f56212d6b1302844a249','source_files':files,'protected_files':f['protected_files'],'identity_nonce':0,'operations':11682054,'expected_qubits':1234,'parent_stream_sha256':'16567ee18910b8ee9f7aca60c33f0aa88df9679e6528fa5a7884e74e1a877baf','parent_records_sha3':d['input_records_sha3'],'semantic_records_sha3_with_original_tail':d['output_records_sha3'],'source_archive_sha256':sha(r/'point-add-source.tar.gz'),'source_patch_sha256':sha(r/'source.patch'),'semantic_proof_native_controls':12,'new_runtime_native_controls':4,'semantic_proof_source_freeze_sha256':sha(proof/'SOURCE-FREEZE.json'),'semantic_proof_result_sha256':sha(proof/'RESULT.json'),'single_record_diff_sha256':sha(diff/'DIFF.json'),'prior_component_development_sha256':sha(ex/'breakthrough-public-semantic-development-20261020/DIAGNOSTIC.json'),'scope':'Finished literal exact publicproduct1829 single CCXtoCX atrecord4189602, full input/output canonical bindings; parent ALL186files/tables/cuts/width/arithmetic unchanged. Only final identity tail exposed atnonce0. Source187/protected17 frozen before localnative4/generation, then official1.93crosscompiler bytecontrol, NEWfinished development and OWNsolefinalgate vs exactcurrentpublic1829. No nonce/benchmark/upload beforePASS and qualified source-bound ORIGINAL_FS engine.'}
(r/'SOURCE-SPEC.json').write_text(json.dumps(spec,indent=2)+'\n');(r/'.gitignore').write_text('candidate/\n__pycache__/\n*.ops.bin\n');(r/'.gitattributes').write_text('* -text\n')
(r/'verify.py').write_text('''import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'candidate';f=json.loads((r/'SOURCE-SPEC.json').read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(t/n)==h for n,h in{**f['source_files'],**f['protected_files']}.items());stats=r.parent/'breakthrough-public1829-width-port-local-v4-20261020/stats-tool/target/release/native_width_stats';subprocess.run([str(stats),str(t/'ops.bin'),str(r/'OUTPUT-STATS.json')],check=True);s=json.loads((r/'OUTPUT-STATS.json').read_text());assert s['qubits_protected_analyzer']==1234 and s['operations']==f['operations'];(r/'LOCAL-GENERATION.json').write_text(json.dumps({'status':'FINISHED_NONCE0_LOCAL_NATIVE4_GENERATION_COMPLETE_NOT_GATED_OR_SCORED','source_spec_sha256':sha(r/'SOURCE-SPEC.json'),'stream_sha256':sha(t/'ops.bin'),'records_sha3':s['records_sha3'],'qubits':1234,'operations':s['operations'],'native_controls':4,'prior_semantic_native_proof':12,'scope':f['scope']},indent=2)+'\\n')
''')
base='/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments';(r/'run-local.sh').write_bytes(f'''#!/bin/sh
set -eu
cd {base}/{r.name}
export RUSTC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc
export RUSTDOC=/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustdoc
export RUSTUP_AUTO_INSTALL=0
export CARGO_HOME=/root/.cargo
export CARGO_BUILD_JOBS=2
export OMP_NUM_THREADS=1
export CARGO_TARGET_DIR={base}/breakthrough-value-guard-fusion-audit-20261020/local-tool/target
ulimit -v 10485760
trap 's=$?; printf "%s\\n" "$s" > local.exit' EXIT
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo test --release --locked --manifest-path candidate/Cargo.toml --bin build_circuit point_add::exact_semantic_product::tests -- --nocapture --test-threads=1 > local-tests.log 2>&1
grep -q 'test result: ok. 4 passed; 0 failed;' local-tests.log
/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo build --release --locked --manifest-path candidate/Cargo.toml --bin build_circuit > local-build.log 2>&1
cd candidate
timeout 1800 "$CARGO_TARGET_DIR/release/build_circuit" > ../local-generate.log 2>&1
cd ..
python3 verify.py
'''.encode());(r/'PLAN.md').write_text('# Finished exact semantic product candidate, before formal gate\n\n'+spec['scope']+'\n\nPublic source186files restored byteexact from official archive; only original build renamed into bound wrapper and new exact_semantic_product module. Newnative4 checks complete tailshape and an implication kernel plus missing-precondition fault; actual whole-prefix proof remains the existing native12oracle with exact single-record diff. No packet/census data selects circuit. Only IDENTITY_NONCE may change after a frozen passed gate; lowestpassingnonce and allscreen disclosures mandatory. Globalproductgoal remainsACTIVE.\n');print(r.name,len(files))
