; benchmark generated from python API
(set-info :status unknown)
(declare-fun j () Int)
(declare-fun k () Int)
(assert
 (let ((?x26 (+ 1 (div (+ (* 8 k) (* (- 3) (+ (* 2 j) 1))) 4))))
(let ((?x54 (mod (+ ?x26 (div (+ (* 2 j) 1) 4)) 2)))
(let ((?x71 (+ 1 (div (+ (* 8 k) (* (- 3) (+ (* 2 j) 1))) 2))))
(let ((?x43 (mod (+ ?x71 (div (+ (* 2 j) 1) 2)) 2)))
(or (and (distinct ?x43 1) true) (and (distinct ?x54 0) true)))))))
(check-sat)
