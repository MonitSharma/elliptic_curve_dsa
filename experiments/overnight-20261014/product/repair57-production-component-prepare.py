"""Exact original104 entry pool, full source body replacement56->57."""
from pathlib import Path
import json,subprocess,sys
base,out,manifest,frames,kernel,pool,loader=map(Path,sys.argv[1:]);subprocess.run([sys.executable,str(Path(__file__).with_name('repair57-component-r2-prepare.py')),str(base),str(out),str(manifest),str(frames),str(kernel)],check=True)
r=json.loads((pool/'before.json').read_text());a=json.loads((pool/'after.json').read_text());assert r['label']=='before' and a['label']=='after'
ids=lambda a:'&['+','.join(map(str,a))+']'
head='const BODY_NQ:usize=%d;const BODY_NB:usize=%d;\n'%tuple(r['dims'])
for name,values in [('BODY_P0',r['p'][0]),('BODY_P1',r['p'][1]),('BODY_LETTER',r['letter']),('BODY_FQ',r['freeq']),('BODY_FB',r['freeb']),('BODY_EXIT_FQ',a['freeq']),('BODY_EXIT_FB',a['freeb'])]:head+='const '+name+':&[u64]='+ids(values)+';\n'
source=loader.read_text();start=source.index('const MAGIC:');stop=source.index('// ─── secp256k1 parameters');loadsource=source[start:stop]
s=(out/'product_repair57_tests.rs').read_text();s=head+'use std::fs::File;use std::io::{Read,BufReader};use crate::circuit::{BitId,RegisterId};\n'+loadsource+s
s=s.replace('for widths in[(57,56)]','for widths in[(56,56),(57,56)]')
needle='let abi=c.alloc_qubits(512);let _bs=c.alloc_bits(512);let source=c.alloc_qubits(256);let letter=c.alloc_qubits(5);let mut p=[abi[256..].to_vec(),source.clone()];'
assert s.count(needle)==1;s=s.replace(needle,'let all=c.alloc_qubits(BODY_NQ);let bs=c.alloc_bits(BODY_NB);for &i in BODY_FQ{c.release_clean(all[i as usize]);}for &i in BODY_FB{c.free_bit(bs[i as usize]);}let abi=all[..512].to_vec();let mut p=[BODY_P0.iter().map(|&i|QubitId(i)).collect::<Vec<_>>(),BODY_P1.iter().map(|&i|QubitId(i)).collect::<Vec<_>>()];let source=p[1].clone();let letter=BODY_LETTER.iter().map(|&i|QubitId(i)).collect::<Vec<_>>();let target=p[0].clone();')
s=s.replace('let forward=c.op_count();rev_tick','let forward=c.op_count();let forward_exit=c.y42_alloc_state();let forward_dims=c.i13_dims();rev_tick')
s=s.replace('let mut q=vec![0;nq];','let mut q:Vec<_>=(0..nq).map(|i|if BODY_FQ.contains(&(i as u64))||i>=BODY_NQ{0}else{mix(i as u64^0x9351)}).collect();')
s=s.replace('ids(&abi[256..])','ids(&target)')
s=s.replace('for i in 0..256{q[i]=mix(i as u64);}','')
s=s.replace('assert_eq!(forward_a.qubits,correct,"independent field reference and clean forward scratch");','if widths.0==57{assert_eq!(forward_a.qubits,correct,"independent field reference and clean forward scratch");}else{assert_ne!(forward_a.qubits,correct,"old missing-borrow regression");}')
s=s.replace('assert_eq!(a.qubits,expected,"full inverse allMR/allq/scratch");','if widths.0==57{assert_eq!(a.qubits,expected,"full inverse allMR/allq/scratch");}')
s=s.replace('assert_eq!(sim.qubits,correct,"full forward native independent field reference");','if widths.0==57{assert_eq!(sim.qubits,correct,"full forward native independent field reference");}else{assert_ne!(sim.qubits,correct);}')
s=s.replace('assert_eq!(sim.qubits,expected,"full inverse native allq");','if widths.0==57{assert_eq!(sim.qubits,expected,"full inverse native allq");}')
s=s.replace('for i in 0..512{assert_eq!(sim.bits[i],b[i],"ABI classic slot{i}");}','for i in 0..BODY_NB{if !BODY_FB.contains(&(i as u64)){assert_eq!(sim.bits[i],b[i],"live classic slot{i}");}}')
s=s.replace('sim.qubits[773..].iter().filter(|x|**x!=0).count()','sim.qubits.iter().enumerate().filter(|(i,x)|(**x!=0)&&(BODY_FQ.contains(&(*i as u64))||*i>=BODY_NQ)).count()')
needle='let ops=c.take_ops();let mut q:'
assert s.count(needle)==1
extra='''let ops=c.take_ops();let original=load_ops("/home/hclau/ecdsa_research/overnight-20261014/product-evidence/c5-fold75/pre-y33.bin").unwrap();let original_slice=&original[START..END];if widths.0==56{assert_eq!(&ops[..forward],original_slice,"original complete104 emitted slice byte equality");assert_eq!(forward_exit.0,BODY_EXIT_FQ.iter().map(|&x|x as u32).collect::<Vec<_>>());assert_eq!(forward_exit.1,BODY_EXIT_FB.iter().map(|&x|x as u32).collect::<Vec<_>>());}let mut oldq=BODY_EXIT_FQ.iter().map(|&x|x as u32).collect::<Vec<_>>();let mut newq=forward_exit.0.clone();oldq.sort_unstable();newq.sort_unstable();assert_eq!(oldq,newq,"complete forward ownership same free quantum set");let mut oldb=BODY_EXIT_FB.iter().map(|&x|x as u32).collect::<Vec<_>>();let mut newb=forward_exit.1.clone();oldb.sort_unstable();newb.sort_unstable();assert_eq!(oldb,newb,"complete forward same free classical set");eprintln!("REPAIR57_PRODUCTION widths={widths:?} entry_dims={:?} forward_dims={forward_dims:?} forward_ops={forward} forward_kinds={:?} entry_pool={entry:?} forward_exit_pool={forward_exit:?} final_pool={exit:?} original_slice_equal={} freeq_order_matches_old={} freeb_order_matches_old={} score=NONE",(BODY_NQ,BODY_NB),kinds(&ops[..forward]),widths.0==56,forward_exit.0==BODY_EXIT_FQ.iter().map(|&x|x as u32).collect::<Vec<_>>(),forward_exit.1==BODY_EXIT_FB.iter().map(|&x|x as u32).collect::<Vec<_>>());let mut q:'''.replace('START',str(r['op'])).replace('END',str(a['op']))
s=s.replace(needle,extra);(out/'product_repair57_tests.rs').write_text(s,newline='\n')
