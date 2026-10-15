"""Independent packed full-state comparison, using unchanged old and new routines."""
from pathlib import Path
import hashlib,json,sys,shutil
old,new,lib,dest=map(Path,sys.argv[1:5]);(dest/'src').mkdir(parents=True,exist_ok=False)
tree=dest/'source/point_add';shutil.copytree(new/'src/point_add',tree)
old_midg=(old/'src/point_add/midg.rs').read_text(encoding='utf8')
reference=''
for name in ['stage1_v_compact_partitioned','stage1_v_compact_bank_partition','inc_with_controls']:
 start=old_midg.index('pub(crate) fn '+name+'(') if name!='inc_with_controls' else old_midg.index('fn '+name+'(')
 brace=old_midg.index('{',start);depth=1;end=brace+1
 while depth:
  if old_midg[end]=='{':depth+=1
  elif old_midg[end]=='}':depth-=1
  end+=1
 reference+='\n'+old_midg[start:end].replace('fn '+name+'(','fn reference_'+name+'(').replace('inc_with_controls(', 'reference_inc_with_controls(')
reference=reference.replace('reference_reference_inc_with_controls(', 'reference_inc_with_controls(')
p=tree/'midg.rs';p.write_text(p.read_text(encoding='utf8')+'\n'+reference,encoding='utf8')
(dest/'Cargo.toml').write_text('[package]\nname="q692_differential"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nquantum_ecc={path='+json.dumps(lib.as_posix())+'}\nalloy-primitives="1.5"\nruint="1.12"\nsha3="0.10"\nzstd="0.13"\n',encoding='utf8')
program=r'''
use quantum_ecc::{circuit,sim,weierstrass_elliptic_curve};
use circuit::{QubitId,Op,OperationType as K};
#[allow(dead_code)]#[path="PRIVATE/mod.rs"]mod point_add;
fn zstd_level()->i32{3}
fn apply(ops:&[Op],q:&mut[u64]){
 for op in ops{let a=op.q_control1.0 as usize;let c=op.q_control2.0 as usize;let t=op.q_target.0 as usize;
  match op.kind{K::X=>q[t]^=!0,K::CX=>q[t]^=q[a],K::CCX=>q[t]^=q[a]&q[c],K::Swap=>q.swap(a,t),_=>panic!("unexpected non-unitary/phase operation {:?}",op.kind)}
 }
}
fn rng(s:&mut u64)->u64{*s^=*s<<13;*s^=*s>>7;*s^=*s<<17;*s}
fn build_old(bank:bool,partitioned:bool)->(Vec<Op>,Vec<Op>){
 let mut b=frozen::builder::B::new();let ring=b.alloc_n(275);let q=b.alloc_n(128);let sy=b.alloc_n(8);let sx=b.alloc_n(8);let _ph=b.alloc();let pool=b.alloc_n(13);let dirty=b.alloc_n(259);
 let mut r=ring[..18].to_vec();r.extend(&sx[1..6]);r.push(ring[274]);if bank{r.extend(&q[120..128]);}
 let k=r.len();let s=frozen::midg::S1{r,f:sx[0],zero:ring[17],sgn:sx[0],gt:vec![sx[0]],anc:vec![],andc:vec![],chain:vec![],dirty};
 let rec=if partitioned{frozen::midg::stage1_v_compact_partitioned(&mut b,&ring[275-k..275],&ring[17..44],&pool[..8],(65,256),&s,pool[12],true,&sy,bank)}else{frozen::midg::stage1_v_compact_bank_partition(&mut b,&ring[275-k..275],&ring[17..44],&pool[..8],(65,256),&s,pool[12],true,&sy,bank,bank)};
 b.play(&rec,false);let f=std::mem::take(&mut b.ops);b.play(&rec,true);(f,b.ops)
}
fn build_new(bank:bool,partitioned:bool)->(Vec<Op>,Vec<Op>){
 let mut b=point_add::builder::B::new();let ring=b.alloc_n(275);let q=b.alloc_n(128);let sy=b.alloc_n(8);let sx=b.alloc_n(8);let _ph=b.alloc();let pool=b.alloc_n(13);let dirty=b.alloc_n(259);
 let mut r=ring[..18].to_vec();r.extend(&sx[1..6]);r.push(ring[274]);if bank{r.extend(&q[120..128]);}
 let k=r.len();let s=point_add::midg::S1{r,f:sx[0],zero:ring[17],sgn:sx[0],gt:vec![sx[0]],anc:vec![],andc:vec![],chain:vec![],dirty};
 let rec=if partitioned{point_add::midg::stage1_v_compact_partitioned(&mut b,&ring[275-k..275],&ring[17..44],&pool[..8],(65,256),&s,pool[12],true,&sy,bank)}else{point_add::midg::stage1_v_compact_bank_partition(&mut b,&ring[275-k..275],&ring[17..44],&pool[..8],(65,256),&s,pool[12],true,&sy,bank,bank)};
 b.play(&rec,false);let f=std::mem::take(&mut b.ops);b.play(&rec,true);(f,b.ops)
}
fn main(){
 assert!(std::env::var_os("LOWQ_EXACT_STREAM_PATH").is_none());
 let mut total=0usize;let mut seed=0x692a5a5af00du64;
 for partitioned in [false,true]{for bank in [false,true]{
  let(old,_oldinv)=build_old(bank,partitioned);let(new,inv)=build_new(bank,partitioned);
  for sy in 0..256usize {for size_group in 0..4usize {for act in [false,true] {
   let mut input:Vec<u64>=(0..692).map(|_|rng(&mut seed)).collect();
   input[411]=0; // SX0 is returned clean by every preceding restoring step.
   for i in 0..8 {input[403+i]=if sy>>i&1!=0{!0}else{0};input[420+i]=0;}
   for lane in 0..64 {let sz=size_group*64+lane;for i in 0..8{input[420+i]|=(((sz>>i)&1)as u64)<<lane;}}
   input[432]=if act{!0}else{0};
   let mut a=input.clone();let mut b=input.clone();apply(&old,&mut a);apply(&new,&mut b);
   assert_eq!(a,b,"entire state sy={sy} sizes={size_group} act={act} bank={bank} partitioned={partitioned}");
   assert_eq!(b[411],0,"flag restored");apply(&inv,&mut b);assert_eq!(b,input,"inverse state");total+=64;
  }}}
  println!("DIFFERENTIAL_CASE_PASS bank={bank} partitioned={partitioned} old_ops={} new_ops={} all_sy_256=true all_sz_256=true both_act=true dirty_arbitrary=true inverse=true phase=unitary_X_CX_CCX_SWAP",old.len(),new.len());
 }}
 println!("DIFFERENTIAL_PASS cases={total}");
}
'''.replace('frozen::','point_add::').replace('point_add::midg::stage1_v_compact_partitioned(&mut b', 'point_add::midg::stage1_v_compact_partitioned(&mut b')
old_start=program.index('fn build_old(');old_end=program.index('fn build_new(',old_start)
program=program[:old_start]+program[old_start:old_end].replace('::stage1_v_compact_partitioned(', '::reference_stage1_v_compact_partitioned(').replace('::stage1_v_compact_bank_partition(', '::reference_stage1_v_compact_bank_partition(')+program[old_end:]
program=program.replace('PRIVATE',tree.as_posix())
(dest/'src/main.rs').write_text(program,encoding='utf8')
(dest/'source-binding.json').write_text(json.dumps({name:{p.relative_to(source).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((source/'src/point_add').rglob('*'))if p.is_file()}for name,source in [('old',old),('new',new)]},indent=2)+'\n',encoding='utf8')
