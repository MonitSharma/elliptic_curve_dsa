//! Universal cache-stage audit. The conservative immutable Boolean Support
//! kernels and the HMR/CZ uncompute identity form the explicitly trusted base.
//! No simulated input, measurement sample, scoring packet or optimizer choice
//! is used. The log proposes leases; all semantic obligations are rechecked.
use crate::circuit::{analyze_ops,Op,OperationType as K,NO_QUBIT,NO_BIT};
use std::collections::{BTreeMap,BTreeSet,HashMap};

enum Symbolic {
    Affine(super::interned_witness::Support),
    Anf(super::interned_anf::Support),
    Retained(super::interned_anf_retained::Support),
}
impl Symbolic {
    fn new(ops:&[Op],mode:&str)->Self{match mode{
        "affine"=>Self::Affine(super::interned_witness::Support::new(ops)),
        "anf"=>Self::Anf(super::interned_anf::Support::new(ops)),
        "retained"=>Self::Retained(super::interned_anf_retained::Support::new(ops)),_=>panic!("unsupported symbolic family")}}
    fn zeros(&self)->Vec<usize>{match self{Self::Affine(s)=>s.cache_zeros(),Self::Anf(s)=>s.cache_zeros(),Self::Retained(s)=>s.cache_zeros()}}
    fn product(&mut self,o:&Op)->(bool,Vec<u64>){match self{Self::Affine(s)=>s.cache_product(o),Self::Anf(s)=>s.cache_product(o),Self::Retained(s)=>s.cache_product(o)}}
    fn step(&mut self,o:&Op){match self{Self::Affine(s)=>{s.step(o);},Self::Anf(s)=>{s.step(o);},Self::Retained(s)=>{s.step(o);}}}
}
#[derive(Clone)]
struct Lease{donor:usize,start:usize,end:usize,uses:Vec<usize>,flag:u64}
fn parse(log:&str,nb:u64)->Vec<Lease>{
    let mut flags=HashMap::new();
    let field=|line:&str,key:&str|->u64{line.split_whitespace().find_map(|x|x.strip_prefix(key)).unwrap().parse().unwrap()};
    for l in log.lines().filter(|l|l.starts_with("LAZY_FLAG ")){assert!(flags.insert(field(l,"lease=")as usize,field(l,"base=")).is_none());}
    log.lines().filter(|l|l.starts_with("LAZY_WINDOW ")).enumerate().map(|(j,l)|Lease{
        donor:field(l,"donor=")as usize,start:field(l,"start=")as usize,end:field(l,"end=")as usize,
        uses:l.split_once("uses=[").unwrap().1.trim_end_matches(']').split(',').map(|x|x.trim().parse().unwrap()).collect(),
        flag:flags.get(&j).copied().unwrap_or(nb+3*j as u64),
    }).collect()
}
fn gate(k:K,a:Option<u64>,b:Option<u64>,t:Option<u64>,bt:Option<u64>,c:Option<u64>)->Op{
    let mut o=Op::empty();o.kind=k;o.q_control1=crate::circuit::QubitId(a.unwrap_or(u64::MAX));o.q_control2=crate::circuit::QubitId(b.unwrap_or(u64::MAX));
    o.q_target=crate::circuit::QubitId(t.unwrap_or(u64::MAX));o.c_target=crate::circuit::BitId(bt.unwrap_or(u64::MAX));o.c_condition=crate::circuit::BitId(c.unwrap_or(u64::MAX));o.validate();o
}
fn store(b:u64,one:bool)->Op{gate(if one{K::BitStore1}else{K::BitStore0},None,None,None,Some(b),None)}
fn push(b:u64)->Op{gate(K::PushCondition,None,None,None,None,Some(b))}
fn pop()->Op{gate(K::PopCondition,None,None,None,None,None)}

pub(crate) fn audit(left:&[Op],right:&[Op],log:&str,mode:&str){
    let (nq,_,_,regs)=analyze_ops(left.iter());let (rq,_,_,rregs)=analyze_ops(right.iter());assert_eq!(regs,rregs);assert_eq!(nq,rq,"product audit forbids added qubits");
    let nb=left.iter().flat_map(|o|[o.c_target,o.c_condition]).filter(|b|*b!=NO_BIT).map(|b|b.0).max().map_or(0,|b|b+1);
    let plans=parse(log,nb);assert!(!plans.is_empty());
    let mut starts=HashMap::<usize,Vec<usize>>::new();let mut ends=HashMap::<usize,Vec<usize>>::new();let mut uses=HashMap::new();let mut last_at=HashMap::<usize,Vec<usize>>::new();
    let mut boundaries=vec![false;left.len()+1];let mut depth=0usize;
    for (i,o) in left.iter().enumerate(){boundaries[i]=depth==0;match o.kind{K::PushCondition=>depth+=1,K::PopCondition=>depth=depth.checked_sub(1).expect("scope underflow"),_=>{}}}
    assert_eq!(depth,0);boundaries[left.len()]=true;
    let mut flag_intervals=BTreeMap::<u64,Vec<(usize,usize)>>::new();
    for (j,p) in plans.iter().enumerate(){
        assert!(p.donor<nq as usize&&p.start<p.end&&p.end<=left.len());
        assert!(boundaries[p.start]&&boundaries[p.end],"private flags must reset at top-level boundaries");
        assert!(p.uses.len()>=2&&p.uses.windows(2).all(|w|w[0]<w[1]));
        assert!(p.start<=p.uses[0]&&*p.uses.last().unwrap()<p.end);assert!(p.flag>=nb&&p.flag.checked_add(2).is_some());
        starts.entry(p.start).or_default().push(j);ends.entry(p.end).or_default().push(j);last_at.entry(*p.uses.last().unwrap()).or_default().push(j);
        for &at in &p.uses{assert!(uses.insert(at,j).is_none());assert_eq!(left[at].kind,K::CCX);}
        for b in p.flag..p.flag+3{flag_intervals.entry(b).or_default().push((p.start,p.end));}
    }
    for intervals in flag_intervals.values_mut(){intervals.sort_unstable();assert!(intervals.windows(2).all(|w|w[0].1<=w[1].0),"private flag leases overlap");}
    // A conservative raw-write fence proves the final controls have precisely
    // the values they had at the last use, through every cleanup boundary.
    let mut next=vec![usize::MAX;nq as usize];
    for (i,o) in left.iter().enumerate().rev(){
        if let Some(js)=last_at.get(&i){for &j in js{for q in [o.q_control1,o.q_control2]{assert!(next[q.0 as usize]>=plans[j].end,"cleanup control overwritten");}}}
        match o.kind{K::X|K::CX|K::CCX|K::R|K::Hmr=>next[o.q_target.0 as usize]=i,K::Swap=>{next[o.q_target.0 as usize]=i;next[o.q_control1.0 as usize]=i;},_=>{}}
    }
    let mut state=Symbolic::new(left,mode);let mut product=HashMap::new();let mut live=HashMap::new();let mut skipped=0;let mut cursor=0;
    let mut emit=|o:Op|{assert_eq!(right.get(cursor),Some(&o),"rendered row differs at {cursor}");cursor+=1;};
    for i in 0..=left.len(){
        if let Some(js)=ends.get(&i){for &j in js{
            let p=&plans[j];let o=left[*p.uses.last().unwrap()];
            emit(push(p.flag));emit(gate(K::Hmr,None,None,Some(p.donor as u64),Some(p.flag+2),None));
            emit(gate(K::CZ,Some(o.q_control1.0),None,Some(o.q_control2.0),None,Some(p.flag+2)));emit(pop());
            for b in p.flag..p.flag+3{emit(store(b,false));}assert_eq!(live.remove(&p.donor),Some(j));
        }}
        if let Some(js)=starts.get(&i){let zeros:BTreeSet<_>=state.zeros().into_iter().collect();for &j in js{
            let p=&plans[j];assert!(zeros.contains(&p.donor),"donor not universally zero at lease start");assert!(live.insert(p.donor,j).is_none(),"quantum donor leases overlap");
            for b in p.flag..p.flag+3{emit(store(b,false));}
        }}
        if i==left.len(){break;}let o=left[i];
        for q in [o.q_control1,o.q_control2,o.q_target].into_iter().filter(|q|*q!=NO_QUBIT){
            if live.contains_key(&(q.0 as usize)){assert!(o.kind==K::R&&o.q_target==q,"original input touches a borrowed donor");}
        }
        // Query every CCX, matching the conservative kernel's allocation order;
        // the allocator/ranking/proposal generator is never called here.
        let current=if o.kind==K::CCX{Some(state.product(&o))}else{None};
        if let Some(&j)=uses.get(&i){
            if let Some(expected)=product.get(&j){assert_eq!(current.as_ref().unwrap(),expected,"cache functions differ across uses");}else{product.insert(j,current.clone().unwrap());}
            let p=&plans[j];let v=p.flag;
            if o.c_condition!=NO_BIT{emit(push(o.c_condition.0));}
            emit(store(v+1,true));emit(gate(K::BitInvert,None,None,None,Some(v+1),Some(v)));emit(push(v+1));
            emit(gate(K::CCX,Some(o.q_control1.0),Some(o.q_control2.0),Some(p.donor as u64),None,None));emit(store(v,true));emit(pop());
            emit(gate(K::CX,Some(p.donor as u64),None,Some(o.q_target.0),None,None));emit(store(v+1,false));if o.c_condition!=NO_BIT{emit(pop());}
        }else if o.kind==K::R&&live.contains_key(&(o.q_target.0 as usize)){skipped+=1;}else{emit(o);}
        state.step(&o);
    }
    assert!(live.is_empty());assert_eq!(cursor,right.len());assert_eq!(product.len(),plans.len());
    println!("UNIVERSAL_CACHE_CERTIFICATE_PASS family={mode} leases={} uses={} skipped_zero_resets={skipped} input_ops={} output_ops={} private_flag_slots={} no_simulated_inputs=true",plans.len(),uses.len(),left.len(),right.len(),flag_intervals.len());
}

#[cfg(test)]
mod tests{
    use super::*;
    fn fixture()->(Vec<Op>,Vec<Op>,String,usize){
        let mut p=vec![];let mut r=Op::empty();r.kind=K::Register;r.r_target=crate::circuit::RegisterId(0);p.push(r);
        for q in [0,1,2,4]{let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=r.r_target;o.q_target=crate::circuit::QubitId(q);p.push(o);}
        for b in 0..2{let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=r.r_target;o.c_target=crate::circuit::BitId(b);p.push(o);}
        p.push(gate(K::R,None,None,Some(3),None,None));let n=p.len();
        p.push(gate(K::CCX,Some(0),Some(1),Some(2),None,Some(0)));p.push(gate(K::CCX,Some(0),Some(1),Some(2),None,Some(1)));
        let log=format!("LAZY_WINDOW donor=3 start={n} end={} proxy=0 uses=[{n}, {}]\nLAZY_FLAG lease=0 base=2\n",n+2,n+1);
        let mut q=p[..n].to_vec();for b in 2..5{q.push(store(b,false));}
        for guard in 0..2{
            q.extend([push(guard),store(3,true),gate(K::BitInvert,None,None,None,Some(3),Some(2)),push(3),gate(K::CCX,Some(0),Some(1),Some(3),None,None),store(2,true),pop(),gate(K::CX,Some(3),None,Some(2),None,None),store(3,false),pop()]);
        }
        q.extend([push(2),gate(K::Hmr,None,None,Some(3),Some(4),None),gate(K::CZ,Some(0),None,Some(1),None,Some(4)),pop(),store(2,false),store(3,false),store(4,false)]);
        (p,q,log,n)
    }
    fn rejected(p:&[Op],q:&[Op],log:&str){assert!(std::panic::catch_unwind(||audit(p,q,log,"retained")).is_err());}
    #[test]fn accepts_all_three_conservative_kernels(){let(p,q,l,_)=fixture();for m in ["affine","anf","retained"]{audit(&p,&q,&l,m);}}
    #[test]fn rejects_changed_boolean_function(){let(mut p,q,l,n)=fixture();p[n+1].q_control2=crate::circuit::QubitId(4);rejected(&p,&q,&l);}
    #[test]fn rejects_unknown_donor(){let(mut p,mut q,l,_)=fixture();p[4].q_target=crate::circuit::QubitId(3);q[4]=p[4];p.remove(7);q.remove(7);let l=l.replace("start=8","start=7").replace("end=10","end=9").replace("[8, 9]","[7, 8]");rejected(&p,&q,&l);}
    #[test]fn rejects_cleanup_control_write(){let(mut p,q,l,n)=fixture();p.push(gate(K::X,None,None,Some(0),None,None));let l=l.replace(&format!("end={}",n+2),&format!("end={}",n+3));rejected(&p,&q,&l);}
    #[test]fn rejects_private_flag_alias(){let(p,q,l,_)=fixture();rejected(&p,&q,&l.replace("base=2","base=0"));}
    #[test]fn rejects_phase_twin_fault(){let(p,mut q,l,_)=fixture();let o=q.iter_mut().find(|o|o.kind==K::CZ).unwrap();o.c_condition=NO_BIT;rejected(&p,&q,&l);}
    #[test]fn rejects_non_top_level_reset(){let(mut p,q,l,n)=fixture();p.insert(n,push(0));p.push(pop());let l=l.replace(&format!("start={n}"),&format!("start={}",n+1)).replace(&format!("end={}",n+2),&format!("end={}",n+3)).replace(&format!("[{n}, {}]",n+1),&format!("[{}, {}]",n+1,n+2));rejected(&p,&q,&l);}
    #[test]fn rejects_original_phase_touch_of_donor(){let(mut p,q,l,n)=fixture();p.insert(n+1,gate(K::CZ,Some(3),None,Some(4),None,None));let l=l.replace(&format!("end={}",n+2),&format!("end={}",n+3)).replace(&format!("[{n}, {}]",n+1),&format!("[{n}, {}]",n+2));rejected(&p,&q,&l);}
}
