//! Resource-only original-body trace; extended primitive producer admission separate.
use super::*;
#[test]
fn toffoli_carry_recipe_trace_v1() {
    let mut completed=0;let mut failed=0;
    for room in [70,74,78,82,86,90,94,100,110,120,140,160,200,240] {
        for tick in 128..137 {
            let result=std::panic::catch_unwind(|| {
                let mut c=Builder::new();let b=c.alloc_qubits(N);let tg=c.alloc_qubits(N);
                let letter=c.alloc_qubits(5);let _pads=c.alloc_qubits(cells::cap()-(2*N+5+room));
                let active=c.active_qubits();let (_,proxy)=proxy_fold(steps()[tick][0],false);let shift=cmp_shift_at(tick);
                cells::with_tie(None,||cells::with_cmp_shift((shift.0+Y15_CMP_EXTRA+super::n2_cmpx(),shift.1),||
                    cells::with_bridge(proxy,false,||body_capped(&mut c,tick,[letter[0],letter[1],letter[2]],letter[3],letter[4],&b,&tg,proxy,false))));
                assert_eq!(c.active_qubits(),active);
                eprintln!("TOFFOLI_CARRY_RECIPE room={room} tick={tick} emitted_ops={} expected={}",c.op_count(),c.expected_total());
            });
            if result.is_ok() {completed+=1;} else {failed+=1;eprintln!("TOFFOLI_CARRY_RECIPE_FAILED room={room} tick={tick}");}
        }
    }
    eprintln!("TOFFOLI_CARRY_RECIPE_SUMMARY contexts=126 completed={completed} failed={failed} resource_only=true");
    assert_eq!(completed+failed,126);
}
