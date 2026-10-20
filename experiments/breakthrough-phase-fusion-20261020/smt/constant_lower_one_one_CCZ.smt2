; benchmark generated from python API
(set-info :status unknown)
(declare-fun lower_add () Bool)
(declare-fun incoming_carry () Bool)
(declare-fun lower_target () Bool)
(declare-fun upper_target () Bool)
(declare-fun upper_add () Bool)
(assert
 (= lower_add true))
(assert
 (let (($x18 (xor upper_add upper_target)))
(let (($x36 (and $x18 lower_target incoming_carry)))
(let (($x42 (xor (xor (and upper_add upper_target) (and $x18 lower_target)) (and $x18 incoming_carry))))
(let (($x43 (xor $x42 $x36)))
(let (($x13 (or (and lower_add lower_target) (and lower_target incoming_carry) (and incoming_carry lower_add))))
(let (($x14 (and upper_add upper_target)))
(let (($x17 (or $x14 (and upper_target $x13) (and $x13 upper_add))))
(and (distinct $x17 $x43) true)))))))))
(check-sat)
