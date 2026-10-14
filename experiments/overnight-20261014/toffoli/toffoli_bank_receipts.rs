//! Native component streams and complete payload-body allocation ledger.
use super::*;
use std::path::PathBuf;

fn save(mut c:Builder,name:&str) {
    let ops=c.take_ops();
    let path=PathBuf::from(std::env::var("TOFFOLI_STREAM_DIR").unwrap()).join(format!("{name}.bin"));
    crate::write_ops(&ops,&path).unwrap();
    eprintln!("TOFFOLI_STREAM name={name} ops={}",ops.len());
}

#[test]
fn toffoli_bank_stream_receipts() {
    for room in [10,12,14,16,18,22,26,31,36,45,50] {
        for on in [false,true] {
            let mut c=Builder::new();
            let acc=c.alloc_qubits(56);
            let e:[QubitId;3]=c.alloc_qubits(3).try_into().unwrap();
            let nm:[QubitId;3]=c.alloc_qubits(3).try_into().unwrap();
            let shift:[QubitId;2]=c.alloc_qubits(2).try_into().unwrap();
            c.alloc_qubits(cells::cap()-(56+8+31+room));
            toffoli_bank_loan::with_mode(on,||fold_fwd_v2(&mut c,&acc,e,nm,shift[0],shift[1],0,None,false,0));
            save(c,&format!("fold-room{room}-bank{on}"));
        }
    }
    for (width,fin) in [(56,0),(57,1),(56,2)] {
        for on in [false,true] {
            if on && fin!=0 {continue;}
            let mut c=Builder::new();
            let acc=c.alloc_qubits(width);
            let e:[QubitId;3]=c.alloc_qubits(3).try_into().unwrap();
            let nm:[QubitId;3]=c.alloc_qubits(3).try_into().unwrap();
            let shift:[QubitId;2]=c.alloc_qubits(2).try_into().unwrap();
            toffoli_bank_loan::with_mode(on,||fold_fwd_v2(&mut c,&acc,e,nm,shift[0],shift[1],fin,None,false,0));
            save(c,&format!("fold-roomy-width{width}-fin{fin}-bank{on}"));
        }
    }
}

#[test]
fn toffoli_bank_body_ledger() {
    // Native builder means are diagnostics only. No correctness or record claim.
    for room in [90,100,120,160,240] {
        for t in [30,60,85,90,100,110,120,127,128,137,145] {
            for on in [false,true] {
                let mut c=Builder::new();
                let b=c.alloc_qubits(N);let tg=c.alloc_qubits(N);
                let letter=c.alloc_qubits(5);
                c.alloc_qubits(cells::cap()-(2*N+5+room));
                let (e0,a0)=(c.expected_total(),c.active_qubits());
                let (_,proxy)=proxy_fold(steps()[t][0],false);
                let shift=cmp_shift_at(t);
                let (_,peak)=c.r3_peak(|c|toffoli_bank_loan::with_mode(on,||toffoli_bank_loan::with_head_plan(on,||
                    cells::with_tie(None,||cells::with_cmp_shift((shift.0+Y15_CMP_EXTRA+super::n2_cmpx(),shift.1),||
                        cells::with_bridge(proxy,false,||body(c,t,[letter[0],letter[1],letter[2]],letter[3],letter[4],&b,&tg,proxy,false)))))));
                assert_eq!(a0,c.active_qubits(),"payload body scratch");
                eprintln!("TOFFOLI_BODY_LEDGER room={room} tick={t} bank={on} diagnostic_mean={} peak={peak}",c.expected_total()-e0);
                save(c,&format!("body-room{room}-tick{t}-bank{on}"));
            }
        }
    }
}
