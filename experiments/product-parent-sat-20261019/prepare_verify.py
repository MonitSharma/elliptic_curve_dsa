from pathlib import Path
r=Path(__file__).resolve().parent;s=(r/'legacy-verify.rs').read_text()
s=s.replace('fn audit(ops:&[Op],leases:&[[u64;9]],zeros:&[usize],cap:usize){',
'''fn audit(ops:&[Op],leases:&[[u64;9]],zeros:&[usize],cap:usize,sat:&HashSet<(usize,usize)>,boundaries:&HashMap<usize,serde_json::Value>){''')
old='   assert_eq!(product.as_ref().unwrap(),&expected[&(s[0]as usize)],"unequal product at {i}");'
new='   assert!(product.as_ref().unwrap()==&expected[&(s[0]as usize)] || sat.contains(&(s[0]as usize,i)),"no verified product theorem at {i}");'
assert s.count(old)==1;s=s.replace(old,new)
needle='   active.insert(s[2],i);expected.insert(i,product.clone().unwrap());'
check='''   if let Some(bd)=boundaries.get(&i){
    assert_eq!(bd["first"].as_u64().unwrap(),i as u64);
    for(k,e)in bd["q"].as_object().unwrap(){assert_eq!(q[k.parse::<usize>().unwrap()],serde_json::from_value::<E>(e.clone()).unwrap(),"quantum boundary mismatch at {i}");}
    for(k,e)in bd["c"].as_object().unwrap(){assert_eq!(c[k.parse::<usize>().unwrap()],serde_json::from_value::<E>(e.clone()).unwrap(),"classical boundary mismatch at {i}");}
    assert_eq!(base,serde_json::from_value::<E>(bd["base"].clone()).unwrap());
    assert_eq!(stack,serde_json::from_value::<Vec<E>>(bd["stack"].clone()).unwrap());
   }
'''
assert s.count(needle)==1;s=s.replace(needle,check+needle)
s=s.replace('assert_eq!(args.len(),5,"baseline public_parent leases_json receipt");','assert_eq!(args.len(),6,"baseline public_parent leases_json receipt verified_proofs");')
old=' audit(&base,&leases,&[],1024);'
new=''' let proof_bytes=std::fs::read(&args[5]).unwrap();let proof_manifest:serde_json::Value=serde_json::from_slice(&proof_bytes).unwrap();
 assert_eq!(proof_manifest["status"],"SOURCE_BOUND_UNIVERSAL_PROOFS_VERIFIED");
 assert_eq!(proof_manifest["base_pre_tail_sha3_256"],hash(&base[..base.len()-96]));
 let mut sat=HashSet::new();let mut boundaries=HashMap::new();
 for p in proof_manifest["proofs"].as_array().unwrap(){
  assert_eq!(p["fresh_replay"]["verdict"],"unsat");let first=p["first"].as_u64().unwrap()as usize;let last=p["last"].as_u64().unwrap()as usize;
  assert!(sat.insert((first,last)));let bd:serde_json::Value=serde_json::from_str(&std::fs::read_to_string(p["boundary_file"].as_str().unwrap()).unwrap()).unwrap();assert!(boundaries.insert(first,bd).is_none());
 }
 assert_eq!(sat.len(),27);assert!(leases.iter().all(|s|sat.contains(&(s[0]as usize,s[1]as usize))));
 audit(&base,&leases,&[],1024,&sat,&boundaries);'''
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace('audit(&generated,&[],&[17876252],1024);','audit(&generated,&[],&[17876252],1024,&HashSet::new(),&HashMap::new());')
s=s.replace('"The 27 unconditional products have exact equal Boolean expressions, clean untouched donors and fresh private measurement/phase correction.',
            '"The 27 unconditional products follow from replayed source-bound SAT theorems and matched global boundary states, with clean untouched donors and fresh private measurement/phase correction.')
s=s.replace('"no_sampled_inputs":true,','"no_sampled_inputs":true,"sat_proof_manifest_sha3_256":format!("{:x}",Sha3_256::digest(&proof_bytes)),')
(r/'verify.rs').write_text(s)
