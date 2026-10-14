"""Exact allocator/physical fixtures from a byte-identical original fold trace."""
from pathlib import Path
import json, sys

manifest, output = map(Path, sys.argv[1:3])
rows = json.loads(manifest.read_text())['rows']
rows = [r for r in rows if r['payload'] is not None and not r['payload'][0] and r['fin'] == 0 and not r['ttm'] and r['drop'] == 0]
assert len(rows) == 105
tables = []
for r in rows:
    q,b,nb = r['entry_state']; nq, dims_b = r['entry_dims']; assert nb == dims_b
    ints = lambda values: '&['+','.join(map(str,values))+']'
    tables.append('Context { tick:'+str(r['payload'][1])+', nq:'+str(nq)+', nb:'+str(nb)+', acc:'+ints(r['acc'])+', e:'+ints(r['e'])+', nm:'+ints(r['nm'])+', k:'+ints(r['k'])+', freeq:'+ints(q)+', freeb:'+ints(b)+' }')
head = '''//! Source-bound physical contexts; no allocation normalization or scoring.
use super::*;
use crate::circuit::{analyze_ops,Op,OperationType,BitId};
use crate::sim::Simulator;
use sha3::digest::XofReader;
#[path="product_h45_phase_kernel.rs"]mod kernel;
struct Context{tick:usize,nq:usize,nb:usize,acc:&'static[u64],e:&'static[u64],nm:&'static[u64],k:&'static[u64],freeq:&'static[u64],freeb:&'static[u64]}
'''
common = '''
fn scramble(mut z:u64)->u64 {z=(z^(z>>30)).wrapping_mul(0xbf58476d1ce4e5b9);z=(z^(z>>27)).wrapping_mul(0x94d049bb133111eb);z^(z>>31)}
struct Tape{seed:u64,at:u64}
impl XofReader for Tape{fn read(&mut self,o:&mut[u8]){assert_eq!(o.len(),8);let z=match self.seed{0=>0,1=>u64::MAX,s=>scramble(s^self.at.wrapping_mul(0x9e3779b97f4a7c15))};self.at+=1;o.copy_from_slice(&z.to_le_bytes());}}
fn prepare(){crate::point_add::clear_process_env();crate::point_add::install_skywalk_submission_recipe();std::env::set_var("EXACT_PAIR_CARRY","1");crate::point_add::leapfrog::install_recipe();}
fn reference(x:u64,e:u64,n:u64,s:u64,mw:usize)->u64{let r=n+(x&7);let low=(x&63)+e+((r&1)<<4)+(((r^(r>>1))&1)<<5);let y=((s!=0)as u64)*(low>>3&1)+2*(s>>1&1)*(low>>4&1)+4*((s&1)&(s>>1&1))*(low>>5&1);let borrow=((x&7)+e>=8)as i128;let k=r as i128+8*(y as i128-borrow);((x as i128+e as i128-((1i128<<32)+976)*k)&((1i128<<mw)-1))as u64}
fn circuit(ctx:&Context,on:bool)->(Vec<Op>,usize){
 crate::point_add::pingpong::with_phase_cap(Some(1234),||{
 let mut c=Builder::new();let all=c.alloc_qubits(ctx.nq);let bits=c.alloc_bits(ctx.nb);
 for &q in ctx.freeq{c.release_clean(all[q as usize]);}for &b in ctx.freeb{c.free_bit(bits[b as usize]);}
 assert_eq!(c.op_count(),0);let entry=c.y42_alloc_state();assert_eq!(entry,(ctx.freeq.iter().map(|&x|x as u32).collect(),ctx.freeb.iter().map(|&x|x as u32).collect(),ctx.nb as u32));assert_eq!(c.i13_dims(),(ctx.nq,ctx.nb));let active=c.active_qubits();
 let acc:Vec<_>=ctx.acc.iter().map(|&q|QubitId(q)).collect();let ids=|a:&[u64]|a.iter().map(|&q|QubitId(q)).collect::<Vec<_>>();
 let oldmode=TOFFOLI_CARRY_CLEANUP_MODE.with(|x|x.replace(on));let oldat=PAYLOAD_AT.with(|x|x.replace(Some((false,ctx.tick))));TOFFOLI_CARRY_CLEANUP_HITS.with(|x|x.set(0));
 let plan=fold_fwd_v2(&mut c,&acc,ids(ctx.e).try_into().unwrap(),ids(ctx.nm).try_into().unwrap(),QubitId(ctx.k[0]),QubitId(ctx.k[1]),0,None,false,0);
 let hits=TOFFOLI_CARRY_CLEANUP_HITS.with(|x|x.get());assert_eq!(hits,usize::from(on&&ctx.tick<=104));TOFFOLI_CARRY_CLEANUP_MODE.with(|x|x.set(oldmode));PAYLOAD_AT.with(|x|x.set(oldat));
 assert_eq!(c.active_qubits(),active);let exit=c.y42_alloc_state();let mut aq=entry.0.clone();let mut bq=exit.0.clone();aq.sort_unstable();bq.sort_unstable();assert_eq!(aq,bq,"every helper/laddder wire returns");let mut ab=entry.1.clone();let mut bb=exit.1.clone();ab.sort_unstable();bb.sort_unstable();assert_eq!(ab,bb);assert_eq!(entry.2,exit.2);assert_eq!(c.i13_dims(),(ctx.nq,ctx.nb));
 let ops=c.take_ops();eprintln!("PRODUCT_H45_ACTUAL_CONTEXT tick={} new={} plan={:?} ops={} cleanup_hits={} exactFreeSets=true score=NONE",ctx.tick,on,plan,ops.len(),hits);(ops,hits)
 })
}
fn input(ctx:&Context,base:usize,high:u64)->(Vec<u64>,Vec<u64>,Vec<u64>){
 let mut q=vec![0u64;ctx.nq];let mut b=vec![0u64;ctx.nb];let owned:std::collections::HashSet<_>=ctx.acc.iter().chain(ctx.e).chain(ctx.nm).chain(ctx.k).copied().collect();let free:std::collections::HashSet<_>=ctx.freeq.iter().copied().collect();
 for(i,v)in q.iter_mut().enumerate(){if !owned.contains(&(i as u64))&&!free.contains(&(i as u64)){*v=scramble(i as u64^0x492bc51fa9372e61);}}
 for(i,v)in b.iter_mut().enumerate(){*v=scramble(i as u64^0x84b16fed304279ac);}
 let mut expected=q.clone();for lane in 0..64{let raw=(base+lane)as u64;let x=(raw&63)|high;let e=raw>>6&7;let n=raw>>9&7;let s=raw>>12&3;let want=reference(x,e,n,s,ctx.acc.len());for(i,&id)in ctx.acc.iter().enumerate(){q[id as usize]|=(x>>i&1)<<lane;expected[id as usize]|=(want>>i&1)<<lane;}for(i,&id)in ctx.e.iter().chain(ctx.nm).chain(ctx.k).enumerate(){let v=(raw>>(i+6)&1)<<lane;q[id as usize]|=v;expected[id as usize]|=v;}}
 (q,b,expected)
}
#[test]fn product_h45_actual_context_all_low_domain_all_mr(){
 prepare();let mut proofs=0usize;let mut native=0usize;let mut admitted=0;
 for ctx in CONTEXTS{let(old,_) = circuit(ctx,false);let(new,hits)=circuit(ctx,true);if hits==0{assert_eq!(old,new,"unadmitted original lean fold remains byte identical");continue;}admitted+=1;
 let mw=ctx.acc.len();let mask=((1u64<<mw)-1)&!63;let highs=[0,mask,0xaaaaaaaaaaaaaa&mask,((1u64<<32)-1)&mask];
 for ops in [&old,&new]{for high in highs{for base in(0..1usize<<14).step_by(64){let(q,b,expected)=input(ctx,base,high);let a=kernel::audit(ops,&q,&b).unwrap_or_else(|e|panic!("tick={} base={base} high={high:#x}: {e}",ctx.tick));assert_eq!(a.qubits,expected,"actual physical integer contract");proofs+=64;
 for seed in[0,1,0x317dc09ae426f5b8]{let mut tape=Tape{seed,at:0};let mut sim=Simulator::new(ctx.nq,ctx.nb,&mut tape);sim.qubits.clone_from(&q);sim.bits.clone_from(&b);sim.phase=0x83fe629a4057d1bc;sim.apply_iter(ops.iter());assert_eq!(sim.qubits,expected);assert_eq!(sim.phase,0x83fe629a4057d1bc);for i in 0..ctx.nb{if !ctx.freeb.contains(&(i as u64)){assert_eq!(sim.bits[i],b[i],"live classical slot{i}");}}native+=64;}
 }}}
 eprintln!("PRODUCT_H45_ACTUAL_PROVED tick={} actual_ids_pooldims=true low_domain=16384 highs=4 allMR=true allq_liveclass_phase=true",ctx.tick);
 }
 assert_eq!(admitted,104);eprintln!("PRODUCT_H45_ACTUAL_TOTAL admitted={admitted} fixed_input_allMR_proofs={proofs} native_cases={native} score=NONE");
}
'''
output.write_text(head+'const CONTEXTS:&[Context]=&[\n'+',\n'.join(tables)+'\n];\n'+common,newline='\n')
source = output.parent/'y15_guarded.rs'
if source.exists():
    (output.parent/'y15_actual_context.rs').write_text(source.read_text()+'\n#[cfg(test)]\n#[path="product_h45_actual_context_tests.rs"]mod product_h45_actual_context_tests;\n',newline='\n')
