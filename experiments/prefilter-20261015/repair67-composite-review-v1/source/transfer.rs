fn bind_transfer(){
 let root="/home/hclau/ecdsa_research/product-exact-20261015/cache-certificate67-20261016";
 for(name,sha)in [
 ("CACHE_EQUIVALENCE_CERTIFICATE.json","303a75ec86a4da8c3a4008646e1b8257768fa40e198f0b7172eeafd19408c7c6"),
 ("PER_INPUT_MASK_TRANSFER.json","d774c492b94f1c6ca458cc42de82d6dbee90a316f7d80c9dc6ee32eb1fe5201f"),
 ("PER_INPUT_MASK_TRANSFER.md","5914f683bb5df08d21f94d79663c6239a84715e27b2eac7e18ce1fcafaee0167")]{sha_check(&format!("{root}/{name}"),sha);}
 eprintln!("TRANSFER_BINDING original2a522394 candidate268aefe2 universal67stage perinput-bit; bounded validation only");
}
fn check_candidate_seeds(ops:&[Op],prefix:&Shake256,tail:&[Op]){
 for nonce in [1,2,17,255]{let mut actual=ops[..ops.len()-TAIL].to_vec();actual.extend(nonce_tail(tail,nonce));let mut reference=fiat_shamir_seed(&actual);let mut h=prefix.clone();for op in nonce_tail(tail,nonce){h.update(&record49(&op));}let mut candidate=h.finalize_xof();let mut a=[0u8;4096];let mut b=[0u8;4096];XofReader::read(&mut reference,&mut a);XofReader::read(&mut candidate,&mut b);assert_eq!(a,b,"candidate own Fiat prefix/tail mismatch nonce{nonce}");}
 eprintln!("CANDIDATE_OWN_FIAT_PROTECTED_4096_BYTE_CONTROLS_PASS nonces=1,2,17,255");
}
