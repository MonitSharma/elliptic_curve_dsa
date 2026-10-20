
#[cfg(test)]mod core_rank_audit_tests{
    use super::*;use crate::circuit::{analyze_ops,OperationType};use crate::sim::Simulator;
    use sha3::{Shake256,digest::ExtendableOutput};
    #[test]fn export_actual_eight_input_fold_core_truth_tables(){
        let mut c=Builder::new();let source=c.alloc_qubits(8);c.declare_qubit_register(&source);
        let input:Vec<_>=source.iter().map(|&q|l(q)).collect();let mut records=Vec::new();let output=addend_from_n(&mut c,&mut records,&input,54);
        let ops=c.take_ops();let(nq,nb,_,_)=analyze_ops(ops.iter());assert!(!ops.iter().any(|o|matches!(o.kind,OperationType::Hmr|OperationType::R)));
        let mut truth=vec![Vec::new();nq as usize];let mut outside_mismatches=Vec::new();let mut supported=0;
        for base in[0usize,64,128,192]{let mut random=Shake256::default().finalize_xof();let mut s=Simulator::new(nq as usize,nb as usize,&mut random);
            for lane in 0..64{let value=base+lane;for i in 0..8{if value>>i&1!=0{s.qubits[source[i].0 as usize]|=1u64<<lane;}}}
            let original=s.qubits.clone();s.apply_iter(ops.iter());assert_eq!(s.phase,0);for i in 0..8{assert_eq!(s.qubits[source[i].0 as usize],original[source[i].0 as usize]);}
            for lane in 0..64{let value=base+lane;let signed=if value>=128{value as i128-256}else{value as i128};
                let wanted=(signed*((1i128<<32)+976)&((1i128<<54)-1))as u64;
                let got=output.iter().enumerate().fold(0u64,|v,(i,a)|{let bit=a.w.iter().fold(u64::from(a.one),|b,q|b^(s.qubits[q.0 as usize]>>lane&1));v|(bit<<i)});
                if(-70..=7).contains(&signed){assert_eq!(got,wanted,"supported n={signed}");supported+=1;}else if got!=wanted{outside_mismatches.push(signed);}}
            for(i,&word)in s.qubits.iter().enumerate(){truth[i].push(word);}
        }
        assert_eq!(supported,78);
        let forms=output.iter().map(|a|format!("{{\"wires\":{:?},\"one\":{}}}",a.w.iter().map(|q|q.0).collect::<Vec<_>>(),a.one)).collect::<Vec<_>>().join(",");
        let data=format!("{{\"source_qubits\":{:?},\"qubit_truth_words\":{:?},\"output_forms\":[{}],\"emitted_ccx\":{},\"held_records\":{},\"supported_signed_inputs_verified\":{},\"outside_promised_range_math_mismatches\":{:?},\"scope\":\"Actual unmodified eight-input function; only signed[-70,7] promised. No runtime circuit change.\"}}",source.iter().map(|q|q.0).collect::<Vec<_>>(),truth,forms,ops.iter().filter(|o|o.kind==OperationType::CCX).count(),records.len(),supported,outside_mismatches);
        std::fs::write("../CORE-TRUTH.json",data).unwrap();
    }
}
