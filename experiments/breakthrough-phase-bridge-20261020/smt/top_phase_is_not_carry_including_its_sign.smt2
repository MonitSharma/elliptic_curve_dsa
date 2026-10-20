; benchmark generated from python API
(set-info :status unknown)
(declare-fun incoming_carry () Bool)
(declare-fun target () Bool)
(declare-fun complement () Bool)
(declare-fun source_parity () Bool)
(assert
 (let (($x12 (and target incoming_carry)))
(let (($x13 (or (and (xor source_parity complement) target) (and (xor source_parity complement) incoming_carry) $x12)))
(let (($x23 (and (xor target incoming_carry) (xor (xor source_parity complement) incoming_carry))))
(let (($x25 (xor $x23 (not incoming_carry))))
(and (distinct $x25 (not $x13)) true))))))
(check-sat)
