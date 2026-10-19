; benchmark generated from python API
(set-info :status unknown)
(declare-fun q () Int)
(declare-fun j () Int)
(declare-fun k () Int)
(assert
 (let ((?x114 (mod q 2)))
 (= ?x114 1)))
(assert
 (and (distinct (mod (+ (* 8 k) (* q (+ (* 2 j) 1))) 2) 1) true))
(check-sat)
