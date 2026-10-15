"""Keep the prior packed benchmark frozen; stream only needed Fiat input bytes."""
from pathlib import Path
import shutil,subprocess,sys
root=Path(__file__).resolve().parent;old=root.parent/'packed-witness-20261016'
tool=root/'tool';(tool/'src').mkdir(parents=True,exist_ok=True)
for name in ['Cargo.toml','Cargo.lock']:shutil.copyfile(old/'tool'/name,tool/name)
for path in (old/'tool/src').glob('*.rs'):shutil.copyfile(path,tool/'src'/path.name)
source=(old/'packed_body.rs').read_text()
source=source.replace('struct CandidatePacket{packet:Packet,','struct CandidatePacket{packet:LazyPacket,')
start=source.index('fn prepare_packets(');end=source.index('struct ZeroReader;',start)
replacement=r'''
struct LazyPacket{reader:sha3::Shake256Reader,next:usize,batches:Vec<Vec<PointTriple>>}
impl LazyPacket{
 fn ensure(&mut self,batch:usize,curve:&FastCurveC)->bool{
  while self.batches.len()<=batch{let mut pts=Vec::with_capacity(64);
   while pts.len()<64&&self.next<NUM_TESTS{let count=(64-pts.len()).min(NUM_TESTS-self.next);let mut raw=vec![0u8;count*64];XofReader::read(&mut self.reader,&mut raw);let mut scalars=Vec::with_capacity(count*2);
    for r in raw.chunks_exact(64){scalars.push(U256::from_le_slice(&r[..32]));scalars.push(U256::from_le_slice(&r[32..]));}self.next+=count;
    for(t,o,e)in curve.points_with_sums(&scalars){if t.0!=o.0&&!(t.0.is_zero()&&t.1.is_zero())&&!(o.0.is_zero()&&o.1.is_zero()){pts.push((t,o,e));}}
   }if pts.is_empty(){return false;}self.batches.push(pts);
  }true
 }
}
fn prepare_packets(_base:&Shake8,hash:&Shake256,tail:&[Op],nonces:[u64;8],valid:[bool;8])->Vec<CandidatePacket>{
 let mut result=Vec::new();for j in 0..8{if !valid[j]{continue;}let mut h=hash.clone();for op in nonce_tail(tail,nonces[j]){h.update(&record49(&op));}
  let reader=h.finalize_xof();result.push(CandidatePacket{packet:LazyPacket{reader,next:0,batches:Vec::new()},nonce:nonces[j],scan_batch:0,candidates:Vec::new(),cursor:0,attempts:0});
 }result
}
'''
source=source[:start]+replacement+source[end:]
(root/'generated-packed_body.rs').write_text(source);(tool/'src/packed_body.rs').write_text(source)
