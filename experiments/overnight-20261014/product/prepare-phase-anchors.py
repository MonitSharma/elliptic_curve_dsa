"""Print existing operation windows only; emit no new operation."""
from pathlib import Path
import sys
source=Path(sys.argv[1]);target=Path(sys.argv[2]);t=source.read_text()
needle='    fn report_phase(&mut self) {\n'
new='''    fn report_phase(&mut self) {
        if self.report.is_some() {
            let end = self.ops.len();
            for (j, o) in self.ops[end.saturating_sub(100)..].iter().enumerate() {
                let at = end.saturating_sub(100) + j;
                eprintln!("PHASE_ANCHOR {} {} {} {} {} {} {} {} {} {}", self.phase, at, end,
                    o.kind as u32, o.q_control2.0, o.q_control1.0, o.q_target.0,
                    o.c_target.0, o.c_condition.0, o.r_target.0);
            }
        }
'''
assert t.count(needle)==1
target.write_text(t.replace(needle,new),newline='\n')
