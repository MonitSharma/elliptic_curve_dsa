"""Emit a native six-wire bank loan with fully charged six-AND regeneration."""
import hashlib
import json
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import load

HERE=Path(__file__).parent
ROOT=HERE.parents[2]
RAW=ROOT/"research-output/overnight-20261014/toffoli"
net=json.loads(HERE.joinpath("constructor-netlist.json").read_text())
proof=json.loads(RAW.joinpath("phase-basis-reverse.json").read_text())
rows=[m for name,m in proof["basis_rows"]]
space=Space(rows)
assert len(rows)==31 and len(space.values)==31
def moved(mask):
    return (mask&((1<<15)-1))|(space.express(mask>>15)<<15)
outputs=[moved(m) for m in net["outputs"][:21]]
carry=moved(net["outputs"][27])
assert carry==1<<15
assert all(m>>(15+25)==0 for m in outputs)
recompute=[]
dead_indices=[4,6,7,8,9,11]
for j,i in enumerate(dead_indices):
    g=net["gates"][i];pair=[moved(g["a"]),moved(g["b"])]
    assert all(m>>(15+25+j)==0 for m in pair)
    recompute.append(pair)
elim=[];working=list(rows)
for col in range(31):
    pivot=next(i for i in range(col,31) if working[i]>>col&1)
    if pivot!=col:
        working[col],working[pivot]=working[pivot],working[col];elim.append((1,col,pivot))
    for i in range(31):
        if i!=col and working[i]>>col&1:
            working[i] ^= working[col];elim.append((0,col,i))
assert working==[1<<i for i in range(31)]
def transformed(value,ops):
    values=[value>>i&1 for i in range(31)]
    for kind,a,b in ops:
        if kind:values[a],values[b]=values[b],values[a]
        else:values[b] ^= values[a]
    return sum(v<<i for i,v in enumerate(values))
for i in range(31):
    got=transformed(1<<i,list(reversed(elim)))
    expected=sum(((m>>i)&1)<<j for j,m in enumerate(rows))
    assert got==expected and transformed(got,elim)==1<<i
phases=[]
for step in proof["early_erasures"]:
    slot=25+int(step["erase"][4:]);terms=[]
    def index(role):
        if role.startswith("data"):
            r=int(role[4:]);assert r!=0;return r-1
        return 14+(int(role[4:]) if role.startswith("live") else 25+int(role[4:]))
    for kind,a,b in step["phase_terms"]:
        assert kind!="one"
        roles=step["available_order"]
        pair=index(roles[a]),index(roles[b])
        assert 14+slot not in pair
        terms.append(pair)
    phases.append((slot,terms))
text='''//! Generated from the source-bound full constructor and six exact phase identities.
//! Keeps31constructionANDs, frees6wires for the ladder, then pays6ANDs to restore
//! the original undo interface. No nonce, input-packet or census simplification.
use super::*;
#[cfg(test)]
thread_local! { static MODE: std::cell::Cell<bool> = const { std::cell::Cell::new(false) }; }
#[cfg(test)] pub(super) fn enabled() -> bool { MODE.with(|x|x.get()) }
#[cfg(not(test))] pub(super) fn enabled() -> bool { false }
#[cfg(test)] pub(super) fn with_mode<R>(on:bool,f:impl FnOnce()->R)->R {
    let before=MODE.with(|x|x.replace(on)); let result=f(); MODE.with(|x|x.set(before));result
}
'''
text+='const TRANSFORM: &[(u8,usize,usize)] = &[\n'+''.join(f'    ({k},{a},{b}),\n' for k,a,b in reversed(elim))+'];\n'
text+='const OUT: [u64;21] = ['+','.join(hex(m) for m in outputs)+'];\n'
text+='const REBUILD: [(u64,u64);6] = ['+','.join(f'({hex(a)},{hex(b)})' for a,b in recompute)+'];\n'
for j,(slot,terms) in enumerate(phases):text+=f'const PHASE{j}: &[(usize,usize)] = &['+','.join(f'({a},{b})' for a,b in terms)+'];\n'
text+='const PHASES: &[(usize,&[(usize,usize)])] = &['+','.join(f'({slot},PHASE{j})' for j,(slot,terms) in enumerate(phases))+'];\n'
text+='''
fn transform(c:&mut Builder,bank:&[QubitId],back:bool) {
    let apply=|c:&mut Builder, &(kind,a,b):&(u8,usize,usize)| {
        if kind==0 { c.cx(bank[a],bank[b]); } else { c.swap(bank[a],bank[b]); }
    };
    if back { for op in TRANSFORM.iter().rev() { apply(c,op); } }
    else { for op in TRANSFORM { apply(c,op); } }
}
fn combine(raw:&[QubitId],bank:&[QubitId],mask:u64)->Lin {
    let mut value=Lin::k(mask&1!=0);
    for (i,&q) in raw.iter().enumerate() { if mask>>(i+1)&1!=0 { value=value.x(&l(q)); } }
    for (i,&q) in bank.iter().enumerate() { if mask>>(i+15)&1!=0 { value=value.x(&l(q)); } }
    value
}
fn rename(recs:&mut [Rec],old:&[QubitId],new:&[QubitId]) {
    let map=|q:QubitId| old.iter().position(|&r|r==q).map_or(q,|i|new[i]);
    let fix=|f:&mut Lin| { for q in &mut f.w { *q=map(*q); } };
    for r in recs {
        match r {
            Rec::And(q,a,b)=>{*q=map(*q);fix(a);fix(b);},
            Rec::Maj(q,a,b,ci)=>{*q=map(*q);fix(a);fix(b);fix(ci);},
            Rec::UndoC5|Rec::UndoC6=>{},
        }
    }
}
pub(super) fn run(c:&mut Builder,acc:&[QubitId],e:[QubitId;3],nm:[QubitId;3],shift:[QubitId;2],
                  cw:[QubitId;6],a4:&Lin,a5:&Lin,mut recs:Vec<Rec>)->Vec<usize> {
    assert!(Y16_CORE && !carry_loan_on());
    let work:Vec<QubitId>=recs.iter().filter_map(|r|match r {Rec::And(q,_,_)|Rec::Maj(q,_,_,_)=>Some(*q),_=>None}).collect();
    assert_eq!(work.len(),25);
    let mut bank=vec![cw[0],cw[1],cw[2],cw[3],work[0],work[1],work[2],work[3],work[4],work[5],cw[4],work[6],cw[5]];
    bank.extend_from_slice(&work[7..]);assert_eq!(bank.len(),31);
    let old=bank.clone();
    let mut raw=acc[..6].to_vec();raw.extend_from_slice(&e);raw.extend_from_slice(&nm);raw.extend_from_slice(&shift);
    // Physical majority carries to their underlying AND coordinates, top down.
    for (a,b) in [(1,2),(0,1),(6,7),(5,6),(10,12),(3,10)] {c.cx(bank[a],bank[b]);}
    transform(c,&bank,false);
    for &(slot,terms) in PHASES {
        let m=c.alloc_bit();c.hmr(bank[slot],m);
        c.push_condition(m);
        for &(a,b) in terms {
            let wire=|index:usize|if index<14 {raw[index]} else {bank[index-14]};
            c.cz(wire(a),wire(b));
        }
        c.pop_condition();c.free_bit(m);c.release_clean(bank[slot]);
    }
    let forms:Vec<Lin>=OUT.iter().map(|&m|combine(&raw,&bank,m)).collect();
    let add=field_map(&forms[..6],&forms[6..13],&forms[13],&forms[14..],acc.len());
    let (plan,lean)=fold_plan(c,acc.len(),"six-wire bank loan");assert!(!lean);
    ladder_d(c,acc,&add,6,bank[0],&plan,&[]);
    // Recompute exactly the six hidden original ANDs, charging six Toffolis.
    for (j,&(a,b)) in REBUILD.iter().enumerate() {
        let q=lin_and(c,&combine(&raw,&bank,a),&combine(&raw,&bank,b));bank[25+j]=q;
    }
    transform(c,&bank,true);
    // Restore the source's physical majority carries, bottom up.
    for (a,b) in [(0,1),(1,2),(5,6),(6,7),(3,10),(10,12)] {c.cx(bank[a],bank[b]);}
    rename(&mut recs,&old,&bank);
    fold_undo(c,recs,acc,e,a4,a5,cw);
    plan
}
'''
destination=RAW/"source/src/point_add/toffoli_bank_loan.rs"
destination.write_bytes(text.encode())
receipt={"source_baseline_lf_sha256":net["source_lf_sha256"],"helper_sha256":hashlib.sha256(text.encode()).hexdigest(),
         "constructor_ANDs":31,"regenerated_ANDs":6,"loaned_live_qubits":6,
         "phase_identity_rows":1<<14,"phase_terms":sum(len(t) for slot,t in phases),
         "linear_transform_ops_each_direction":len(elim),"status":"Native helper emitted; tests and complete consumer cost not yet checked."}
HERE.joinpath("bank-loan-emission.json").write_bytes((json.dumps(receipt,indent=2)+"\n").encode())
print(json.dumps(receipt,indent=2))
