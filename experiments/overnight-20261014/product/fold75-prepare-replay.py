"""Exact open-ripple value frames for source-specific internal fold observers."""
from pathlib import Path
import subprocess,sys
base,dest,archive=map(Path,sys.argv[1:4])
subprocess.run([sys.executable,str(Path(__file__).with_name('prepare-walk-replay.py')),str(base),str(dest),str(archive)],check=True)
s=(dest/'src/main.rs').read_text()
s=s.replace('struct Frame{scope:', 'struct Frame{sp2:usize,cc:Vec<usize>,etop:Vec<usize>,comp:bool,open:bool,scope:')
start=s.index('  let mut frames=Vec::new();')
end=s.index('  for(packet,mode)',start)
s=s[:start]+r'''
  let mut frames=Vec::new();for line in std::fs::read_to_string(if source=="c5_raw"{&a[10]}else{&a[11]}).unwrap().lines(){let v:Vec<_>=line.split('\t').collect();assert_eq!(v.len(),11);let ids=|i:usize|if v[i]=="-"{Vec::new()}else{v[i].split(',').map(|x|x.parse::<usize>().unwrap()).collect()};frames.push(Frame{scope:"div".into(),label:v[0].into(),t:v[1].parse().unwrap(),end:v[2].parse().unwrap(),lowrel:false,skip:false,r:[Vec::new(),Vec::new()],p:[ids(3),ids(4)],letter:ids(5),sp2:v[6].parse().unwrap(),cc:ids(7),etop:ids(8),comp:v[9]=="true",open:v[10]=="true"});}
  assert_eq!(frames.len(),8);assert!(frames.windows(2).all(|w|w[0].end<=w[1].end));assert!(frames.last().unwrap().end<pre.len());
''' +s[end:]
helpers=r'''
fn open_value(q:&[u64],frame:&Frame,lane:usize)->U256{let mut x=readq(q,&frame.p[0],lane);if frame.open{for i in frame.sp2+2..frame.p[0].len(){if ((q[frame.p[1][i-2]]^q[frame.cc[i-2-frame.sp2]])>>lane)&1!=0{x^=U256::from(1)<<i;}}}x}
#[cfg(test)]mod open_tests{use super::*;
 #[test]fn open_ripple_snapshot(){let mut q=vec![0u64;18];q[5]=u64::MAX;q[8+3]=u64::MAX;q[16]=u64::MAX;
 let mut f=Frame{scope:"div".into(),label:"fixture".into(),t:75,end:0,lowrel:false,skip:false,r:[vec![],vec![]],p:[(0..8).collect(),(8..16).collect()],letter:vec![],sp2:2,cc:vec![16,17,17,17,17,17,17],etop:vec![],comp:false,open:true};
 assert_eq!(open_value(&q,&f,0),U256::from(16));f.cc[0]=17;assert_eq!(open_value(&q,&f,0),U256::ZERO,"fault stale carry toggles reconstructed bit4");}
}
'''
s=s.replace('fn main(){use sha3::Digest;',helpers+'\nfn main(){use sha3::Digest;')
needle='      println!("PRODUCT_WALK_FRAME'
start=s.index(needle);end=s.index('\n',start)
line=s[start:end]
line=line.replace('skip={} phase={}', 'skip={} phase={} open_x={:#x} overflow={:#x} b_complemented={} open_ripple={} sp2={}')
line=line.replace('frame.skip,(sim.phase>>lane)&1);','frame.skip,(sim.phase>>lane)&1,open_value(&logical_q,frame,lane),readq(&logical_q,&frame.etop,lane),frame.comp,frame.open,frame.sp2);')
s=s[:start]+line+s[end:]
s=s.replace('PRODUCT_WALK_', 'PRODUCT_FOLD_')
(dest/'src/main.rs').write_text(s,newline='\n')
