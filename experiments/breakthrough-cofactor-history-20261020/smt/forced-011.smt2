; benchmark generated from python API
(set-info :status unknown)
(declare-fun j () Int)
(declare-fun k () Int)
(assert
 (let ((?x29 (+ 1 (div (+ (* 8 k) (* (- 5) (+ (* 2 j) 1))) 4))))
(let ((?x30 (mod (+ ?x29 (div (+ (* 2 j) 1) 4)) 2)))
(let ((?x55 (+ 1 (div (+ (* 8 k) (* (- 5) (+ (* 2 j) 1))) 2))))
(let ((?x73 (mod (+ ?x55 (div (+ (* 2 j) 1) 2)) 2)))
(or (and (distinct ?x73 0) true) (and (distinct ?x30 1) true)))))))
(check-sat)
