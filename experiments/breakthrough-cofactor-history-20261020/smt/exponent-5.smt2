; benchmark generated from python API
(set-info :status unknown)
(declare-fun j () Int)
(assert
 (let ((?x98 (mod (div (* 32 (+ (* 2 j) 1)) 8) 2)))
(let (($x32 (= ?x98 0)))
(let (($x96 (and $x32 (= (mod (div (* 32 (+ (* 2 j) 1)) 16) 2) 0))))
(let ((?x97 (ite $x96 1 0)))
(let (($x73 (or (= (mod (div (* 32 (+ (* 2 j) 1)) 16) 2) 1) (= (mod (div (* 32 (+ (* 2 j) 1)) 32) 2) 0))))
(let ((?x41 (ite (and $x32 $x73) 1 0)))
(or (and (distinct ?x41 0) true) (and (distinct ?x97 1) true)))))))))
(check-sat)
