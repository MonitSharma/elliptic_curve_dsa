; benchmark generated from python API
(set-info :status unknown)
(declare-fun j () Int)
(declare-fun k () Int)
(assert
 (let ((?x68 (+ 1 (div (+ (* 8 k) (* (- 7) (+ (* 2 j) 1))) 4))))
(let ((?x75 (mod (+ ?x68 (div (+ (* 2 j) 1) 4)) 2)))
(let ((?x28 (+ 1 (div (+ (* 8 k) (* (- 7) (+ (* 2 j) 1))) 2))))
(let ((?x48 (mod (+ ?x28 (div (+ (* 2 j) 1) 2)) 2)))
(or (and (distinct ?x48 1) true) (and (distinct ?x75 1) true)))))))
(check-sat)
