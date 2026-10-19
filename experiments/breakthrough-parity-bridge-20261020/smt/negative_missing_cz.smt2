; benchmark generated from python API
(set-info :status unknown)
(declare-fun incoming_carry () Bool)
(declare-fun b () Bool)
(declare-fun a () Bool)
(declare-fun measurement_outcome () Bool)
(assert
 (let (($x23 (xor b incoming_carry)))
(let (($x27 (xor a incoming_carry)))
(and measurement_outcome $x27 $x23))))
(check-sat)
