from pathlib import Path
import hashlib, shutil

root=Path(__file__).resolve().parent
old=root.parent/'prefilter-20261015'
tool=root/'tool'
(tool/'src').mkdir(parents=True,exist_ok=True)
for name in ['Cargo.toml','Cargo.lock']:
 shutil.copyfile(old/'tool'/name,tool/name)
for name in ['official.rs','fast_curve_c.rs','fast_sim_wide.rs','rail_advisory.rs','simd_screen_ffi_wide.rs','rail_fast_ffi.rs']:
 shutil.copyfile(old/'tool/src'/name,tool/'src'/name)
source=(old/'tool/src/bin/bucket_fast_wide_screen.rs').read_text().replace('../','')
(tool/'src/main.rs').write_text(source)
body=(old/'tool/src/bucket_fast_screen_body.rs').read_text()
body=body.replace('fn exact_batch(', 'fn original_batch(',1)
insertion=r'''
include!("value_program.rs");
fn exact_batch(p:&Compact,packets:&[Packet],indices:[usize;8],active:[bool;8],regs:&[Vec<QubitOrBit>],nq:usize,nb:usize,rng:&[u64])->[&'static str;8]{
 let mut q=vec![0u64;nq*8];let mut b=vec![0u64;nb*8];let mut stack=vec![0u64;4096*8];let mut used=0;
 for j in 0..8{if !active[j]{continue;}for(lane,(t,o,_))in packets[j].batches[indices[j]].iter().enumerate(){for(reg,value)in regs[..4].iter().zip([t.0,t.1,o.0,o.1]){for(i,wire)in reg.iter().enumerate(){let v=(value.bit(i)as u64)<<lane;match wire{QubitOrBit::Qubit(id)=>q[id.0 as usize*8+j]|=v,QubitOrBit::Bit(id)=>b[id.0 as usize*8+j]|=v}}}}}
 let shadow=std::env::var_os("VALUE_SHADOW").is_some();let initial=shadow.then(||(q.clone(),b.clone()));
 let vp=value_program();assert_eq!(vp.rng_count,p.rng_count);
 assert_eq!(unsafe{(value_backend())(vp.ops.as_ptr(),vp.ops.len(),q.as_mut_ptr(),b.as_mut_ptr(),rng.as_ptr(),vp.rng_count,stack.as_mut_ptr(),4096,&mut used)},0);assert_eq!(used,p.rng_count);
 if let Some((mut oq,mut ob))=initial{let mut phase=[0u64;8];let mut ous=0;assert_eq!(unsafe{(exact_backend().run)(p.ops.as_ptr(),p.ops.len(),oq.as_mut_ptr(),ob.as_mut_ptr(),phase.as_mut_ptr(),rng.as_ptr(),p.rng_count,stack.as_mut_ptr(),4096,&mut ous)},0);assert_eq!(ous,used);for(i,(x,y))in oq.iter().zip(&q).enumerate(){assert_eq!(x,y,"quantum word{i} differs");}for(i,(x,y))in ob.iter().zip(&b).enumerate(){assert_eq!(x,y,"classical word{i} differs");}}
 let mut result=["inactive";8];let mut fallback=[false;8];
 for j in 0..8{if !active[j]{continue;}let mut wrong=false;for(lane,(_,_,expected))in packets[j].batches[indices[j]].iter().enumerate(){for(reg,value)in regs[..2].iter().zip([expected.0,expected.1]){for(i,wire)in reg.iter().enumerate(){let raw=match wire{QubitOrBit::Qubit(id)=>q[id.0 as usize*8+j],QubitOrBit::Bit(id)=>b[id.0 as usize*8+j]};wrong|=((raw>>lane)&1)!=(value.bit(i)as u64);}}}if wrong{result[j]="classical";}else{fallback[j]=true;}}
 if std::env::var_os("VALUE_SHADOW").is_some(){let expected=original_batch(p,packets,indices,active,regs,nq,nb,rng);for j in 0..8{if result[j]=="classical"{assert_eq!(expected[j],"classical","certified value rejection differs from original");}}}
 if fallback.iter().any(|x|*x){let full=original_batch(p,packets,indices,fallback,regs,nq,nb,rng);for j in 0..8{if fallback[j]{result[j]=full[j];}}}
 result
}
'''
body=insertion+body
body=body.replace('let p=Compact::compile(&ops[..n-TAIL]);','bind_value_source(&a[1],&regs);let p=Compact::compile(&ops[..n-TAIL]);value_program();',1)
body=body.replace('"rejection_policy":"exact_full_state_only"','"rejection_policy":"certified_value_or_original_full_state"')
(tool/'src/bucket_fast_screen_body.rs').write_text(body)
shutil.copyfile(root/'value_program.rs',tool/'src/value_program.rs')
shutil.copyfile(old/'simd8wide.h',root/'simd8wide.h')
c=(old/'simd8wide.c').read_text()
c=c.replace('int simd8_run(', 'int value8_run(').replace(' uint64_t *phase,const uint64_t *rng,',' const uint64_t *rng,')
c=c.replace('V ph=ld(phase,0),base=', 'V base=')
c=c.replace('case 0:ph=XOR(ph,c);break;', 'case 0:case 7:case 9:case 14:break;\n   case 18:if(ri>=nr)return 1;ri++;break;')
c=c.replace('   case 7:ph=XOR(ph,AND(c,ld(q,o.t)));break;\n','')
c=c.replace('   case 9:ph=XOR(ph,AND(c,AND(ld(q,o.a),ld(q,o.t))));break;\n','')
c=c.replace('    ph=XOR(ph,AND(c,AND(x,w)));st(q,o.t,ANDNOT(c,x));','    st(q,o.t,ANDNOT(c,x));')
c=c.replace('   case 14:ph=XOR(ph,AND(c,AND(ld(q,o.t),AND(ld(q,o.a),ld(q,o.b)))));break;\n','')
c=c.replace(' st(phase,0,ph);*used=ri;', ' *used=ri;')
c=c.replace('#include "simd8wide.h"','#include "simd8wide.h"')
# Original header declares a different exported function; the new ABI is local.
(root/'value8.c').write_text(c)
print('Prepared isolated exact value screen; source and reduced IR bindings enforced at startup')
