; benchmark generated from python API
(set-info :status unknown)
(declare-fun j () Int)
(assert
 (let ((?x10 (* 2 j)))
(let ((?x12 (+ ?x10 1)))
(let ((?x18 (div ?x12 2)))
(and (distinct (mod (+ (+ 1 (div (+ 2 (* 7 ?x12)) 2)) ?x18) 2) 0) true)))))
(check-sat)
