; benchmark generated from python API
(set-info :status unknown)
(declare-fun j () Int)
(assert
 (let ((?x94 (mod (div (* 16 (+ (* 2 j) 1)) 8) 2)))
(let (($x91 (= ?x94 0)))
(let (($x80 (and $x91 (= (mod (div (* 16 (+ (* 2 j) 1)) 16) 2) 0))))
(let ((?x44 (ite $x80 1 0)))
(let (($x140 (or (= (mod (div (* 16 (+ (* 2 j) 1)) 16) 2) 1) (= (mod (div (* 16 (+ (* 2 j) 1)) 32) 2) 0))))
(let ((?x103 (ite (and $x91 $x140) 1 0)))
(or (and (distinct ?x103 1) true) (and (distinct ?x44 0) true)))))))))
(check-sat)
