"""Add exact under-condition absorption/disjointness proof rules."""
from pathlib import Path
import sys
source=Path(sys.argv[1])
p=source/'truth7_simplify.rs'
t=p.read_text()
old='''                let rewrite = Self::ccx_rewrite(&condition, &a, &b, op);
                let product = self.and(&a, &b);
                let toggle = self.and(&condition, &product);'''
new='''                let product = self.and(&a, &b);
                let toggle = self.and(&condition, &product);
                // Equality is of whole immutable Boolean functions. Failed
                // support unions become distinct fresh atoms, losing proofs.
                // Compare the actual conditional toggle, retaining the exact
                // original classical condition and stack in every replacement.
                let rewrite = if toggle.is_zero() {
                    Rewrite::Drop
                } else if toggle == condition {
                    Rewrite::X
                } else if toggle == self.and(&condition, &a) {
                    Rewrite::Cx(op.q_control1)
                } else if toggle == self.and(&condition, &b) {
                    Rewrite::Cx(op.q_control2)
                } else {
                    Self::ccx_rewrite(&condition, &a, &b, op)
                };'''
assert t.count(old)==1
p.write_text(t.replace(old,new),newline='\n')
print('exact conditional toggle absorption installed')
