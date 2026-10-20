# Restore original exact carry loan at forward128

Parent public88869 retunes the original0c3 forward loan range128..137 to129..137,
claiming about0.3T saving at1234. Lower1233/1232 budgets hit the originaly16 guard
at128: raw fold short23, existing allowed shedding16+2+4 covers22. One loaned
wire may remove this admission cliff without weakening any assertion.

Restore only the original exact forward128 carry loan, using its unchanged
existing implementation. No new primitive, approximation/window/cut, or guard
change. Prior lean128 probe had no effect (the path was not eligible at128),
positive streams identical and lowerbudget failures preserved. Keep that result.

First fullpublic714c control with loanoverride OFF. Fixed raw cases1234/t21,
1234/t28,1233/t28,1232/t28 with loan128 ON. Stronger28-bit square witness is the
candidate precision;21 is an inherited diagnostic control. Freeze before native
generation; measure actual physicalQ and completeT only later, never inferQ
from budget. No final gate, nonce search, benchmark or scored record here.
