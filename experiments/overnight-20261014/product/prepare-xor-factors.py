"""Use a*!b=a XOR a*b; preserve all classical bits and snapshots."""
from pathlib import Path
import sys
s=Path(sys.argv[1]);t=(s/'classical_factors.rs').read_text()
start=t.index('   let bit=if negated{');end=t.index('   let mut push=Op::empty();',start)
t=t[:start]+'''   // a*!b = a XOR (a*b): two CX gates, no classical mutation.
   // Both carry the original per-op condition and the unchanged outer stack.
   if negated {
    let mut base=Op::empty();base.kind=OperationType::CX;base.q_control1=other;base.q_target=o.q_target;base.c_condition=o.c_condition;base.validate();
    out.push(base);complement_hits+=1;
   }
   let bit=crate::circuit::BitId(b as u64);
'''+t[end:]
t=t.replace('let mut fresh_bit=state.bits.len() as u64;','')
t=t.replace('CLASSICAL_FACTORS native_hits','CLASSICAL_XOR_FACTORS native_hits')
(s/'classical_factors_xor.rs').write_text(t,newline='\n')
