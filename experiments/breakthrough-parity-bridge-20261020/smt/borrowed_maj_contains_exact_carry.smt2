; benchmark generated from python API
(set-info :status unknown)
(declare-fun incoming_carry () Bool)
(declare-fun b () Bool)
(declare-fun a () Bool)
(assert
 (let (($x12 (or (and a b) (and a incoming_carry) (and b incoming_carry))))
(let (($x14 (xor incoming_carry a)))
(let (($x13 (xor b a)))
(let (($x15 (and $x13 $x14)))
(let (($x16 (xor a $x15)))
(and (distinct $x16 $x12) true)))))))
(check-sat)
