; benchmark generated from python API
(set-info :status unknown)
(declare-fun incoming_carry () Bool)
(declare-fun original_target () Bool)
(declare-fun addend () Bool)
(assert
 (let (($x9 (xor (xor addend original_target) incoming_carry)))
(let (($x14 (not $x9)))
(let (($x11 (and addend incoming_carry)))
(let (($x13 (or (and addend original_target) $x11 (and original_target incoming_carry))))
(and (distinct $x13 (or (and addend $x14) $x11 (and $x14 incoming_carry))) true))))))
(check-sat)
