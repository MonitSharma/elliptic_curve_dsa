from pathlib import Path
r=Path(__file__).resolve().parent;s=(r/'verify.rs').read_text()
s=s.replace('assert_eq!(proof_manifest["status"],"SOURCE_BOUND_UNIVERSAL_PROOFS_VERIFIED");','assert_eq!(proof_manifest["status"],"SOURCE_BOUND_EXTENSION_PROOFS_VERIFIED");')
old=' audit(&generated,&[],&[17876252],1024,&HashSet::new(),&HashMap::new());'
new=''' let zero=&proof_manifest["zero_row"];assert_eq!(zero["fresh_replay"]["verdict"],"unsat");assert_eq!(zero["meaningful_source_fault_detected"],true);
 let meta=&zero["input"];assert_eq!(meta["base_pre_tail_sha3_256"],"468e86dd1628976643d42b4bb50bdb8c43211f4d29bfbc3df60b11f7342ac619");
 let start=meta["start"].as_u64().unwrap()as usize;let index=meta["first"].as_u64().unwrap()as usize;assert_eq!(index,17876252);assert_eq!(meta["last"].as_u64().unwrap()as usize,index);assert_eq!(meta["initial_depth"],0);
 let mut depth=0isize;for o in &generated[..start]{if o.kind==K::PushCondition{depth+=1;}if o.kind==K::PopCondition{depth-=1;}assert!(depth>=0);}assert_eq!(depth,0);
 assert_eq!(hash(&generated[start..=index]),meta["raw_sha3_256"].as_str().unwrap());
 assert_eq!(hash(&generated[index..=index]),meta["row_sha3_256"].as_str().unwrap());
 assert_eq!(meta["row_sha3_256"],"167c7dad3201c7b11743b8d6bdd1949fa61952ac7201f71692a3a369be305823");'''
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace('"zero_rows":1,','"zero_rows":1,"zero_row_proof":"source-bound root-scope arbitrary-input SAT theorem, freshly replayed with detected source-control mutation",')
(r/'verify_extension.rs').write_text(s)
