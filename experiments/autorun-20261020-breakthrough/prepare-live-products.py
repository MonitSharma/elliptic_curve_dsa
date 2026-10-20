from pathlib import Path
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-live-products-20261020';r.mkdir(exist_ok=False)
(r/'.gitattributes').write_text('* -text\n');(r/'.gitignore').write_text('tool/\n__pycache__/\n*resource-preflight*\nevidence.tar.gz\n*.ops.bin\n')
(r/'PLAN.md').write_text('''# General exact live-product and affine-span elimination

Fixed complete input sources before sampling: publice3/714c, fixed1233/t28 generic
36e809, our officially reproducedT748691/cec715. Reuse the exact XOR/SymTriple
algebra from the controlled context engine, cap96 terms and fresh whole-function
atoms on overflow. Track all original operations, registers, mutable classical
values, fresh measurement outcomes and captured guards. At a CCX/CCZ, its two
control product may be exactlyzero/one or an exact affine parity of CURRENT
other physical quantum wires. Sparse atom closure (64 wires/3 levels) nominates
rows; Gaussian elimination over full exact symbolic expressions proves parity.
Replace only that gate with CX/X or CZ/Z of the proved parity, retaining its
classical condition and lexical guard. CCX may never use its own target as a
parity control. CCZ self-target factors becomeZ. No measurement, RNG draw,
classical operation, metadata or quantum index is added or reordered. Every
proof state consumes ORIGINAL operations before the next query.

Input constraints are only circuit register metadata/zero ancillas; arbitrary
quantum/classical data and measurement outcomes. Hashes index full keys only;
no fingerprint-based acceptance. Native controls must verify full basis/phase,
guard capture/mutation, self-target exclusion and broken affine relations before
any complete source scan. Static savings are not full benchmark results.
No final gate/nonce/benchmark; each assembled finished source needs its own gate.
''')
(r/'main.rs').write_text(r'''
mod io;
use quantum_ecc::circuit::{Op,OperationType as K,QubitId,BitId,NO_BIT,analyze_ops};
use std::collections::{HashMap,HashSet};use sha3::{Digest,Sha3_256};
include!("algebra.rs");
fn parity(target:&E,q:&[E],index:&HashMap<u32,HashSet<usize>>,skip:Option<usize>)->Option<(Vec<usize>,bool)>{
let mut reached:HashSet<u32>=target.iter().copied().filter(|&a|a!=0).collect();let mut frontier:Vec<u32>=reached.iter().copied().collect();frontier.sort_unstable();let mut seen=HashSet::new();let mut rows=vec![];
if frontier.iter().any(|a|!index.contains_key(a)){return None;}
for _ in 0..3{let mut add=HashSet::new();for a in &frontier{if let Some(ws)=index.get(a){for &w in ws{if !seen.contains(&w)&&Some(w)!=skip{add.insert(w);}}}}let mut add:Vec<_>=add.into_iter().collect();add.sort_unstable();if rows.len()+add.len()>64{break;}let mut next=vec![];for w in add{seen.insert(w);rows.push(w);for &a in &q[w]{if a!=0&&reached.insert(a){next.push(a);}}}frontier=next;if frontier.is_empty(){break;}}
let mut basis:HashMap<u32,(E,Vec<usize>)>=HashMap::new();for w in rows{let mut row=q[w].clone();let mut comb=vec![w];while let Some(p)=row.iter().rev().copied().find(|&a|a!=0){if let Some((b,c))=basis.get(&p){row=Algebra::xor_raw(&row,b);comb=symdiff(&comb,c);}else{basis.insert(p,(row.clone(),comb));break;}}}
let mut row=target.clone();let mut comb=vec![];while let Some(p)=row.iter().rev().copied().find(|&a|a!=0){let(b,c)=basis.get(&p)?;row=Algebra::xor_raw(&row,b);comb=symdiff(&comb,c);}Some((comb,row.contains(&0)))
}
fn symdiff(a:&[usize],b:&[usize])->Vec<usize>{let(mut i,mut j)=(0,0);let mut out=vec![];while i<a.len()||j<b.len(){if j==b.len()||(i<a.len()&&a[i]<b[j]){out.push(a[i]);i+=1;}else if i==a.len()||b[j]<a[i]{out.push(b[j]);j+=1;}else{i+=1;j+=1;}}out}
fn index_remove(index:&mut HashMap<u32,HashSet<usize>>,q:usize,value:&E){for &a in value{if a!=0{let s=index.get_mut(&a).unwrap();assert!(s.remove(&q));if s.is_empty(){index.remove(&a);}}}}
fn index_add(index:&mut HashMap<u32,HashSet<usize>>,q:usize,value:&E){for &a in value{if a!=0{index.entry(a).or_default().insert(q);}}}
fn simplify(ops:&[Op])->(Vec<Op>,Vec<serde_json::Value>,u64){let(nq,nb,_,_)=analyze_ops(ops.iter());let mut alg=Algebra{next:1,products:HashMap::new(),cap:96,truncations:0};let(mut q,mut c)=initial_inputs(ops,nq as usize,nb as usize,&mut alg);let mut index=HashMap::new();for(w,v)in q.iter().enumerate(){index_add(&mut index,w,v);}let mut base=vec![0];let mut stack=vec![];let mut out=Vec::with_capacity(ops.len());let mut hits=vec![];let no=u64::MAX;
for(i,o)in ops.iter().copied().enumerate(){let t=o.q_target.0 as usize;let a=o.q_control1.0 as usize;let b=o.q_control2.0 as usize;let ct=o.c_target.0 as usize;let mut replacement=None;
if matches!(o.kind,K::CCX|K::CCZ){let product=alg.and(&q[a],&q[b]);if let Some((controls,one))=parity(&product,&q,&index,if o.kind==K::CCX{Some(t)}else{None}){let mut emitted=vec![];if one{let mut x=o;x.kind=if o.kind==K::CCX{K::X}else{K::Z};x.q_control1=QubitId(no);x.q_control2=QubitId(no);x.validate();emitted.push(x);}for &w in &controls{let mut x=o;x.q_control2=QubitId(no);if o.kind==K::CCZ&&w==t{x.kind=K::Z;x.q_control1=QubitId(no);}else{x.kind=if o.kind==K::CCX{K::CX}else{K::CZ};x.q_control1=QubitId(w as u64);}x.validate();emitted.push(x);}hits.push(serde_json::json!({"index":i,"kind":o.kind as u32,"controls":controls,"one":one,"classical_condition":o.c_condition.0,"expression":product}));replacement=Some(emitted);}}
if let Some(v)=replacement{out.extend(v);}else{out.push(o);}
if o.kind==K::PushCondition{stack.push(base.clone());base=alg.and(&base,&c[o.c_condition.0 as usize]);continue;}if o.kind==K::PopCondition{base=stack.pop().unwrap();continue;}
let eff=if o.c_condition==NO_BIT{base.clone()}else{alg.and(&base,&c[o.c_condition.0 as usize])};if eff.is_empty(){continue;}
let writes=match o.kind{K::Swap=>vec![a,t],K::X|K::CX|K::CCX|K::R|K::Hmr=>vec![t],_=>vec![]};for &w in &writes{index_remove(&mut index,w,&q[w]);}
match o.kind{K::X=>q[t]=alg.xor(&q[t],&eff),K::CX=>{let v=alg.and(&q[a],&eff);q[t]=alg.xor(&q[t],&v);},K::CCX=>{let v=alg.and(&q[a],&q[b]);let v=alg.and(&v,&eff);q[t]=alg.xor(&q[t],&v);},K::Swap=>{let v=alg.xor(&q[a],&q[t]);let v=alg.and(&v,&eff);q[a]=alg.xor(&q[a],&v);q[t]=alg.xor(&q[t],&v);},K::R|K::Hmr=>{q[t]=alg.select(&q[t],&vec![],&eff);if o.kind==K::Hmr{let v=alg.fresh();c[ct]=alg.select(&c[ct],&v,&eff);}},K::BitInvert=>c[ct]=alg.xor(&c[ct],&eff),K::BitStore0=>c[ct]=alg.select(&c[ct],&vec![],&eff),K::BitStore1=>c[ct]=alg.select(&c[ct],&vec![0],&eff),K::Neg|K::Z|K::CZ|K::CCZ|K::Register|K::AppendToRegister|K::DebugPrint=>{},_=>panic!("unsupported")}
for &w in &writes{index_add(&mut index,w,&q[w]);}if i%2000000==0{eprintln!("LIVE_PRODUCTS op={i} proven={} algebra_nodes={} truncations={}",hits.len(),alg.products.len(),alg.truncations);}}
assert!(stack.is_empty());(out,hits,alg.truncations)}
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),3);let ops=io::load_ops(&a[1]);let(out,hits,truncations)=simplify(&ops);io::save_ops(&(a[2].clone()+".ops.bin"),&out);let result=serde_json::json!({"status":"EXACT_ORIGINAL_OP_LIVE_PRODUCT_PARITIES_COMPONENT_NOT_SCORED","input_count":ops.len(),"input_records_sha3":hash(&ops),"output_count":out.len(),"output_records_sha3":hash(&out),"hits":hits,"truncations":truncations,"scope":"Every replacement proved by exact global expression and sparse Gaussian parity. No measurement/RNG/classical/metadata/quantum index changes. Counts are diagnostic, not scored."});std::fs::write(a[2].clone()+".json",serde_json::to_string_pretty(&result).unwrap()).unwrap();println!("proven={} input={} output={}",result["hits"].as_array().unwrap().len(),ops.len(),out.len());}
#[cfg(test)]mod tests{
use super::*;use quantum_ecc::circuit::RegisterId;use quantum_ecc::sim::Simulator;use sha3::digest::XofReader;
struct Fixed{v:u8,reads:usize}impl XofReader for Fixed{fn read(&mut self,out:&mut[u8]){self.reads+=out.len();out.fill(self.v);}}
fn op(k:K,c2:u64,c1:u64,t:u64,ct:u64,cc:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_control2=QubitId(c2);o.q_control1=QubitId(c1);o.q_target=QubitId(t);o.c_target=BitId(ct);o.c_condition=BitId(cc);o.validate();o}
fn fixture(guard:bool,mutate:bool,broken:bool)->Vec<Op>{let n=u64::MAX;let mut ops=vec![];for q in 0..4{let mut o=op(K::AppendToRegister,n,n,q,n,n);o.r_target=RegisterId(0);ops.push(o);}for b in 0..2{let mut o=op(K::AppendToRegister,n,n,n,b,n);o.r_target=RegisterId(1);ops.push(o);}ops.push(op(K::CCX,0,1,4,n,n));ops.push(op(K::CX,n,2,4,n,n));if broken{ops.push(op(K::X,n,n,4,n,n));}if guard{ops.push(op(K::PushCondition,n,n,n,n,0));}if mutate{ops.push(op(K::BitInvert,n,n,n,0,n));}ops.push(op(K::CCX,0,1,3,n,1));ops.push(op(K::CCZ,0,1,3,n,1));if guard{ops.push(op(K::PopCondition,n,n,n,n,n));}ops}
fn paired(ops:&[Op],out:&[Op]){let(nq,nb,_,_)=analyze_ops(ops.iter());for word in[0u8,255,0xa5,0x5a]{let mut ra=Fixed{v:word,reads:0};let mut rb=Fixed{v:word,reads:0};let mut a=Simulator::new(nq as usize,nb as usize,&mut ra);let mut b=Simulator::new(nq as usize,nb as usize,&mut rb);for lane in 0..64{for q in 0..4{a.qubits[q]|=((lane>>q&1)as u64)<<lane;}for q in 0..2{a.bits[q]|=((lane>>(q+4)&1)as u64)<<lane;}}b.qubits.clone_from(&a.qubits);b.bits.clone_from(&a.bits);a.apply_iter(ops.iter());b.apply_iter(out.iter());assert_eq!(a.qubits,b.qubits);assert_eq!(a.bits,b.bits);assert_eq!(a.phase,b.phase);drop(a);drop(b);assert_eq!(ra.reads,rb.reads);}}
#[test]fn live_affine_parities_preserve_all_values_phase_and_captured_mutating_guards(){for guard in[false,true]{for mutate in[false,true]{for broken in[false,true]{let ops=fixture(guard,mutate,broken);let(out,hits,_)=simplify(&ops);assert_eq!(hits.len(),2);assert!(hits.iter().all(|x|x["controls"].as_array().unwrap().len()==2));paired(&ops,&out);}}}}
#[test]fn ccx_target_is_excluded_while_ccz_self_target_becomes_phase(){let n=u64::MAX;let mut ops=fixture(false,false,false);ops.truncate(8);ops.push(op(K::CCX,0,1,4,n,n));ops.push(op(K::CCZ,0,1,4,n,n));let(out,_,_)=simplify(&ops);paired(&ops,&out);assert!(out.iter().all(|o|!matches!(o.kind,K::CX|K::CZ)||o.q_control1!=o.q_target));}
#[test]fn unknown_fresh_input_and_missing_parity_rows_are_not_reduced(){let mut ops=fixture(false,false,false);ops.remove(6);let(out,hits,_)=simplify(&ops);assert!(hits.is_empty());paired(&ops,&out);}
#[test]fn fresh_measurements_and_conditional_resets_keep_rng_and_full_state(){let n=u64::MAX;let mut ops=fixture(true,true,true);ops.extend([op(K::Hmr,n,n,4,2,n),op(K::R,n,n,3,n,2)]);let(out,_,_)=simplify(&ops);paired(&ops,&out);}
}
''')
(r/'run.py').write_text('''import hashlib,json,subprocess,shutil,time
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'tool';old=ws/'breakthrough-context16384-lease-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd=t):
 with(r/(name+'.log')).open('xb')as out:p=subprocess.Popen(cmd,cwd=cwd,stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\\n');assert rc==0,name
try:
 f=json.loads((old/'SOURCE-FREEZE.json').read_text());assert all(sha(old/'tool'/p)==h for p,h in f['tool_source_files'].items());assert all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items());t.mkdir();s=(old/'tool/discover.rs').read_text();algebra=s[s.index('type E ='):s.index('fn make(')]+s[s.index('fn initial_inputs('):s.index('// Fingerprints propose')];(t/'algebra.rs').write_text(algebra);shutil.copyfile(r/'main.rs',t/'main.rs');shutil.copyfile(old/'tool/io.rs',t/'io.rs');shutil.copyfile(old/'tool/Cargo.lock',t/'Cargo.lock');cargo=(old/'tool/Cargo.toml').read_text();cargo=cargo[:cargo.index('[[bin]]')]+"[[bin]]\\nname=\\"live_products\\"\\npath=\\"main.rs\\"\\n[profile.release]\\nopt-level=3\\n";(t/'Cargo.toml').write_text(cargo);subprocess.run(['cp','-a','--reflink=auto',str(old/'tool/target'),str(t/'target')],check=True)
 inputs={'publice3':(ws/'breakthrough-stackv3-width-plan7-both-20261020/public/ops.bin','714c4e4c1c2c5c59544dcc3ade28587663b616d46a168b0fcd22a06c29c0916f'),'generic1233':(ws/'breakthrough-stackv3-plan7-generic-v2-20261020/candidate/ops.bin','36e809e798c8a8880bd41c77e30c2a1763081bde177a91e035a7eb83c83a87b7'),'toffoli748691':(ws/'breakthrough-native-both-final-20261020/candidate/ops.bin','cec71544f16da5598921a8a04e3b1416bda6f28d01878b1101ac724157a6f536')};assert all(sha(p)==h for p,h in inputs.values());freeze={'tool_source_files':{p:sha(t/p)for p in['main.rs','algebra.rs','io.rs','Cargo.toml','Cargo.lock']},'protected_dependency_files':f['protected_dependency_files'],'inputs':{n:{'path':str(p),'sha256':h}for n,(p,h)in inputs.items()},'scope':'Exact original-op Boolean live-product affine parity simplification; no RNG/quantum scratch changes, component only.'};(r/'SOURCE-FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\\n');run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','live_products','--','--nocapture'],'tests');run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','live_products'],'build');results={}
 for n,(p,h)in inputs.items():
  start=time.time();run(['timeout','2400',str(t/'target/release/live_products'),str(p),str(r/n)],'scan-'+n);x=json.loads((r/(n+'.json')).read_text());results[n]={'hits':len(x['hits']),'input_count':x['input_count'],'output_count':x['output_count'],'output_records_sha3':x['output_records_sha3'],'output_stream_sha256':sha(r/(n+'.ops.bin')),'seconds':time.time()-start};print(json.dumps({'case':n,**results[n]}),flush=True)
 assert all(sha(t/p)==h for p,h in freeze['tool_source_files'].items());assert all(sha(p)==h for p,h in inputs.values());(r/'RESULT.json').write_text(json.dumps({'status':'EXACT_LIVE_PRODUCTS_COMPONENT_NOT_SCORED','cases':results},indent=2)+'\\n');(r/'run.exit').write_text('0\\n')
except Exception:
 (r/'run.exit').write_text('1\\n');raise
''');print(r)
