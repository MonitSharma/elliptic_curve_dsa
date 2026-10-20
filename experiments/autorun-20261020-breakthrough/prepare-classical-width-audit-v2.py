from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-classical-width-audit-20261020';r=root/'experiments/breakthrough-classical-width-audit-v2-20261020';r.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore','run.py','PLAN.md']:shutil.copyfile(old/p,r/p)
s=(old/'audit.rs').read_text();s=s.replace('struct State{q:Vec<V>,b:Vec<V>,stack:Vec<V>,base:V}','struct Frame{q:Vec<V>,b:Vec<V>,base:V,guard:V}\nstruct State{q:Vec<V>,b:Vec<V>,stack:Vec<Frame>,base:V}')
needle='K::PushCondition=>{self.stack.push(self.base);self.base=and(self.base,self.b[o.c_condition.0 as usize]);},K::PopCondition=>self.base=self.stack.pop().unwrap()'
assert s.count(needle)==1
s=s.replace(needle,'K::PushCondition=>{let bit=o.c_condition.0 as usize;let guard=and(self.base,self.b[bit]);self.stack.push(Frame{q:self.q.clone(),b:self.b.clone(),base:self.base,guard});self.base=if guard==V::Zero{V::Zero}else{V::One};if guard!=V::Zero{self.b[bit]=V::One;}},K::PopCondition=>{let old=self.stack.pop().unwrap();for(i,x)in old.q.into_iter().enumerate(){self.q[i]=mux(x,self.q[i],old.guard);}for(i,x)in old.b.into_iter().enumerate(){self.b[i]=mux(x,self.b[i],old.guard);}self.base=old.base;}')
needle='let unconditional_reset=touches_high&&o.q_target.0 as usize==high&&matches!(o.kind,K::R|K::Hmr)&&o.c_condition==NO_BIT&&stack_depth==0;'
assert s.count(needle)==1
s=s.replace(needle,'let effective=if o.c_condition==NO_BIT||o.kind==K::PushCondition{s.base}else{and(s.base,s.b[o.c_condition.0 as usize])};let unconditional_reset=touches_high&&o.q_target.0 as usize==high&&matches!(o.kind,K::R|K::Hmr)&&effective==V::One&&s.stack.iter().all(|f|f.q[high]==V::Zero);')
needle='#[test]fn conditional_reset_never_proves_an_unknown_input_zero()'
assert s.count(needle)==1
test='''#[test]fn branch_local_reset_restores_global_zero_without_erasing_a_live_parent(){let mut s=state();let mut p=Op::empty();p.kind=K::PushCondition;p.c_condition=BitId(0);s.apply(&p);let mut x=Op::empty();x.kind=K::X;x.q_target=QubitId(2);s.apply(&x);assert_eq!(s.q[2],V::One);let mut h=Op::empty();h.kind=K::Hmr;h.q_target=QubitId(2);h.c_target=BitId(1);h.c_condition=BitId(0);s.apply(&h);assert_eq!(s.q[2],V::Zero);let mut pop=Op::empty();pop.kind=K::PopCondition;s.apply(&pop);assert_eq!(s.q[2],V::Zero);assert_eq!(s.q[0],V::Quantum);assert_eq!(s.b[0],V::Classical);assert_eq!(s.b[1],V::Classical);}
'''
s=s.replace(needle,test+needle);s=s.replace('Classical taint and unconditional-reset delimiters are conservative.','Classical taint with exact branch cofactors and zero-preserving joins is conservative; reset delimiter requires zero on every false outer branch.');(r/'audit.rs').write_text(s)
with(r/'PLAN.md').open('a')as out:out.write('''
V2 is a new read-only tool with branch cofactoring: enter an unknown classical
guard's true world, save the false-world parent, then conservatively join at
PopCondition. Only equal known constants survive both worlds. A reset-delimited
highest-wire interval may close under an outer guard only when that wire was
zero in every saved false world. This avoids spurious multi-million-operation
lifetimes created by forgetting branch-local clean ancillas. Native fourth
control covers conditional HMR and joins without erasing a live parent. Every
nominee remains conditional on a separate exact interval/snapshot/remapping
proof; this audit makes no rewrite or width-bound claim. V1 verdict preserved.
''')
print(r)
