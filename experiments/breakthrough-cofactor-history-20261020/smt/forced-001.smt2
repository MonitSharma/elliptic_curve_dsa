; benchmark generated from python API
(set-info :status unknown)
(declare-fun j () Int)
(declare-fun k () Int)
(assert
 (let ((?x62 (+ 1 (div (+ (* 8 k) (* (- 1) (+ (* 2 j) 1))) 4))))
(let ((?x67 (mod (+ ?x62 (div (+ (* 2 j) 1) 4)) 2)))
(let ((?x48 (+ 1 (div (+ (* 8 k) (* (- 1) (+ (* 2 j) 1))) 2))))
(let ((?x61 (mod (+ ?x48 (div (+ (* 2 j) 1) 2)) 2)))
(or (and (distinct ?x61 0) true) (and (distinct ?x67 0) true)))))))
(check-sat)
