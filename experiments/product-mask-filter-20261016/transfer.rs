fn bind_transfer(){
 let root="/home/hclau/ecdsa_research/product-exact-20261015/cache-certificate-v2-20261016";
 for(name,sha)in [
 ("CACHE_EQUIVALENCE_CERTIFICATE.json","4857f8255c6aa85f0c6cb84720c6d5690aaca060f2758a8c517bd43fc5e2f04e"),
 ("PER_INPUT_MASK_TRANSFER.json","722be8db61c0a29533f3297a31192e64f7558d4c828b210c1b1dc33ce272c8b3"),
 ("PER_INPUT_MASK_TRANSFER.md","efc7c9583caf0d918fa555694a51aed9959b19c6b29fc198c2e82a8affc22317")]{sha_check(&format!("{root}/{name}"),sha);}
 eprintln!("TRANSFER_BINDING original2a522394 candidate180af069 universal25stage perinput-bit; bounded validation only");
}
fn check_candidate_seeds(ops:&[Op],prefix:&Shake256,tail:&[Op]){
 for nonce in [1,2,17,255]{let mut actual=ops[..ops.len()-TAIL].to_vec();actual.extend(nonce_tail(tail,nonce));let mut reference=fiat_shamir_seed(&actual);let mut h=prefix.clone();for op in nonce_tail(tail,nonce){h.update(&record49(&op));}let mut candidate=h.finalize_xof();let mut a=[0u8;4096];let mut b=[0u8;4096];XofReader::read(&mut reference,&mut a);XofReader::read(&mut candidate,&mut b);assert_eq!(a,b,"candidate own Fiat prefix/tail mismatch nonce{nonce}");}
 eprintln!("CANDIDATE_OWN_FIAT_PROTECTED_4096_BYTE_CONTROLS_PASS nonces=1,2,17,255");
}
