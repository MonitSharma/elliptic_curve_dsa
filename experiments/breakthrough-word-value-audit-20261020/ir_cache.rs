use super::{Program,Node,Expr,QX,QCX,QCCX,QSWAP,QZERO,CINV,CZERO,CONE,CRNG};
fn take<const N:usize>(b:&[u8],at:&mut usize)->Result<[u8;N],&'static str>{let end=at.checked_add(N).ok_or("overflow")?;let x=b.get(*at..end).ok_or("truncated")?.try_into().unwrap();*at=end;Ok(x)}
fn u32le(b:&[u8],at:&mut usize)->Result<u32,&'static str>{Ok(u32::from_le_bytes(take(b,at)?))}
pub(super)fn decode(b:&[u8],source_ops:usize)->Result<(Program,Vec<usize>),&'static str>{
 let mut at=0;if take::<8>(b,&mut at)?!=*b"VALUEIR1"{return Err("magic");}let mut h=[0usize;8];for x in &mut h{*x=usize::try_from(u64::from_le_bytes(take(b,&mut at)?)).map_err(|_|"size")?;}
 let[nq,nb,versions,rng,ni,ng,nn,no]=h;
 if nq==0||nq>10000||nb>100000||versions<nb||versions>2000000||rng>2000000||ni>nq||ng==0||ng>2000000||nn>20000000||no>nq{return Err("bounds");}
 let mut inputs=Vec::with_capacity(ni);for _ in 0..ni{let q=u32le(b,&mut at)?as usize;if q>=nq{return Err("input");}inputs.push(q);}
 let mut outputs=Vec::with_capacity(no);for _ in 0..no{let q=u32le(b,&mut at)?as usize;if q>=nq{return Err("output");}outputs.push(q);}
 let mut guards=Vec::with_capacity(ng);let mut total=0usize;for _ in 0..ng{let len=u32le(b,&mut at)?as usize;total=total.checked_add(len).ok_or("guard sum")?;if len>versions||total>100000000{return Err("guard bound");}let mut row=Vec::with_capacity(len);for _ in 0..len{let v=u32le(b,&mut at)?;if v as usize>=versions{return Err("guard version");}row.push(v);}guards.push(row);}
 if !guards[0].is_empty(){return Err("unconditional guard");}
 let mut nodes=Vec::with_capacity(nn);for _ in 0..nn{let k=take::<1>(b,&mut at)?[0];let mut v=[0;6];for x in &mut v{*x=u32le(b,&mut at)?;}let[a,bb,t,g,r,source]=v;if g as usize>=ng||source as usize>=source_ops{return Err("node metadata");}
  match k{QX|QCX|QCCX|QSWAP|QZERO=>{if t as usize>=nq{return Err("quantum target");}if matches!(k,QCX|QCCX|QSWAP)&&a as usize>=nq{return Err("quantum control");}if k==QCCX&&bb as usize>=nq{return Err("second control");}},CINV|CZERO|CONE|CRNG=>{if t as usize>=versions||a as usize>=versions{return Err("classical version");}if k==CRNG&&r as usize>=rng{return Err("random slot");}},_=>return Err("opcode")}
  nodes.push(Node{k,a,b:bb,t,g,r,source});
 }
 if at!=b.len(){return Err("trailing bytes");}
 Ok((Program{symbols:vec![],expr:Expr::default(),guard_exprs:vec![],inputs,nodes,guards,nq,nb,versions,rng,certified_zero_resets:0},outputs))
}
#[cfg(test)]mod tests{use super::*;
 fn fixture()->Vec<u8>{let mut b=b"VALUEIR1".to_vec();for v in[3u64,2,3,1,2,1,1,2]{b.extend_from_slice(&v.to_le_bytes());}for v in[0u32,1,0,1,0]{b.extend_from_slice(&v.to_le_bytes());}b.push(QX);for v in[u32::MAX,u32::MAX,2,0,u32::MAX,0]{b.extend_from_slice(&v.to_le_bytes());}b}
 #[test]fn compact_cache_decodes_fields_without_native_struct_layout(){let(p,outputs)=decode(&fixture(),1).unwrap();assert_eq!((p.nq,p.nb,p.versions,p.rng),(3,2,3,1));assert_eq!(p.inputs,vec![0,1]);assert_eq!(outputs,vec![0,1]);assert_eq!(p.nodes[0].t,2);assert_eq!(p.nodes[0].k,QX);}
 #[test]fn malformed_cache_never_becomes_a_verified_program(){let b=fixture();for end in 0..b.len(){assert!(decode(&b[..end],1).is_err());}let mut extra=b.clone();extra.push(0);assert!(decode(&extra,1).is_err());let mut bad=b;bad[0]=0;assert!(decode(&bad,1).is_err());}
}
