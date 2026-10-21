from pathlib import Path
import hashlib,json,tarfile,re,shutil,difflib
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-public1829-reproduction-20261020';r=ex/'breakthrough-public-product-generic-repeat-20261020';r.mkdir(exist_ok=False);t=r/'candidate';t.mkdir();f=json.loads((old/'SOURCE-FREEZE.json').read_bytes());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
for p,h in f['protected_files'].items():
 src=ex/'breakthrough-value-guard-fusion-audit-20261020/local-protected'/p;assert sha(src)==h;dest=t/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
original={}
with tarfile.open(old/'point-add-source.tar.gz')as ar:
 assert {m.name for m in ar.getmembers()}==set(f['source_files'])
 for m in ar.getmembers():
  assert m.isfile()and m.name.startswith('src/point_add/')and'..'not in Path(m.name).parts;data=ar.extractfile(m).read();assert hashlib.sha256(data).hexdigest()==f['source_files'][m.name];original[m.name]=data;p=t/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
p=t/'src/point_add/mod.rs';s=p.read_text(encoding='utf-8');matches=list(re.finditer(r'pub fn build\s*\(\)\s*->\s*Vec<Op>\s*\{',s));assert len(matches)==1;match=matches[0];s=s[:match.start()]+s[match.start():match.end()].replace('pub fn build','fn product_repeat_parent_build')+s[match.end():];assert 'mod breakthrough_generic;'not in s;s+='\nmod breakthrough_generic;mod product_repeat;\npub fn build()->Vec<Op>{product_repeat::run(product_repeat_parent_build())}\n';p.write_text(s,encoding='utf-8')
generic=ex/'breakthrough-local-de8-replay-20261020/candidate/src/point_add/breakthrough_generic.rs';shutil.copyfile(generic,t/'src/point_add/breakthrough_generic.rs')
for n in ['truth_simplify.rs','affine_simplify.rs','quadratic_simplify.rs','interned_witness.rs','mabsorb.rs','pscan.rs','cond_pass.rs','sqtop_pass.rs','zero_force.rs','classical_factors_xor.rs','classical_wide/mod.rs']:assert(t/'src/point_add'/n).exists(),n
runtime='''use crate::circuit::{Op,OperationType as K,QubitId};use sha3::{Digest,Sha3_256};
fn strip_identity_tail(mut ops:Vec<Op>)->Vec<Op>{assert!(ops.len()>=96);let no=u64::MAX;let end=ops.len()-96;for pair in ops[end..].chunks_exact(2){assert_eq!(pair[0],pair[1]);let o=pair[0];assert_eq!(o.kind,K::X);assert!(o.q_target.0<2);assert_eq!((o.q_control2.0,o.q_control1.0,o.c_target.0,o.c_condition.0,o.r_target.0),(no,no,no,no,no));}ops.truncate(end);ops}
pub(super)fn run(ops:Vec<Op>)->Vec<Op>{assert_eq!(ops.len(),11682054);let mut h=Sha3_256::new();for o in &ops{for v in[o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(v.to_le_bytes());}}assert_eq!(format!("{:x}",h.finalize()),"3000fc9119ca08944ea9f087f1f69d42a149ede69ea6221b8a60e2f23929171b");let mut ops=super::breakthrough_generic::run(strip_identity_tail(ops));for _ in 0..48{let mut o=Op::empty();o.kind=K::X;o.q_target=QubitId(0);ops.extend([o,o]);}ops}
#[cfg(test)]mod tests{use super::*;
fn tail(k:u64)->Vec<Op>{let mut ops=vec![];for bit in 0..48{let mut o=Op::empty();o.kind=K::X;o.q_target=QubitId((k>>bit)&1);ops.extend([o,o]);}ops}
#[test]fn every_pair_of_the_actual_identity_tail_is_checked(){for k in[0,261,(1u64<<48)-1]{assert!(strip_identity_tail(tail(k)).is_empty());}}
#[test]#[should_panic]fn asymmetric_tail_is_not_silently_removed(){let mut ops=tail(0);ops[95].q_target=QubitId(1);strip_identity_tail(ops);}
#[test]#[should_panic]fn quantum_data_gate_is_not_accepted_as_a_tail(){let mut ops=tail(0);ops[94].q_target=QubitId(2);ops[95].q_target=QubitId(2);strip_identity_tail(ops);}
}
''';(t/'src/point_add/product_repeat.rs').write_text(runtime)
files={p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()};freeze={'base':f['base'],'source_files':files,'protected_files':f['protected_files'],'identity_nonce':0,'parent_stream_sha256':'16567ee18910b8ee9f7aca60c33f0aa88df9679e6528fa5a7884e74e1a877baf','generic_source_sha256':sha(generic),'scope':'Exact currentpublic1829 builder and ALL source-bound tables unchanged, full canonical output binding3000fc before checking/removing actual96op identity tail. Repeat the byte-unchanged existing generic simplification pipeline from currentofficialde8, append diagnosticnonce0. No arithmetic/cut/window/round/table changes. Parent186files verified from official archive; all17protected unchanged. Component source only, native3tail validation before generation; no pointinputs/gate/nonce/score. ActualQ/staticresource diagnostics determine whether fresh development is worthwhile.'};(r/'SOURCE-FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n')
patch=[]
for p in files:
 before=original.get(p,b'');after=(t/p).read_bytes()
 if before!=after:patch.extend(difflib.unified_diff(before.decode('utf-8').splitlines(True),after.decode('utf-8').splitlines(True),fromfile='a/'+p,tofile='b/'+p))
(r/'source.patch').write_text(''.join(patch),encoding='utf-8')
with tarfile.open(r/'point-add-source.tar.gz','w:gz')as ar:
 for p in sorted(files):ar.add(t/p,arcname=p,recursive=False)
(r/'verify.py').write_text('''import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE-FREEZE.json').read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(r/'candidate'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());stats=r.parent/'breakthrough-public1829-width-port-local-v4-20261020/stats-tool/target/release/native_width_stats';subprocess.run([str(stats),str(r/'candidate/ops.bin'),str(r/'STATS.json')],check=True);(r/'RESULT.json').write_text(json.dumps({'status':'PUBLIC_PRODUCT_GENERIC_REPEAT_COMPONENT_NOT_SCORED','native_tail_controls':3,'stream_sha256':sha(r/'candidate/ops.bin'),'static_diagnostics':json.loads((r/'STATS.json').read_text()),'scope':f['scope']},indent=2)+'\\n')
''')
s=(ex/'breakthrough-de8-generic-repeat-v3-20261020/run-local.sh').read_text().replace('breakthrough-de8-generic-repeat-v3-20261020',r.name).replace('point_add::repeat_generic_cache::cache_tests','point_add::product_repeat::tests').replace('1 passed; 0 failed;','3 passed; 0 failed;');(r/'run-local.sh').write_bytes(s.encode());(r/'.gitignore').write_text('candidate/\n__pycache__/\n');(r/'.gitattributes').write_text('* -text\n');(r/'PLAN.md').write_text('# Fixed exact generic repeat on the current product parent\n\n'+freeze['scope']+'\n\nAny competitive complete source needs its own fresh development and sole final failure-rate gate vs exact then-current publicproduct parent. A future value-filter may reject only when separately source-certified and qualified on the ORIGINAL packet transcript; current symbolic results remain research only. Automatically upload only a complete unchanged-benchmark improvement after all gates.\n');print(r.name)
