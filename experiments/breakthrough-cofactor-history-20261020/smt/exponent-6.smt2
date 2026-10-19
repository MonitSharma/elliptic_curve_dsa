; benchmark generated from python API
(set-info :status unknown)
(declare-fun j () Int)
(assert
 (let ((?x39 (mod (div (* 64 (+ (* 2 j) 1)) 8) 2)))
(let (($x64 (= ?x39 0)))
(let (($x111 (and $x64 (= (mod (div (* 64 (+ (* 2 j) 1)) 16) 2) 0))))
(let ((?x132 (ite $x111 1 0)))
(let (($x17 (or (= (mod (div (* 64 (+ (* 2 j) 1)) 16) 2) 1) (= (mod (div (* 64 (+ (* 2 j) 1)) 32) 2) 0))))
(let ((?x54 (ite (and $x64 $x17) 1 0)))
(or (and (distinct ?x54 1) true) (and (distinct ?x132 1) true)))))))))
(check-sat)
