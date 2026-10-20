"""Separate read-only rank probe; original branch witness verdict remains final."""
import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'tool';assert(r/'run-v2.exit').read_text().strip()=='0'
f=json.loads((r/'SOURCE_FREEZE-v2.json').read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(t/p)==h for p,h in f['tool_source_files'].items())
s=(t/'alias.rs').read_text();a='"universal_supports":s.iter().filter(|x|x.len()==1&&x[0].is_empty()).count(),';assert s.count(a)==1;s=s.replace(a,a+'"affine_rank_probe":affine_rank(&q[..top]),"failing_op_kind":format!("{:?}",o.kind),')
s=s.replace('assert_eq!(args.len(),3);let v=io::load_ops(&args[1]);let a=analyze(&v,64);','assert_eq!(args.len(),4);let cap=args[3].parse::<usize>().unwrap();assert!([64,256,1024].contains(&cap));let v=io::load_ops(&args[1]);let a=analyze(&v,cap);').replace('"xor_expression_cap":64','"xor_expression_cap":cap')
s+='''
fn affine_rank(q:&[E])->serde_json::Value{
 let mut basis:HashMap<u32,(E,E)>=HashMap::new();basis.insert(0,(vec![0],vec![q.len()as u32]));let mut dependencies=vec![];
 for(i,row)in q.iter().enumerate(){let mut r=row.clone();let mut w=vec![i as u32];while let Some(&lead)=r.last(){if let Some((b,v))=basis.get(&lead){r=Algebra::xor_raw(&r,b);w=Algebra::xor_raw(&w,v);}else{basis.insert(lead,(r.clone(),w.clone()));break;}}if r.is_empty(){dependencies.push(w);}}
 serde_json::json!({"formal_rank_including_constant":basis.len(),"rows":q.len(),"dependencies":dependencies,"constant_witness_index":q.len(),"scope":"Only exact formal-expression dependencies qualify; opaque functions may hide more relationships. No lower bound on true function rank."})
}
#[cfg(test)]mod rank_controls{use super::*;#[test]fn affine_witness_finds_long_xor_and_constant_relation(){let q=vec![vec![1],vec![2],vec![1,2],vec![0,1,2],vec![3]];let r=affine_rank(&q);assert_eq!(r["formal_rank_including_constant"],4);for w in r["dependencies"].as_array().unwrap(){let mut v=vec![];for i in w.as_array().unwrap(){let i=i.as_u64().unwrap()as usize;v=Algebra::xor_raw(&v,&if i==q.len(){vec![0]}else{q[i].clone()});}assert!(v.is_empty());}}}
'''
(t/'rank_probe.rs').write_text(s);p=t/'Cargo.toml';s=p.read_text();s+='\n[[bin]]\nname="exact_rank_probe"\npath="rank_probe.rs"\n';p.write_text(s)
f['tool_source_files']={p.relative_to(t).as_posix():sha(p)for p in t.iterdir()if p.is_file()};f['scope']='Read-only exact affine dependency probe at first uncertified highest-wire lifetime, fixed expression caps64/256/1024. Separate source/binary; original failed width proof remains unchanged. Native9 controls before grid. No source transformation, statistical gate or nonce.';(r/'SOURCE_FREEZE-rank.json').write_text(json.dumps(f,indent=2)+'\n')
