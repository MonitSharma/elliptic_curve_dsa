; benchmark generated from python API
(set-info :status unknown)
(declare-fun j () Int)
(declare-fun k () Int)
(assert
 (let ((?x23 (+ 1 (div (+ (* 8 k) (* 7 (+ (* 2 j) 1))) 4))))
(let ((?x26 (mod (+ ?x23 (div (+ (* 2 j) 1) 4)) 2)))
(let ((?x17 (+ 1 (div (+ (* 8 k) (* 7 (+ (* 2 j) 1))) 2))))
(let ((?x20 (mod (+ ?x17 (div (+ (* 2 j) 1) 2)) 2)))
(or (and (distinct ?x20 0) true) (and (distinct ?x26 0) true)))))))
(check-sat)
