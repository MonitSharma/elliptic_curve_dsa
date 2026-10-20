
#[cfg(test)]mod weighted_plan_tests{
    use super::*;
    use crate::point_add::phase_plan::{self,Plan};
    use crate::circuit::{analyze_ops,Op,OperationType};
    use crate::sim::Simulator;
    use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
    struct Words{data:Vec<u8>,pos:usize}
    impl XofReader for Words{fn read(&mut self,b:&mut[u8]){let end=self.pos+b.len();assert!(end<=self.data.len());b.copy_from_slice(&self.data[self.pos..end]);self.pos=end;}}
    fn draws(ops:&[Op])->usize{ops.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).count()}
    fn execute(c:&mut Builder,acc:&[QubitId],add:&[Lin],lo0:usize,cin0:QubitId,plan:&Plan){
        let(mut lo,mut cin)=(lo0,cin0);let mut kept=Vec::new();
        for(j,chunk)in plan.chunks.iter().enumerate(){let hi=lo+chunk.width;let last=j+1==plan.chunks.len();
            let out=if chunk.drops.is_empty(){ladder_chunk(c,acc,add,lo,chunk.width,cin,last)}else{
                let out=if last{None}else{Some(c.alloc_qubit())};let mut target=acc[lo..hi].to_vec();target.extend(out);
                let mut rows:Vec<_>=add[lo..hi].iter().map(|v|v.w.clone()).collect();let mut ones:Vec<_>=add[lo..hi].iter().map(|v|v.one).collect();
                if !last{rows.push(Vec::new());ones.push(false);}
                assert!(crate::point_add::phase_pebble::add(c,&target,&rows,&ones,cin,&chunk.drops));out
            };
            if let Some(out)=out{kept.push((lo,hi,cin,out));cin=out;}lo=hi;
        }
        assert_eq!(lo,acc.len());
        for(lo,hi,cin,out)in kept.into_iter().rev(){kept_erase(c,acc,add,lo,hi,cin,out);}
    }
    fn fixture(pattern:usize,budget:usize,old:bool,inverse:bool,probe:Option<usize>){
        let mut b=Builder::new();let source=b.alloc_qubits(56);let target=b.alloc_qubits(56);let ci=b.alloc_qubit();let sign=b.alloc_qubit();
        let interface:Vec<_>=source.iter().chain(&target).copied().chain([ci,sign]).collect();b.declare_qubit_register(&interface);
        let mut recs=Vec::new();let add:Vec<Lin>=if pattern==2{addend_from_n(&mut b,&mut recs,&source[..8].iter().map(|&q|l(q)).collect::<Vec<_>>(),56)}else{source.iter().enumerate().map(|(i,&q)|{
            let mut v=if pattern==1{l(sign)}else{l(q)};if pattern==0&&i%3==0{v=v.x(&l(sign));}if i%5==0{v=v.x(&Lin::k(true));}v
        }).collect()};
        let core=b.take_ops();let rows:Vec<_>=add[6..].iter().map(|v|v.w.clone()).collect();let plan=phase_plan::choose(&rows,budget).unwrap();
        let active=b.active_qubits();let((),peak)=b.r3_peak(|b|{
            let run=|b:&mut Builder|{if old{let(p,d)=if budget==8{(&Y28_PLAN8.0[..],&Y28_PLAN8.1[..])}else{(&Y28_PLAN9.0[..],&Y28_PLAN9.1[..])};ladder_drop(b,&target,&add,6,ci,p,d);}else{execute(b,&target,&add,6,ci,&plan);}};
            run(b);if inverse{b.x_all(&target[6..]);run(b);b.x_all(&target[6..]);}
        });
        assert!(peak<=active+budget as u32,"pattern={pattern} budget={budget} old={old} peak={} plan={plan:?}",peak-active);
        let ops=b.take_ops();let all:Vec<_>=core.iter().chain(&ops).collect();let(nq,nb,_,_)=analyze_ops(all.into_iter());let nr=draws(&ops);let core_nr=draws(&core);
        let ccx=ops.iter().filter(|o|o.kind==OperationType::CCX).count();let ccz=ops.iter().filter(|o|o.kind==OperationType::CCZ).count();
        eprintln!("WEIGHTED_COMPONENT pattern={pattern} budget={budget} old={old} inverse={inverse} peak_extra={} ccx={ccx} ccz={ccz} rng={nr} model_extra_x2={} plan={:?}",peak-active,plan.extra_x2,plan.chunks);
        let count=if probe.is_some(){64}else{65536};let mut input_hash=Shake256::default();input_hash.update(b"weighted-phase-chunks-native-v1");let mut input=input_hash.finalize_xof();let mut executed=0u64;
        for first in(0..count).step_by(64){
            let mut data=vec![0u8;(core_nr+nr)*8];for j in 0..core_nr+nr{let word=if j<core_nr{0}else{match probe{Some(p)=>if p==j-core_nr||p==nr{u64::MAX}else{0},None=>0xD1B54A32D192ED03u64.wrapping_mul((first+j+1)as u64).rotate_left(j as u32)}};data[j*8..j*8+8].copy_from_slice(&word.to_le_bytes());}
            let mut random=Words{data,pos:0};let mut s=Simulator::new(nq as usize,nb as usize,&mut random);
            for &q in &interface{let mut bytes=[0u8;8];input.read(&mut bytes);s.qubits[q.0 as usize]=u64::from_le_bytes(bytes);}
            s.apply_iter(core.iter());let original=s.qubits.clone();let mut expected=vec![0u64;56];
            for lane in 0..64{let mut a=0u64;let mut t=0u64;for i in 0..56{let x=add[i].w.iter().fold(u64::from(add[i].one),|v,q|v^(s.qubits[q.0 as usize]>>lane&1));a|=x<<i;t|=(s.qubits[target[i].0 as usize]>>lane&1)<<i;}
                let sum=if inverse{t}else{(((t>>6)+(a>>6)+(s.qubits[ci.0 as usize]>>lane&1))&((1u64<<50)-1))<<6|(t&63)};for i in 0..56{expected[i]|=(sum>>i&1)<<lane;}}
            s.apply_iter(ops.iter());for i in 0..56{assert_eq!(s.qubits[target[i].0 as usize],expected[i],"pattern={pattern} budget={budget} old={old} inverse={inverse} first={first} bit={i}");}
            for i in 0..nq as usize{if !target.iter().any(|q|q.0 as usize==i){assert_eq!(s.qubits[i],original[i]);}}assert_eq!(s.phase,0);executed+=s.stats.toffoli_gates as u64;drop(s);assert_eq!(random.pos,(core_nr+nr)*8);
        }
        eprintln!("WEIGHTED_EXECUTED_DIAGNOSTIC pattern={pattern} budget={budget} old={old} inverse={inverse} shots={count} toffoli_total={executed}");
    }
    #[test]fn weighted_fifty_bit_plans_against_old_plans_and_actual_core_rows(){for pattern in 0..3{for budget in 8..=10{fixture(pattern,budget,false,false,None);if budget<=9{fixture(pattern,budget,true,false,None);}}}}
    #[test]fn weighted_every_measurement_coefficient_and_inverse(){for pattern in 0..3{for budget in[8,9]{for inverse in[false,true]{for probe in 0..140{fixture(pattern,budget,false,inverse,Some(probe));}}}}}
    #[test]fn uniform_rank_costs_match_independent_model(){for(rank,expected)in[(1,[52,42,38]),(2,[64,45,38])]{let rows:Vec<_>=(0..50).map(|i|vec![QubitId(if rank==1{100}else{100+i})]).collect();for(budget,&cost)in(8..=10).zip(&expected){let p=phase_plan::choose(&rows,budget).unwrap();assert_eq!(p.extra_x2,cost,"rank={rank} budget={budget}");}}}
}
