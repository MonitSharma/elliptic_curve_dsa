"""Replay exact source-bound tick frames; export raw integers for independent model."""
from pathlib import Path
import subprocess,sys
base,dest,archive=map(Path,sys.argv[1:4])
subprocess.run([sys.executable,str(Path(__file__).with_name('prepare-body-prefix-replay-v2.py')),str(base),str(dest),str(archive)],check=True)
s=(dest/'src/main.rs').read_text()
s=s.replace('a.len(),10,','a.len(),12,')
helpers=r'''
struct Frame{scope:String,label:String,t:usize,end:usize,lowrel:bool,skip:bool,r:[Vec<usize>;2],p:[Vec<usize>;2],letter:Vec<usize>}
fn full_word(q:&[u64],ids:&[usize],lane:usize,lowrel:bool)->alloy_primitives::U512{
 assert!(ids.len()+usize::from(lowrel)<512);let mut n=alloy_primitives::U512::from(usize::from(lowrel));for(i,&id)in ids.iter().enumerate(){if(q[id]>>lane)&1!=0{n|=alloy_primitives::U512::from(1)<<(i+usize::from(lowrel));}}n
}
#[cfg(test)]mod frame_tests{use super::*;
 #[test]fn implicit_odd_signed_word(){let q=[0,u64::MAX];assert_eq!(full_word(&q,&[0,1],0,true),alloy_primitives::U512::from(5));assert_eq!(full_word(&q,&[1,1],0,true),alloy_primitives::U512::from(7));assert_eq!(full_word(&q,&[0],0,false),alloy_primitives::U512::ZERO);}
}
'''
s=s.replace('fn main(){use sha3::Digest;',helpers+'\nfn main(){use sha3::Digest;')
at=s.index('  for(packet,mode)')
parse=r'''
  let mut frames=Vec::new();for line in std::fs::read_to_string(if source=="c5_raw"{&a[10]}else{&a[11]}).unwrap().lines(){let v:Vec<_>=line.split('\t').collect();assert_eq!(v.len(),11);let ids=|i:usize|if v[i]=="-"{Vec::new()}else{v[i].split(',').map(|x|x.parse::<usize>().unwrap()).collect()};frames.push(Frame{scope:v[0].into(),label:v[1].into(),t:v[2].parse().unwrap(),end:v[3].parse().unwrap(),lowrel:v[4]=="true",skip:v[5]=="true",r:[ids(6),ids(7)],p:[ids(8),ids(9)],letter:ids(10)});}
  assert!(frames.windows(2).all(|w|w[0].end<=w[1].end));assert!(frames.last().unwrap().end<pre.len());
'''
s=s[:at]+parse+s[at:]
start=s.index('    for b in &boundaries{let old_end=b.end;')
mid=s.index('    let mut logical_q=',start)
mapping=s[start:mid].replace('for b in &boundaries','for (seq,frame) in frames.iter().enumerate()').replace('let old_end=b.end','let old_end=frame.end')
end=s.index('   }\n  }\n }\n println!',mid)
body=r'''
    let mut logical_q=sim.qubits.clone();for(&q,&v)in &logical{logical_q[q]=v;}
    for(lane,(index,_))in cases.iter().enumerate(){if mode=="independent"&&*index!=94{continue;}
      let rail=|i:usize|if frame.r[i].is_empty(){"-".into()}else{format!("{:#x}",full_word(&logical_q,&frame.r[i],lane,frame.lowrel))};
      let payload=|i:usize|if frame.p[i].is_empty(){"-".into()}else{format!("{:#x}",readq(&logical_q,&frame.p[i],lane))};
      let letter=if frame.letter.is_empty(){"-".into()}else{frame.letter.iter().map(|&q|((logical_q[q]>>lane)&1).to_string()).collect::<Vec<_>>().join("")};
      println!("PRODUCT_WALK_FRAME source={source} mode={mode} batch={batch} index={index} seq={seq} scope={} label={} t={} old_end={} final_end={final_at} pending_y33={} r0={} r1={} r0_width={} r1_width={} p0={} p1={} letter={letter} skip={} phase={} score=NONE",frame.scope,frame.label,frame.t,frame.end,logical.len(),rail(0),rail(1),if frame.r[0].is_empty(){0}else{frame.r[0].len()+usize::from(frame.lowrel)},if frame.r[1].is_empty(){0}else{frame.r[1].len()+usize::from(frame.lowrel)},payload(0),payload(1),frame.skip,(sim.phase>>lane)&1);
    }
    }
    sim.apply_iter(ops[final_at..].iter());for(lane,(index,_))in cases.iter().enumerate(){let x=sim.get_register(&regs[0],lane);let y=sim.get_register(&regs[1],lane);let phase=(sim.phase>>lane)&1;assert_eq!((x,y,phase),archived[&(source.to_string(),mode.to_string(),*index)],"entire final raw values/phase equal independent archived replay");}
    eprintln!("PRODUCT_WALK_FINAL_GUARD source={source} mode={mode} batch={batch} shots={} archived_full_raw_values_and_phase_equal=true frames={} score=NONE",cases.len(),frames.len());
'''
s=s[:start]+mapping+body+s[end:]
s=s.replace('PRODUCT_BODY_TOTAL','PRODUCT_WALK_TOTAL')
(dest/'src/main.rs').write_text(s,newline='\n')
