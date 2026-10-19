; benchmark generated from python API
(set-info :status unknown)
(declare-fun j () Int)
(declare-fun k () Int)
(assert
 (let ((?x51 (+ 1 (div (+ (* 8 k) (* 3 (+ (* 2 j) 1))) 4))))
(let ((?x59 (mod (+ ?x51 (div (+ (* 2 j) 1) 4)) 2)))
(let ((?x76 (+ 1 (div (+ (* 8 k) (* 3 (+ (* 2 j) 1))) 2))))
(let ((?x49 (mod (+ ?x76 (div (+ (* 2 j) 1) 2)) 2)))
(or (and (distinct ?x49 0) true) (and (distinct ?x59 1) true)))))))
(check-sat)
