; benchmark generated from python API
(set-info :status unknown)
(declare-fun j () Int)
(assert
 (let ((?x49 (mod (div (* 8 (+ (* 2 j) 1)) 8) 2)))
(let (($x67 (= ?x49 0)))
(let (($x95 (and $x67 (= (mod (div (* 8 (+ (* 2 j) 1)) 16) 2) 0))))
(let ((?x132 (ite $x95 1 0)))
(let (($x54 (or (= (mod (div (* 8 (+ (* 2 j) 1)) 16) 2) 1) (= (mod (div (* 8 (+ (* 2 j) 1)) 32) 2) 0))))
(let ((?x42 (ite (and $x67 $x54) 1 0)))
(or (and (distinct ?x42 0) true) (and (distinct ?x132 0) true)))))))))
(check-sat)
