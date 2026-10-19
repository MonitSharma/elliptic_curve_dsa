; benchmark generated from python API
(set-info :status unknown)
(declare-fun incoming_carry () Bool)
(declare-fun b () Bool)
(declare-fun a () Bool)
(assert
 (let (($x12 (or (and a b) (and a incoming_carry) (and b incoming_carry))))
(let (($x23 (xor b incoming_carry)))
(let (($x27 (xor a incoming_carry)))
(let (($x28 (and $x27 $x23)))
(and (distinct (xor $x28 incoming_carry) $x12) true))))))
(check-sat)
