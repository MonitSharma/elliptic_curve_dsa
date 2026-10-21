fn nonce_tail(tail:&[Op],nonce:u64)->Vec<Op>{assert!(nonce<1<<48);let mut t=tail.to_vec();for b in 0..48{t[2*b].q_target=QubitId((nonce>>b)&1);t[2*b+1].q_target=QubitId((nonce>>b)&1);}t}
