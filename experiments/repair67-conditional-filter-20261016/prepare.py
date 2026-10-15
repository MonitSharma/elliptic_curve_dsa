"""Prepare a new disabled tool; never edit either qualified/active predecessor."""
from pathlib import Path
import hashlib,json,shutil
root=Path(__file__).resolve().parent
old=root.parent/'product67-filter-20261016'
tool=root/'tool'
assert not tool.exists(),'never overwrite a qualification tree'
declaration=json.loads((root/'DECLARATION.json').read_text())
shutil.copytree(old/'tool/src',tool/'src')
for name in ['Cargo.toml','Cargo.lock']:shutil.copyfile(old/'tool'/name,tool/name)
def exact(source,before,after):
    assert source.count(before)==1,(before,source.count(before))
    return source.replace(before,after)
p=tool/'src/packed_body.rs';source=p.read_text()
source=exact(source,'include!("masks.rs");','include!("masks.rs");\ninclude!("guard.rs");')
source=exact(source,'268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d',declaration['candidate_stream'])
source=exact(source,'assert_eq!(n,17_891_821)','assert_eq!(n,17_898_400)')
source=exact(source,'let(nq,nb)=(nq as usize,nb as usize);','let(nq,nb)=(nq as usize,nb as usize);assert_eq!((nq,nb),(1234,66245));')
# The predecessor returned provisional original-source witnesses directly.
source=exact(source,'let known=known_masks(points);','let known=known_masks(points);')
before='points.iter().enumerate().map(|(index,(_,_,expected))|'
source=exact(source,before,'let original_wrong=points.iter().enumerate().map(|(index,(_,_,expected))|')
source=exact(source,';}}wrong}).collect()',';}}wrong}).collect::<Vec<_>>();\n let proposed=points.iter().zip(&original_wrong).filter_map(|(p,b)|(*b).then_some(*p)).collect::<Vec<_>>();let safe=guard_safe(&proposed);let mut next=safe.into_iter();original_wrong.into_iter().map(|b|b&&next.next().unwrap()).collect()')
# Original zero-MR function shadow must retain its original source premise.
source=exact(source,'let shadow=std::env::var_os("PACKED_ZERO_SHADOW").is_some();','let shadow=std::env::var_os("PACKED_ZERO_SHADOW").is_some();let original=if shadow||std::env::var_os("FIXED_TRANSFER_SHADOW").is_some(){let path="/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin";sha_check(path,"2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e");let old=load_ops(path).unwrap();let(oq,ob,_,oldregs)=analyze_ops(old.iter());assert_eq!((oq,ob),(1234,45701));assert_eq!(oldregs,regs);Some(old)}else{None};if std::env::var_os("FIXED_TRANSFER_SHADOW").is_some(){validate_fixed_transfer(&program,original.as_ref().unwrap(),&ops,&regs,nq,nb);}')
source=exact(source,'shadow.then_some(ops.as_slice())','if shadow{Some(original.as_ref().unwrap().as_slice())}else{None}')
source=exact(source,'let(kind,early_shots)=exact_early(&full,packet,&regs,nq,nb,&curve);','let(kind,early_shots)=exact_early(&full,packet,&regs,nq,nb,&curve);if std::env::var_os("FORCE_FULL_FALLBACK").is_some(){let reference=protected_fallback_kind(&ops[..n-TAIL],&mut packet.packet,&regs,nq,nb,&curve);assert_eq!((kind,early_shots),reference);eprintln!("FORCED_SCHEDULER_PROTECTED_KIND_PASS nonce={} kind={kind} shots={early_shots}",packet.nonce);}')
assert 'const PROOF_ACCEPTED:bool=false;' in source
p.write_text(source)
shutil.copyfile(root/'guard.rs',tool/'src/guard.rs')
# Universal cache equivalence is relative to A29, not original2a.
p=tool/'src/transfer.rs';source=p.read_text()
for before,after in [
 ('cache-certificate67-20261016','repair67-universal-20261016'),
 ('303a75ec86a4da8c3a4008646e1b8257768fa40e198f0b7172eeafd19408c7c6','3cb037399462d45683c9790793ed1bfbff2df2934898f38f9ffe2cd857ff4d39'),
 ('d774c492b94f1c6ca458cc42de82d6dbee90a316f7d80c9dc6ee32eb1fe5201f','0bfcc1dd3657e1c8eb6ae8ce404c1c91da22eb9c7b3622d3ad8dbfecbf12a1e3'),
 ('5914f683bb5df08d21f94d79663c6239a84715e27b2eac7e18ce1fcafaee0167','08f04e547716aca8d48856f912b6c54cff9ac64013560868281f1d25370a6f43'),
 ('original2a522394 candidate268aefe2 universal67stage perinput-bit','A29_relative1cd3457b candidate0beec42b universal67stage PLUS conditional_original2a_G0 perinput-bit')]:
    source=exact(source,before,after)
# Bind the separately prepared composite manifest. Its theorem is independently
# reviewed before launch; no manifest can change the disabled authority constant.
manifest=root/'COMPOSITE_BINDING.json';binding=json.loads(manifest.read_text())
assert binding['candidate_stream']==declaration['candidate_stream']
sha=hashlib.sha256(manifest.read_bytes()).hexdigest()
checks='\n'.join(f' sha_check("{item["path"]}","{item["sha256"]}");' for item in binding['artifacts'])
source=exact(source,'fn bind_transfer(){',f'fn bind_transfer(){{\n sha_check("{manifest}","{sha}");\n{checks}')
p.write_text(source)
highid=r'''
#[cfg(test)]mod repaired_high_classical_tests{use super::*;
 #[test]fn repaired_ids_roundtrip_protected_phase_and_MR(){
  let none=u64::MAX;
  let make=|kind,q,c,bt|Op{kind,q_control1:QubitId(none),q_control2:QubitId(none),q_target:QubitId(q),c_condition:BitId(c),c_target:BitId(bt),r_target:RegisterId(none)};
  for high in[65535,66244]{let ops=vec![make(OperationType::BitStore1,none,none,high),make(OperationType::PushCondition,none,high,none),make(OperationType::X,0,none,none),make(OperationType::PopCondition,none,none,none),make(OperationType::Hmr,0,none,high),make(OperationType::BitInvert,none,none,high)];let p=Compact::compile(&ops);assert!(p.ops.iter().any(|o|o.bt as u64==high));let mut h=Shake256::default();h.update(b"high-id-protected-control");let mut a=h.clone().finalize_xof();let mut b=h.finalize_xof();let mut reference=Simulator::new(1,66245,&mut a);let mut fast=FastSimulator::new(1,66245,&mut b);reference.apply_iter(ops.iter());fast.apply(&p);assert_eq!(reference.qubits,fast.qubits);assert_eq!(reference.bits,fast.bits);assert_eq!(reference.phase,fast.phase);drop(reference);drop(fast);let mut x=[0;64];let mut y=[0;64];XofReader::read(&mut a,&mut x);XofReader::read(&mut b,&mut y);assert_eq!(x,y);}
 }
}
'''
p=tool/'src/fast_sim_wide.rs';p.write_text(p.read_text()+highid)
pins={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in tool.rglob('*') if p.is_file()}
(root/'PREPARED_SOURCE.json').write_text(json.dumps(pins,indent=2)+'\n')
driver=(old/'run.py').read_text()
driver=exact(driver,"root.parent/'product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin'","root.parent/'product-exact-20261015/repair-to67-rank-20261016/repair-67-retained-1024-proxy.bin'")
driver=exact(driver,"['FAST_ZERO_DISPATCH','PACKED_ZERO_SHADOW','EARLY_FULLSTATE_SHADOW']","['FAST_ZERO_DISPATCH','PACKED_ZERO_SHADOW','EARLY_FULLSTATE_SHADOW','FIXED_TRANSFER_SHADOW','FORCE_FULL_FALLBACK']")
driver=exact(driver,"if full:env['EARLY_FULLSTATE_SHADOW']='1'","if full:env['EARLY_FULLSTATE_SHADOW']='1';env['FIXED_TRANSFER_SHADOW']='1'")
driver=exact(driver,'def run(name,first,count,look,fast,shadow=False,full=False):','def run(name,first,count,look,fast,shadow=False,full=False,force=False):')
driver=exact(driver,"if fast:env['FAST_ZERO_DISPATCH']='1'","if fast:env['FAST_ZERO_DISPATCH']='1'\n if force:env['FORCE_FULL_FALLBACK']='1'")
driver=exact(driver,"if full:assert 'EARLY_FULLSTATE_AND_PHYSICAL_RNG9024_PASS' in error","if force:assert error.count('FORCED_SCHEDULER_PROTECTED_KIND_PASS')==count\n if full:assert 'EARLY_FULLSTATE_AND_PHYSICAL_RNG9024_PASS' in error")
driver=exact(driver,"if full:assert 'EARLY_FULLSTATE_AND_PHYSICAL_RNG9024_PASS' in error","if full:assert 'EARLY_FULLSTATE_AND_PHYSICAL_RNG9024_PASS' in error and 'FIXED445_GUARD_CONDITIONAL_KNOWN_BITS_PASS' in error")
driver=exact(driver,'DISABLED_PRODUCT67_PIPELINE_QUALIFICATION_PASS','DISABLED_REPAIRED67_CONDITIONAL_PIPELINE_QUALIFICATION_PASS')
driver=exact(driver,'268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d',declaration['candidate_stream'])
driver=exact(driver,"for name,first,count,look in [('shadow128',1,128,128),('partial',17,11,9)]:","a,_=run('forced2-generic',1,2,1,False,force=True)\nb,_=run('forced2-threaded',1,2,1,True,force=True)\nassert a==b and all(not row['provisional_wrong_value'] for row in a)\nfor name,first,count,look in [('shadow128',1,128,128),('partial',17,11,9)]:")
(root/'run.py').write_text(driver)
print(json.dumps({'prepared_files':len(pins),'proof_accepted':False,'composite_manifest_sha256':sha}))
