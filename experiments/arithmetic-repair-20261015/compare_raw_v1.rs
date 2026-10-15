// Byte-locality certificate and event-aligned diagnostic pairing; no score.
struct Words { values: Vec<u64>, at: usize }
impl XofReader for Words { fn read(&mut self,out:&mut[u8]) { assert_eq!(out.len(),8);out.copy_from_slice(&self.values[self.at].to_le_bytes());self.at+=1; } }
fn is_mr(o:&Op)->bool{matches!(o.kind,OperationType::R|OperationType::Hmr)}
fn main(){
    let root="/home/hclau/ecdsa_research/arithmetic-repair-20261015";
    let old=load_ops(&format!("{root}/diagnostic-b3/ops.bin")).unwrap();
    let new=load_ops(&format!("{root}/diagnostic-fold104-b3/ops.bin")).unwrap();
    let prefix=old.iter().zip(&new).take_while(|(a,b)|a==b).count();
    let suffix=old[prefix..].iter().rev().zip(new[prefix..].iter().rev()).take_while(|(a,b)|a==b).count();
    let old_end=old.len()-suffix;let new_end=new.len()-suffix;
    let mpre=old[..prefix].iter().filter(|o|is_mr(o)).count();
    let mold=old[prefix..old_end].iter().filter(|o|is_mr(o)).count();
    let mnew=new[prefix..new_end].iter().filter(|o|is_mr(o)).count();
    let msuffix=old[old_end..].iter().filter(|o|is_mr(o)).count();
    println!("RAW_LOCALITY prefix={prefix} old_end={old_end} new_end={new_end} suffix={suffix} added_ops={} old_span_mr={mold} new_span_mr={mnew} all_outside_ops_identical=true",new.len() as i64-old.len() as i64);
    assert!(prefix>0&&suffix>0);assert_eq!(new.len(),old.len()+201);
    let(nq,nb,_,regs)=analyze_ops(old.iter());let(rq,rb,_,rregs)=analyze_ops(new.iter());assert_eq!((nq,nb,&regs),(rq,rb,&rregs));
    for family in ["independent","structured","candidate"]{
        let text=std::fs::read_to_string(format!("{root}/packets/{family}.tsv")).unwrap();
        let rows:Vec<[U256;6]>=text.lines().map(|l|l.split_whitespace().skip(1).map(|v|U256::from_str_radix(v.trim_start_matches("0x"),16).unwrap()).collect::<Vec<_>>().try_into().unwrap()).collect();
        let(mut old_bad,mut new_bad,mut introduced,mut corrected,mut phase_diff,mut dirty_old,mut dirty_new)=(0,0,0,0,0,0,0);
        for(batch,points)in rows.chunks(64).enumerate(){
            let mut h=Shake256::default();h.update(b"fold104-event-aligned-v1");h.update(family.as_bytes());h.update(&(batch as u64).to_le_bytes());let mut rng=h.finalize_xof();
            let mut draw=|n:usize|->Vec<u64>{(0..n).map(|_|{let mut b=[0u8;8];XofReader::read(&mut rng,&mut b);u64::from_le_bytes(b)}).collect()};
            let pre=draw(mpre);let lcore=draw(mold);let rcore=draw(mnew);let post=draw(msuffix);
            let mut lr=Words{values:pre.iter().chain(&lcore).chain(&post).copied().collect(),at:0};
            let mut rr=Words{values:pre.iter().chain(&rcore).chain(&post).copied().collect(),at:0};
            let mut l=Simulator::new(nq as usize,nb as usize,&mut lr);let mut r=Simulator::new(rq as usize,rb as usize,&mut rr);
            for(lane,v)in points.iter().enumerate(){for k in 0..4{l.set_register(&regs[k],v[k],lane);r.set_register(&regs[k],v[k],lane);}}
            l.apply_iter(old.iter());r.apply_iter(new.iter());let mask=if points.len()==64{u64::MAX}else{(1u64<<points.len())-1};
            phase_diff+=((l.phase^r.phase)&mask).count_ones();
            for(lane,v)in points.iter().enumerate(){
                let lb=l.get_register(&regs[0],lane)!=v[4]||l.get_register(&regs[1],lane)!=v[5];
                let rb=r.get_register(&regs[0],lane)!=v[4]||r.get_register(&regs[1],lane)!=v[5];
                old_bad+=usize::from(lb);new_bad+=usize::from(rb);introduced+=usize::from(!lb&&rb);corrected+=usize::from(lb&&!rb);
                if lb!=rb {println!("CHANGED_CORRECTNESS family={family} shot={} old_bad={lb} new_bad={rb}",batch*64+lane);}
            }
            for reg in &regs{for q in reg{if let QubitOrBit::Qubit(q)=q{*l.qubit_mut(*q)=0;*r.qubit_mut(*q)=0;}}}
            dirty_old+=usize::from(l.qubits.iter().any(|v|v&mask!=0));dirty_new+=usize::from(r.qubits.iter().any(|v|v&mask!=0));
        }
        println!("PAIRED_REPAIR family={family} shots={} old_bad={old_bad} new_bad={new_bad} corrected={corrected} introduced={introduced} phase_diff_shots={phase_diff} old_dirty_batches={dirty_old} new_dirty_batches={dirty_new} score=NONE",rows.len());
        assert_eq!(introduced,0,"new value regression on fixed packet");assert_eq!(dirty_new,0);
        if family=="independent"{assert_eq!(old_bad,1);assert_eq!(new_bad,0);assert_eq!(corrected,1);}
    }
}
