; benchmark generated from python API
(set-info :status unknown)
(declare-fun j () Int)
(declare-fun k () Int)
(assert
 (let ((?x30 (+ 1 (div (+ (* 8 k) (* 1 (+ (* 2 j) 1))) 4))))
(let ((?x72 (mod (+ ?x30 (div (+ (* 2 j) 1) 4)) 2)))
(let ((?x90 (+ 1 (div (+ (* 8 k) (* 1 (+ (* 2 j) 1))) 2))))
(let ((?x17 (mod (+ ?x90 (div (+ (* 2 j) 1) 2)) 2)))
(or (and (distinct ?x17 1) true) (and (distinct ?x72 1) true)))))))
(check-sat)
