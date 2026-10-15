from pathlib import Path
import shutil
root=Path(__file__).resolve().parent;old=root.parent/'zero-mr-slice-20261016';tool=root/'tool'
shutil.copytree(old/'tool/src',tool/'src',dirs_exist_ok=True)
for name in ['Cargo.toml','Cargo.lock','zero8.c','simd8wide.h','build.rs']:shutil.copyfile(old/'tool'/name,tool/name)
s=(tool/'src/main.rs').read_text()
query=r'''
fn selected_output_bits()->&'static Vec<usize>{
 static SELECTED:std::sync::OnceLock<Vec<usize>>=std::sync::OnceLock::new();
 SELECTED.get_or_init(||{
  let path="/home/hclau/ecdsa_research/prefilter-20261015/evidence/mr-mask-tip-v3.bin";
  let digest=std::process::Command::new("sha256sum").arg(path).output().unwrap();assert!(digest.status.success());assert_eq!(String::from_utf8(digest.stdout).unwrap().split_whitespace().next().unwrap(),"560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d");
  let data=fs::read(path).unwrap();assert_eq!(&data[..8],b"MRMASK01");let w=|i|u64::from_le_bytes(data[i..i+8].try_into().unwrap())as usize;let n=w(8);assert_eq!(n,7_914_981);assert_eq!((w(16),w(24)),(1024,512));assert_eq!(data.len(),32+16*n+512*4);
  let mut selected=Vec::new();for(bit,raw)in data[32+16*n..].chunks_exact(4).enumerate(){let node=u32::from_le_bytes(raw.try_into().unwrap())as usize;assert!(node<n);let kind=u32::from_le_bytes(data[32+16*node..36+16*node].try_into().unwrap());if kind!=1{assert_eq!(kind,5);selected.push(bit);}}
  assert_eq!(selected.len(),49);assert!(selected.iter().all(|b|*b>=309&&*b<=374));println!("MASK_BOUND_SELECTED_OUTPUTS bits={selected:?} constant1_other_roots=463");selected
 })
}
fn query_outputs(regs:&[Vec<QubitOrBit>])->Vec<&QubitOrBit>{
 if regs.len()>=2&&regs[0].len()==256&&regs[1].len()==256{selected_output_bits().iter().map(|bit|&regs[bit/256][bit%256]).collect()}else{regs[..2].iter().flat_map(|r|r.iter()).collect()}
}
'''
s=s.replace('fn slice(',query+'\nfn slice(',1)
start=s.index(' let mut qlive=vec![false;nq];');end=s.index(' let mut keep=',start)
s=s[:start]+''' let mut qlive=vec![false;nq]; let mut blive=vec![false;nb];
 for w in query_outputs(regs){match w{QubitOrBit::Qubit(id)=>qlive[id.0 as usize]=true,QubitOrBit::Bit(id)=>blive[id.0 as usize]=true,}}
'''+s[end:]
start=s.index('fn same_outputs(');end=s.index('// A separate research-only opcode range',start)
s=s[:start]+'''fn same_outputs(aq:&[u64],ab:&[u64],bq:&[u64],bb:&[u64],regs:&[Vec<QubitOrBit>]) {
 for w in query_outputs(regs){for j in 0..8{match w{QubitOrBit::Qubit(id)=>assert_eq!(aq[id.0 as usize*8+j],bq[id.0 as usize*8+j]),QubitOrBit::Bit(id)=>assert_eq!(ab[id.0 as usize*8+j],bb[id.0 as usize*8+j]),}}}
}
'''+s[end:]
s=s.replace('outputs=registers0and1','outputs=49mask-certifiable-bits').replace('SLICE_VERIFIED shots=512 output_registers0and1=true','SLICE_VERIFIED shots=512 queried49outputs=true')
needle='fs::write(format!("{}.tsv",a[3]),meta).unwrap();'
assert s.count(needle)==1
s=s.replace(needle,'meta.push_str(&format!("queried_flat_bits\\t{:?}\\nother_outputs_not_certified\\ttrue\\n",selected_output_bits()));'+needle)
(tool/'src/main.rs').write_text(s)
