from pathlib import Path
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-classical-width-audit-20261020';r.mkdir(exist_ok=False)
(r/'.gitattributes').write_text('* -text\n');(r/'.gitignore').write_text('tool/\n__pycache__/\n*resource-preflight*\nevidence.tar.gz\n')
(r/'PLAN.md').write_text('''# Conservative classical-carrier and idle-slot nomination

Read only two complete fixed streams: exactpublic714c and stronger28-bit raw2bc0.
Track values as provenconstant0/1, classical-only, or possibly quantum. Quantum
inputregisters start possiblyquantum; classical inputs/outcomes/conditions are
classical. Unsupported cancellation remains possiblyquantum. At each unconditional
reset-delimited lifetime of the highest physical wire, nominate lower noninput
wires that are provenzero or classical-only and have no original quantum touch
through the entire interval. Historical classical values would need a separately
proved snapshot before any borrowing. No rewrite, quantum-rank theorem, resource
record, census, nonce or benchmark. This is only a read-only nomination audit;
absence of nominees is not a lower bound. Freeze inputs, tool and17 protected
dependency files first. Native controls cover conditional reset, swap and taint.
''')
(r/'audit.rs').write_text(r'''mod io;
use quantum_ecc::circuit::{OperationType as K,Op,NO_BIT,NO_QUBIT,analyze_ops,QubitOrBit};
use serde_json::json;
#[derive(Clone,Copy,Debug,PartialEq,Eq)]enum V{Zero,One,Classical,Quantum}
fn and(a:V,b:V)->V{use V::*;match(a,b){(Zero,_)|(_,Zero)=>Zero,(One,x)|(x,One)=>x,(Quantum,_)|(_,Quantum)=>Quantum,_=>Classical}}
fn xor(a:V,b:V)->V{use V::*;match(a,b){(Zero,x)|(x,Zero)=>x,(One,One)=>Zero,(Quantum,_)|(_,Quantum)=>Quantum,_=>Classical}}
fn inv(x:V)->V{xor(x,V::One)}
fn mux(old:V,new:V,c:V)->V{if c==V::One{new}else if c==V::Zero||old==new&&matches!(old,V::Zero|V::One){old}else if old!=V::Quantum&&new!=V::Quantum{V::Classical}else{V::Quantum}}
struct State{q:Vec<V>,b:Vec<V>,stack:Vec<V>,base:V}
impl State{
fn apply(&mut self,o:&Op){let cond=if o.c_condition==NO_BIT||o.kind==K::PushCondition{self.base}else{and(self.base,self.b[o.c_condition.0 as usize])};let t=o.q_target.0 as usize;match o.kind{
K::X=>self.q[t]=xor(self.q[t],cond),K::CX=>self.q[t]=xor(self.q[t],and(cond,self.q[o.q_control1.0 as usize])),K::CCX=>self.q[t]=xor(self.q[t],and(cond,and(self.q[o.q_control1.0 as usize],self.q[o.q_control2.0 as usize]))),
K::Swap=>{let a=o.q_control1.0 as usize;let(x,y)=(self.q[a],self.q[t]);self.q[a]=mux(x,y,cond);self.q[t]=mux(y,x,cond);},
K::R|K::Hmr=>{self.q[t]=mux(self.q[t],V::Zero,cond);if o.kind==K::Hmr{let b=o.c_target.0 as usize;self.b[b]=mux(self.b[b],V::Classical,cond);}},
K::BitStore0|K::BitStore1|K::BitInvert=>{let b=o.c_target.0 as usize;let v=match o.kind{K::BitStore0=>V::Zero,K::BitStore1=>V::One,_=>inv(self.b[b])};self.b[b]=mux(self.b[b],v,cond);},
K::PushCondition=>{self.stack.push(self.base);self.base=and(self.base,self.b[o.c_condition.0 as usize]);},K::PopCondition=>self.base=self.stack.pop().unwrap(),_=>{}}}
}
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),3);let ops=io::load_ops(&a[1]);let(nq,nb,_,regs)=analyze_ops(ops.iter());let n=nq as usize;let high=n-1;let mut inputs=vec![false;n];let mut s=State{q:vec![V::Zero;n],b:vec![V::Zero;nb as usize],stack:vec![],base:V::One};for reg in regs{for slot in reg{match slot{QubitOrBit::Qubit(q)=>{inputs[q.0 as usize]=true;s.q[q.0 as usize]=V::Quantum;},QubitOrBit::Bit(b)=>s.b[b.0 as usize]=V::Classical}}}
let mut touches=vec![Vec::<usize>::new();n];for(k,o)in ops.iter().enumerate(){for q in[o.q_control2,o.q_control1,o.q_target]{if q!=NO_QUBIT{touches[q.0 as usize].push(k);}}}for t in &mut touches{t.dedup();}
let mut ends=Vec::new();for &k in &touches[high]{let o=ops[k];if o.q_target.0 as usize==high&&matches!(o.kind,K::R|K::Hmr)&&o.c_condition==NO_BIT{ends.push(k);}}
let mut rows=Vec::new();let mut begin=None;let mut snapshot=Vec::<(usize,V)>::new();let mut last_end=None;let mut stack_depth=0i32;
for(k,o)in ops.iter().enumerate(){let touches_high=[o.q_control2,o.q_control1,o.q_target].iter().any(|q|q.0 as usize==high);if touches_high&&begin.is_none(){begin=Some(k);snapshot=(512..high).filter(|&q|!inputs[q]&&s.q[q]!=V::Quantum).map(|q|(q,s.q[q])).collect();}
let unconditional_reset=touches_high&&o.q_target.0 as usize==high&&matches!(o.kind,K::R|K::Hmr)&&o.c_condition==NO_BIT&&stack_depth==0;
if unconditional_reset{let start=begin.take().unwrap();let candidates:Vec<_>=snapshot.iter().filter_map(|&(q,v)|{let pos=touches[q].partition_point(|&x|x<start);let next=touches[q].get(pos).copied().unwrap_or(ops.len());(next>k).then(||json!({"wire":q,"kind":format!("{:?}",v),"next_quantum_touch":next}))}).collect();rows.push(json!({"start":start,"end":k,"operations":k-start+1,"next_previous_interval_end":last_end,"idle_classical_or_zero_donors":candidates}));last_end=Some(k);}
s.apply(o);match o.kind{K::PushCondition=>stack_depth+=1,K::PopCondition=>stack_depth-=1,_=>{}}}
assert_eq!(stack_depth,0);let with_donors=rows.iter().filter(|r|!r["idle_classical_or_zero_donors"].as_array().unwrap().is_empty()).count();let result=json!({"status":"READ_ONLY_CONSERVATIVE_NOMINATION_NOT_A_WIDTH_BOUND_OR_REWRITE","operations":ops.len(),"qubits":nq,"highest_wire":high,"highest_wire_touches":touches[high].len(),"closed_intervals":rows.len(),"closed_intervals_with_nominees":with_donors,"unclosed_interval_start":begin,"intervals":rows,"scope":"Classical taint and unconditional-reset delimiters are conservative. No quantum rank/correctness/benchmark claim. Need separate exact snapshot and full remapping proof before any rewrite."});std::fs::write(&a[2],serde_json::to_string_pretty(&result).unwrap()).unwrap();println!("{}",json!({"highest_wire":high,"intervals":rows.len(),"with_nominees":with_donors,"unclosed":begin}));}
#[cfg(test)]mod tests{use super::*;use quantum_ecc::circuit::{QubitId,BitId};fn state()->State{State{q:vec![V::Quantum,V::Classical,V::Zero],b:vec![V::Classical,V::Zero],stack:vec![],base:V::One}}
#[test]fn conditional_reset_never_proves_an_unknown_input_zero(){let mut s=state();let mut o=Op::empty();o.kind=K::R;o.q_target=QubitId(0);o.c_condition=BitId(0);s.apply(&o);assert_eq!(s.q[0],V::Quantum);o.c_condition=NO_BIT;s.apply(&o);assert_eq!(s.q[0],V::Zero);}
#[test]fn conditional_swap_with_quantum_operand_taints_both(){let mut s=state();let mut o=Op::empty();o.kind=K::Swap;o.q_control1=QubitId(0);o.q_target=QubitId(1);o.c_condition=BitId(0);s.apply(&o);assert_eq!(s.q[..2],[V::Quantum,V::Quantum]);}
#[test]fn classical_copy_and_false_control_remain_classical(){let mut s=state();let mut o=Op::empty();o.kind=K::CX;o.q_control1=QubitId(1);o.q_target=QubitId(2);s.apply(&o);assert_eq!(s.q[2],V::Classical);o.q_control1=QubitId(0);o.c_condition=BitId(1);s.apply(&o);assert_eq!(s.q[2],V::Classical);}
}
''')
(r/'run.py').write_text('''import hashlib,json,subprocess,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'tool';old=ws/'breakthrough-stackv3-width-stats-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd=t):
 with(r/(name+'.log')).open('xb')as out:p=subprocess.Popen(cmd,cwd=cwd,stdout=out,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\\n');assert rc==0,name
try:
 f=json.loads((old/'SOURCE-FREEZE.json').read_text());assert all(sha(old/'tool'/p)==h for p,h in f['tool_source_files'].items());assert all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items());t.mkdir();shutil.copyfile(old/'tool/io.rs',t/'io.rs');shutil.copyfile(r/'audit.rs',t/'audit.rs');shutil.copyfile(old/'tool/Cargo.lock',t/'Cargo.lock');s=(old/'tool/Cargo.toml').read_text();s=s[:s.index('[[bin]]')]+"[[bin]]\\nname=\\"classical_width_audit\\"\\npath=\\"audit.rs\\"\\n[profile.release]\\nopt-level=3\\n";(t/'Cargo.toml').write_text(s);subprocess.run(['cp','-a','--reflink=auto',str(old/'tool/target'),str(t/'target')],check=True)
 inputs={'public':ws/'breakthrough-stackv3-width-plan7-20261020/public/ops.bin','stronger28':ws/'breakthrough-stackv3-width-plan7-20261020/cap1234-t28/ops.bin'};expected={'public':'714c4e4c1c2c5c59544dcc3ade28587663b616d46a168b0fcd22a06c29c0916f','stronger28':'2bc0537813dcb2f8b0785c567ecdc5a8056b8c7afe8cffd4f78240c34d32de51'};assert all(sha(p)==expected[n]for n,p in inputs.items());freeze={'tool_source_files':{p:sha(t/p)for p in['audit.rs','io.rs','Cargo.toml','Cargo.lock']},'protected_dependency_files':f['protected_dependency_files'],'inputs':{n:{'path':str(p),'sha256':expected[n]}for n,p in inputs.items()},'scope':'Read-only classical taint/idle-slot nomination, no stream rewrite or scored result.'};(r/'SOURCE-FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\\n');run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','classical_width_audit'],'tests');run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','classical_width_audit'],'build')
 for n,p in inputs.items():run([str(t/'target/release/classical_width_audit'),str(p),str(r/(n+'.json'))],'audit-'+n)
 assert all(sha(t/p)==h for p,h in freeze['tool_source_files'].items());assert all(sha(Path(p))==h for p,h in freeze['protected_dependency_files'].items());assert all(sha(p)==expected[n]for n,p in inputs.items());(r/'run.exit').write_text('0\\n')
except Exception:
 (r/'run.exit').write_text('1\\n');raise
''')
print(r)
