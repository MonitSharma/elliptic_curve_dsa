"""Matched documented unbound allocator mode, with/without full square assembly carry."""
from pathlib import Path
import sys
folder=Path(__file__).parent;base=folder/'source/point_add'
for label,full in [('unbound-base',False),('unbound-full-cross',True)]:
 out=folder/(label+'-source');out.mkdir(exist_ok=True)
 s=(folder/'raw-handoff-source/builder.rs').read_text().replace('/product-evidence/raw-handoff/raw-ops.bin',f'/product-evidence/{label}/raw-ops.bin')
 out.joinpath('builder.rs').write_text(s,newline='\n')
 s=(folder/'raw-handoff-source/leapfrog.rs').read_text()
 for before,after in [('pub(crate) const Y42_UNBOUND: bool = false;','pub(crate) const Y42_UNBOUND: bool = true;'),('pub(crate) const Y42_ALLOC: bool = Y42;','pub(crate) const Y42_ALLOC: bool = false;')]:
  assert s.count(before)==1;s=s.replace(before,after)
 needle='    eprintln!("SQUARE_R0_WIRES {:?}", r0.iter().map(|q|q.0).collect::<Vec<_>>());'
 new='    eprintln!("UNBOUND_SETTINGS y42_unbound={} y42_alloc={} sq_asm_tail={:?}", Y42_UNBOUND, Y42_ALLOC, super::optional_env::<usize>("SQ_ASM_TAIL"));\n'+needle
 assert s.count(needle)==1;s=s.replace(needle,new)
 out.joinpath('leapfrog.rs').write_text(s,newline='\n')
 s=base.joinpath('square.rs').read_bytes()
 if full:
  needle=b'    let acc=match super::optional_env::<usize>("SQ_ASM_TAIL"){Some(e)=>&full[..full.len().min(cross.len()+e)],None=>full};'
  assert s.count(needle)==1
  s=s.replace(needle,b'    // Exact diagnostic: retain the full assembly carry path.\n    let acc=full;')
 out.joinpath('square.rs').write_bytes(s)
