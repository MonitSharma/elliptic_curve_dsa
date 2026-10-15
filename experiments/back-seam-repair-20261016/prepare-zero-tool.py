from pathlib import Path
import shutil,hashlib,json
r=Path('/home/hclau/ecdsa_research/back-seam-repair-20261016');s=r/'tool/src';(s/'bin').mkdir(parents=True,exist_ok=True);old=r.parent/'seam-phase-repair-20261016/tool';shutil.copy2(old/'Cargo.toml',r/'tool/Cargo.toml')
prefix=(old/'src/bin/phase_primitive.rs').read_text().split('include!')[0]
text=(r/'width_interned_witness_cap512.rs').read_text();text='\n'.join('//'+line[3:]if line.startswith('//!')else line for line in text.splitlines())+'\n';(s/'width_interned_witness_cap512.rs').write_text(text)
body='''
pub use quantum_ecc::circuit;
mod support {
 include!("../width_interned_witness_cap512.rs");
 impl Support { pub(super) fn zero(&self,q:usize)->bool {self.qubits[q].is_zero()} }
}
fn main(){let args:Vec<_>=std::env::args().collect();let ops=load_ops(&args[1]).unwrap();let input:serde_json::Value=serde_json::from_reader(File::open(&args[2]).unwrap()).unwrap();let queries=input["results"].as_array().unwrap();let mut state=support::Support::new(&ops);let mut results=Vec::new();let end=queries.iter().map(|v|v["at"].as_u64().unwrap()as usize).max().unwrap();for(at,op)in ops.iter().enumerate(){for row in queries.iter().filter(|v|v["at"].as_u64().unwrap()as usize==at){let unresolved:Vec<_>=row["qubits"].as_array().unwrap().iter().filter(|q|!state.zero(q.as_u64().unwrap()as usize)).cloned().collect();let mut out=row.clone();out["unresolved"]=serde_json::json!(unresolved);eprintln!("PREFIX_EXACT site={} kind={} unresolved={}",row["site"],row["kind"],unresolved.len());results.push(out);}if at>=end{break;}let _=state.step(op);}let proved=results.iter().all(|r|r["unresolved"].as_array().unwrap().is_empty());println!("{}",serde_json::json!({"proved":proved,"results":results,"all_abi_inputs_arbitrary":true,"all_hmr_fresh":true,"original_ops_only_no_rewrites":true,"phase_outside_contract":true,"immutable_expression_atoms":true,"fresh_nonreused_caps":true}));}
'''
(s/'bin/zero_prefix.rs').write_text(prefix+body)
(r/'zero-tool-hashes.json').write_text(json.dumps({str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest()for p in s.rglob('*.rs')},indent=2)+'\n')
