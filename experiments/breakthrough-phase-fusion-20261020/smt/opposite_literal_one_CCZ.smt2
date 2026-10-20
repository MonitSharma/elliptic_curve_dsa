; benchmark generated from python API
(set-info :status unknown)
(declare-fun lower_add () Bool)
(declare-fun upper_add () Bool)
(declare-fun incoming_carry () Bool)
(declare-fun lower_target () Bool)
(declare-fun upper_target () Bool)
(assert
 (= upper_add (not lower_add)))
(assert
 (let (($x27 (xor incoming_carry lower_add)))
(let (($x26 (xor lower_target lower_add)))
(let (($x34 (xor upper_target (and (not (xor upper_target lower_add)) $x26 $x27))))
(let (($x13 (or (and lower_add lower_target) (and lower_target incoming_carry) (and incoming_carry lower_add))))
(let (($x14 (and upper_add upper_target)))
(let (($x17 (or $x14 (and upper_target $x13) (and $x13 upper_add))))
(and (distinct $x17 $x34) true))))))))
(check-sat)
