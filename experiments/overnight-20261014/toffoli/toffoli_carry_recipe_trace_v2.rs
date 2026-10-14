//! One isolated resource-only context per process, preserving plan failures.
use super::*;
#[test]
fn toffoli_carry_recipe_trace_v2() {
    let room=std::env::var("TOFFOLI_TRACE_ROOM").unwrap().parse::<usize>().unwrap();
    let tick=std::env::var("TOFFOLI_TRACE_TICK").unwrap().parse::<usize>().unwrap();
    crate::point_add::pingpong::with_phase_cap(Some(1234),|| {
        assert_eq!(cells::cap(),1234);
        let mut c=Builder::new();let b=c.alloc_qubits(N);let tg=c.alloc_qubits(N);
        let letter=c.alloc_qubits(5);let _pads=c.alloc_qubits(cells::cap()-(2*N+5+room));
        let active=c.active_qubits();let (_,proxy)=proxy_fold(steps()[tick][0],false);let shift=cmp_shift_at(tick);
        cells::with_tie(None,||cells::with_cmp_shift((shift.0+Y15_CMP_EXTRA+super::n2_cmpx(),shift.1),||
            cells::with_bridge(proxy,false,||body_capped(&mut c,tick,[letter[0],letter[1],letter[2]],letter[3],letter[4],&b,&tg,proxy,false))));
        assert_eq!(c.active_qubits(),active);
        eprintln!("TOFFOLI_CARRY_RECIPE_V2 cap=1234 room={room} tick={tick} emitted_ops={} expected={}",c.op_count(),c.expected_total());
    });
}
