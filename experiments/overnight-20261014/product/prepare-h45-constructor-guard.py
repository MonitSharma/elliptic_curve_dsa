"""Derive extra-loan admission from the unchanged constructor's actual plan."""
from pathlib import Path
import sys

p, out = map(Path, sys.argv[1:3])
s = p.read_text()
old = '''    // Parameter-only extension: retain the baseline nine selected loans and
    // admit only actual payload forward folds with the proved fin0 interface.
    let extra_loan=TOFFOLI_CARRY_CLEANUP_MODE.with(|x|x.get()) && fin==0 && !ttm && drop==0
        && PAYLOAD_AT.with(|x|x.get().is_some_and(|(rev,_)|!rev));
    let loan=extra_loan || PAYLOAD_AT.with(|x|x.get().is_some_and(|(rev,t)|carry_loan_selected(rev,t)));
'''
new = '''    // Preserve baseline loans. Constructor emission does not read LOAN_ACTIVE.
    // Decide the additional loan from its actual unmodified nonlean plan below.
    let extra_parameter=TOFFOLI_CARRY_CLEANUP_MODE.with(|x|x.get()) && fin==0 && !ttm && drop==0
        && PAYLOAD_AT.with(|x|x.get().is_some_and(|(rev,_)|!rev));
    let mut loan=PAYLOAD_AT.with(|x|x.get().is_some_and(|(rev,t)|carry_loan_selected(rev,t)));
'''
assert s.count(old) == 1
s = s.replace(old, new)
old = '''    let (y5_q, y3_q) = (y5.w[0], y3.w[0]);
    if loan {'''
new = '''    let (y5_q, y3_q) = (y5.w[0], y3.w[0]);
    let extra_loan=extra_parameter && !fold_plan_d(c,mw,"forward unchanged constructor admission",drop).1;
    loan |= extra_loan;
    LOAN_ACTIVE.with(|x|x.set(loan));
    if loan {'''
assert s.count(old) == 1
s = s.replace(old, new)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(s, newline='\n')
