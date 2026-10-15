fn export_census(path:&str,label:&str,count:usize,out:&str) {
 let mut known=std::collections::HashMap::new();let mut bad=std::collections::HashSet::new();
 for line in std::fs::read_to_string(path).unwrap().lines(){let row:serde_json::Value=serde_json::from_str(line).unwrap();let batch=row["batch"].as_u64().unwrap()as usize;for fail in row["failures"].as_array().unwrap(){let k1=U256::from_str_radix(fail["k1"].as_str().unwrap().trim_start_matches("0x"),16).unwrap();let k2=U256::from_str_radix(fail["k2"].as_str().unwrap().trim_start_matches("0x"),16).unwrap();known.insert((batch,fail["lane"].as_u64().unwrap()as usize),(k1,k2));if fail["value"].as_u64().unwrap()==1{bad.insert((batch,fail["lane"].as_u64().unwrap()as usize));}}}
 let fast=FastCurve::new(10);let curve=secp256k1();let mut out=std::io::BufWriter::new(File::create(out).unwrap());let t=std::time::Instant::now();let mut nbad=0;
 writeln!(out,"batch\tlane\tk1\tk2\ttx\tty\tox\toy\tex\tey\tvalue").unwrap();
 for batch in 0..count {
  let mut h=Shake256::default();h.update(b"ecdsa-research-failure-census-v1");h.update(&(label.len()as u64).to_le_bytes());h.update(label.as_bytes());h.update(&(batch as u64).to_le_bytes());let mut rng=h.finalize_xof();let mut ks=Vec::new();
  for _ in 0..128{let mut r=[0u8;32];XofReader::read(&mut rng,&mut r);ks.push(U256::from_le_bytes(r));}
  let pts=fast.points(&ks);
  for lane in 0..64{let(t,o)=(pts[lane*2],pts[lane*2+1]);assert!(t.0!=o.0,"degenerate input requires census skip replay");if let Some(pair)=known.get(&(batch,lane)){assert_eq!(*pair,(ks[lane*2],ks[lane*2+1]));}let e=curve.add(t.0,t.1,o.0,o.1);let b=bad.contains(&(batch,lane));nbad+=usize::from(b);writeln!(out,"{batch}\t{lane}\t{:x}\t{:x}\t{:x}\t{:x}\t{:x}\t{:x}\t{:x}\t{:x}\t{}",ks[lane*2],ks[lane*2+1],t.0,t.1,o.0,o.1,e.0,e.1,usize::from(b)).unwrap();}
 }
 eprintln!("EXPORTED batches={count} shots={} value_failures={nbad} seconds={:.3}",count*64,t.elapsed().as_secs_f64());
}
