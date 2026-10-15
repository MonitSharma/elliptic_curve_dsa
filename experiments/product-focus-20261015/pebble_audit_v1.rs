use crate::circuit::{Op,OperationType as K,NO_QUBIT,NO_BIT};

fn reads(o:&Op)->Vec<usize>{
    [o.q_control1,o.q_control2,o.q_target].into_iter().filter(|q|*q!=NO_QUBIT).map(|q|q.0 as usize).collect()
}
fn writes(o:&Op)->Vec<usize>{
    match o.kind {
        K::X|K::CX|K::CCX|K::Hmr|K::R=>vec![o.q_target.0 as usize],
        K::Swap=>vec![o.q_control1.0 as usize,o.q_target.0 as usize],
        _=>vec![]
    }
}
#[derive(Clone,Copy,Debug)]
struct Product {a:usize,b:usize,va:u64,vb:u64}

pub fn audit(ops:&[Op]) {
    let nq=ops.iter().flat_map(reads).max().unwrap()+1;
    let top=nq-1;
    let mut depth=0usize;
    let mut begin=None;
    let mut spans=vec![];
    let mut abi=vec![false;nq];
    for (i,o) in ops.iter().enumerate(){
        if o.kind==K::AppendToRegister && o.q_target!=NO_QUBIT {abi[o.q_target.0 as usize]=true;}
        if reads(o).contains(&top){
            let s=*begin.get_or_insert(i);
            if matches!(o.kind,K::Hmr|K::R) && depth==0 && o.c_condition==NO_BIT {spans.push((s,i));begin=None;}
        }
        if o.kind==K::PushCondition {depth+=1;} else if o.kind==K::PopCondition {depth-=1;}
    }
    if let Some(s)=begin {spans.push((s,ops.len()-1));}
    println!("PEBBLE top={top} spans={}",spans.len());
    let mut nexttouch=vec![usize::MAX;nq]; let mut nextwrite=nexttouch.clone();
    let mut snapshots=std::collections::HashMap::new();
    let starts:std::collections::HashSet<_>=spans.iter().map(|s|s.0).collect();
    for (i,o) in ops.iter().enumerate().rev(){
        for q in reads(o){nexttouch[q]=i;}
        for q in writes(o){nextwrite[q]=i;}
        if starts.contains(&i) {snapshots.insert(i,(nexttouch.clone(),nextwrite.clone()));}
    }
    let mut zero:Vec<bool>=abi.iter().map(|x|!*x).collect();
    let mut vers=vec![0u64;nq];let mut prod=vec![None::<Product>;nq];
    let ends:std::collections::HashMap<_,_>=spans.iter().copied().collect();
    depth=0;let mut admitted=0;
    for (i,o) in ops.iter().enumerate(){
        if let Some(&end)=ends.get(&i){
            let (nt,nw)=&snapshots[&i];let mut choices=vec![];
            for q in 0..top {
                if abi[q]||nt[q]<=end {continue;}
                if let Some(p)=prod[q] {
                    if p.a==top||p.b==top||nw[p.a]<=end||nw[p.b]<=end {continue;}
                    if vers[p.a]==p.va&&vers[p.b]==p.vb {choices.push((q,p));}
                }
            }
            if !choices.is_empty()&&zero[top]&&depth==0 {admitted+=1;}
            println!("PEBBLE_SPAN start={i} end={end} len={} zero={} depth={depth} choices={choices:?}",end-i+1,zero[top]);
        }
        let unconditional=depth==0&&o.c_condition==NO_BIT;
        match o.kind {
            K::PushCondition=>depth+=1,
            K::PopCondition=>depth-=1,
            K::CCX=>{
                let t=o.q_target.0 as usize;let a=o.q_control1.0 as usize;let b=o.q_control2.0 as usize;
                let prior=prod[t];
                let cancellation=prior.is_some_and(|p|((p.a==a&&p.b==b&&p.va==vers[a]&&p.vb==vers[b])||(p.a==b&&p.b==a&&p.va==vers[b]&&p.vb==vers[a])));
                prod[t]=if unconditional&&zero[t] {Some(Product{a,b,va:vers[a],vb:vers[b]})}else{None};
                zero[t]=unconditional&&cancellation;vers[t]+=1;
            }
            K::Hmr|K::R=>{let t=o.q_target.0 as usize;zero[t]=unconditional;prod[t]=None;vers[t]+=1;}
            K::X|K::CX|K::Swap=>for q in writes(o){zero[q]=false;prod[q]=None;vers[q]+=1;},
            _=>{}
        }
    }
    println!("PEBBLE_SUMMARY spans={} admitted={admitted} all={}",spans.len(),admitted==spans.len());
}
