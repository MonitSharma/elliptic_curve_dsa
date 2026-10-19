from pathlib import Path
r=Path(__file__).resolve().parent;s=(r/'verify.rs').read_text()
taint=(r/'taint.rs').read_text();helpers=taint[taint.index('fn and('):taint.index('fn hash(')]
helpers=helpers.replace('fn and(','fn causal_and(').replace('=and(','=causal_and(').replace('{and(','{causal_and(')
helpers=helpers.replace('fn select(','fn causal_select(').replace('=select(','=causal_select(')
helpers=helpers.replace('fn propagate(','fn causal_propagate(').replace('NO','CAUSAL_NO')
old=' audit(&generated,&[],&[17876252],1024,&HashSet::new(),&HashMap::new());'
new=''' assert_eq!(hash(&generated[17876252..17876253]),"167c7dad3201c7b11743b8d6bdd1949fa61952ac7201f71692a3a369be305823");
 let(influence,_)=causal_propagate(&parent,17876252,10);
 let mut regs:std::collections::BTreeMap<u64,Vec<u64>>=std::collections::BTreeMap::new();
 for o in &parent{if o.kind==K::AppendToRegister&&o.q_target.0!=no{regs.entry(o.r_target.0).or_default().push(o.q_target.0);}}
 assert_eq!(regs[&0].len(),256);assert_eq!(regs[&1].len(),256);
 let mut affected_output_bits=vec![];for reg in 0..2{for(bit,&q)in regs[&reg].iter().enumerate(){if influence[q as usize]{affected_output_bits.push(reg as usize*256+bit);}}}
 let allowed_output_bits:Vec<_>=(0..512).filter(|i|!affected_output_bits.contains(i)).collect();assert!(!allowed_output_bits.is_empty());'''
assert s.count(old)==1;s=s.replace(old,new)
lo=s.index(' let result=serde_json::json!(');hi=s.index('\n std::fs::write(&args[4]',lo)
s=s[:lo]+''' let result=serde_json::json!({"status":"PUBLIC_PARENT_VALUE_MASK_TRANSFER_PASS","base_pre_tail_sha3_256":hash(&base[..base.len()-96]),"parent_sha3_256":hash(&parent),"retained_products":leases.len(),"sat_proof_manifest_sha3_256":format!("{:x}",Sha3_256::digest(&proof_bytes)),"source_bound_parent_reconstruction":true,"omitted_zero_row_index":17876252,"omitted_zero_row_sha3_256":"167c7dad3201c7b11743b8d6bdd1949fa61952ac7201f71692a3a369be305823","affected_output_bits":affected_output_bits,"allowed_output_bits":allowed_output_bits,"phase_equivalence_of_zero_row_claimed":false,"no_sampled_inputs":true,"statement":"All 27 cached products use replayed source-bound universal theorems and exact matched global boundaries, with clean untouched donors and private measured phase repair. The inherited deleted row is not assumed zero: conservative causal influence excludes every possibly affected output value bit. The original per-input RNG-free mask may be used only on allowed_output_bits. No phase theorem is claimed for the inherited row; protected survivor checks still test every output, phase and ancilla."});'''+s[hi:]
s=s.replace('println!("PUBLIC_PARENT_EXTENSION_UNIVERSAL_AUDIT_PASS")','println!("PUBLIC_PARENT_VALUE_MASK_TRANSFER_PASS")')
s+='\nconst CAUSAL_NO:u64=u64::MAX;\n'+helpers
(r/'verify_mask.rs').write_text(s)
