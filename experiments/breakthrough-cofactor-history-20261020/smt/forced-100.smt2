; benchmark generated from python API
(set-info :status unknown)
(declare-fun j () Int)
(declare-fun k () Int)
(assert
 (let ((?x63 (+ 1 (div (+ (* 8 k) (* 5 (+ (* 2 j) 1))) 4))))
(let ((?x61 (mod (+ ?x63 (div (+ (* 2 j) 1) 4)) 2)))
(let ((?x39 (+ 1 (div (+ (* 8 k) (* 5 (+ (* 2 j) 1))) 2))))
(let ((?x62 (mod (+ ?x39 (div (+ (* 2 j) 1) 2)) 2)))
(or (and (distinct ?x62 1) true) (and (distinct ?x61 0) true)))))))
(check-sat)
