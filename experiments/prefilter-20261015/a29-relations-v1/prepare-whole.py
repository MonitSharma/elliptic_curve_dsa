from pathlib import Path
r=Path(__file__).resolve().parents[1];out=r/'a29-relations-v2';out.mkdir(exist_ok=True)
def put(p,s):p.write_bytes(s.encode())
s=(r/'tool/src/bin/a29_relation_prefix.rs').read_text(encoding='utf8').replace('../a29_relation_prefix_body.rs','../a29_relation_whole_body.rs')
put(r/'tool/src/bin/a29_relation_whole.rs',s)
s=(r/'tool/src/a29_relation_prefix_body.rs').read_text(encoding='utf8').replace('if i==3991190 {','if i==3982904 {')
s=s.replace('for end in[3991588usize,3991609]{let local=relation_obligations(&ops[i..end],500000,5000,&Default::default());','''let old=load_ops("/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin").unwrap();assert_eq!(&old[3977260..3977276],&ops[3982888..3982904],"whole-helper entry outside anchor");assert_eq!(&old[3985789..3985805],&ops[3991609..3991625],"whole-helper exit outside anchor");drop(old);
 let zeros:std::collections::BTreeSet<u64>=q.iter().enumerate().filter(|(_,p)|p.0.iter().all(|(_,c)|alg.dag.find(*c)==0)).map(|(id,_)|id as u64).collect();
 for end in[3991609usize]{let local=relation_obligations(&ops[i..end],500000,5000,&zeros);''')
s=s.replace('"entry_exact_input_roots":entry,','"entry_exact_input_roots":entry,"required_proved_zero_entry_wires":local.quantum_ids.iter().filter(|q|zeros.contains(q)).copied().collect::<Vec<_>>(),')
# The diagnostic remains a prefix stop, never an export or replacement.
put(r/'tool/src/a29_relation_whole_body.rs',s)
s=(r/'a29-relations-v1/run.sh').read_text(encoding='utf8').replace('a29-relations-v1','a29-relations-v2').replace('a29_relation_prefix','a29_relation_whole')
put(out/'run.sh',s)
