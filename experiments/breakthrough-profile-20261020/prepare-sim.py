"""Build region counters around the existing independent replay kernel."""
from pathlib import Path
import hashlib
import json
import shutil

r = Path(__file__).resolve().parent
old = r.parent / 'simd-census-v2-20261016/tool'
t = r / 'tool'
assert not t.exists()
(t / 'src').mkdir(parents=True)
for name in ['simd8wide.h', 'build.rs']:
    shutil.copyfile(old / name, t / name)
for name in ['prefix.rs', 'fast_sim_wide.rs', 'fast_curve_c.rs', 'shake_rng.rs']:
    shutil.copyfile(old / 'src' / name, t / 'src' / name)
shutil.copyfile(r.parent / 'product-carry-readers-20261019/io.rs', t / 'src/io.rs')
shutil.copyfile(r / 'map-phases.rs', t / 'src/map-phases.rs')
c = (old / 'simd8count.c').read_text()
profile = c[c.index('int simd8_run('):].replace('int simd8_run(', 'int simd8_profile(', 1)
profile = profile.replace('uint64_t *toffoli){', 'uint64_t *toffoli,const size_t *ends,size_t regions,uint64_t *profile){', 1)
profile = profile.replace('size_t depth=0,ri=0;', 'size_t depth=0,ri=0,region=0;', 1)
profile = profile.replace('const CompactOp o=ops[i];', 'while(region+1<regions && i>=ends[region])region++;\n  const CompactOp o=ops[i];', 1)
needle = 'for(unsigned j=0;j<8;j++)toffoli[j]+=(uint64_t)__builtin_popcountll(words[j]);'
assert profile.count(needle) == 1
profile = profile.replace(needle, 'for(unsigned j=0;j<8;j++){uint64_t count=(uint64_t)__builtin_popcountll(words[j]);toffoli[j]+=count;profile[region*8+j]+=count;}')
(t / 'simd8count.c').write_text(c + '\n' + profile)

source = (old / 'src/main.rs').read_text()
source = source.replace('type Point=', '''unsafe extern "C"{fn simd8_profile(ops:*const CompactOp,n:usize,q:*mut u64,b:*mut u64,p:*mut u64,rng:*const u64,nr:usize,stack:*mut u64,cap:usize,used:*mut usize,toffoli:*mut u64,ends:*const usize,regions:usize,profile:*mut u64)->i32;}
type Point=''', 1)
source = source.replace('let next=Arc::new', '''let map=std::fs::read_to_string(std::env::var("PHASE_MAP").expect("PHASE_MAP required")).unwrap();
 let full_ends:Vec<usize>=map.lines().map(|line|line.split('\\t').nth(1).unwrap().parse().unwrap()).collect();
 assert!(full_ends.windows(2).all(|w|w[0]<=w[1])&&full_ends.last()==Some(&ops.len()));
 let mut ends=Vec::new();let mut cursor=0;let mut compact=0;
 for end in full_ends {while cursor<end{if !matches!(ops[cursor].kind,OperationType::Register|OperationType::AppendToRegister|OperationType::DebugPrint){compact+=1;}cursor+=1;}ends.push(compact);}
 assert_eq!(compact,p.ops.len());let ends=Arc::new(ends);
 let next=Arc::new''', 1)
source = source.replace('handles.push(std::thread::spawn(move||{', 'let ends=ends.clone();\n  handles.push(std::thread::spawn(move||{', 1)
needle = 'let(mut phase,mut toffoli,mut used)=([0u64;8],[0u64;8],0usize);assert_eq!(unsafe{simd8_run('
assert source.count(needle) == 1
source = source.replace(needle, '''let original_q=if start<verify_first{Some(q.clone())}else{None};let original_b=if start<verify_first{Some(b.clone())}else{None};
    let mut regional=vec![0u64;ends.len()*8];
    let(mut phase,mut toffoli,mut used)=([0u64;8],[0u64;8],0usize);assert_eq!(unsafe{simd8_profile(''', 1)
needle = '4096,&mut used,toffoli.as_mut_ptr())},0);assert_eq!(used,p.rng_count);'
assert source.count(needle) == 1
source = source.replace(needle, '''4096,&mut used,toffoli.as_mut_ptr(),ends.as_ptr(),ends.len(),regional.as_mut_ptr())},0);assert_eq!(used,p.rng_count);
    for j in 0..8{assert_eq!((0..ends.len()).map(|region|regional[region*8+j]).sum::<u64>(),toffoli[j]);}
    if let (Some(mut rq),Some(mut rb))=(original_q,original_b){let(mut rp,mut rt,mut ru)=([0u64;8],[0u64;8],0usize);let mut rs=vec![0u64;4096*8];assert_eq!(unsafe{simd8_run(p.ops.as_ptr(),p.ops.len(),rq.as_mut_ptr(),rb.as_mut_ptr(),rp.as_mut_ptr(),rng.as_ptr(),p.rng_count,rs.as_mut_ptr(),4096,&mut ru,rt.as_mut_ptr())},0);assert_eq!(q,rq);assert_eq!(b,rb);assert_eq!(phase,rp);assert_eq!(toffoli,rt);assert_eq!(used,ru);}''', 1)
needle = 'let line=format!('
source = source.replace(needle, '''let regional_text=(0..ends.len()).map(|i|regional[i*8+j].to_string()).collect::<Vec<_>>().join(",");
     let line=format!(''', 1)
needle = '\\"failures\\":[{failures}]}}'
assert source.count(needle) == 1
source = source.replace(needle, '\\"regional_toffoli\\":[{regional_text}],\\"failures\\":[{failures}]}}', 1)
source += (r / 'sim-tests.rs').read_text()
(t / 'src/main.rs').write_text(source)
manifest = (old / 'Cargo.toml').read_text()
manifest = manifest.replace('name="product_paired_diagnostic"', 'name="breakthrough_phase_diagnostic"')
manifest = manifest.replace('/home/hclau/ecdsa_research/overnight-20261014/product-b3-baseline', str(r / 'observer'))
manifest += '\n[[bin]]\nname="map-phases"\npath="src/map-phases.rs"\n\n[[bin]]\nname="phase-replay"\npath="src/main.rs"\n'
(t / 'Cargo.toml').write_text(manifest)
files={p.relative_to(t).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(t.rglob('*')) if p.is_file()}
(r / 'REPLAY-SOURCE-FREEZE.json').write_text(json.dumps({'files':files,'original_kernel_copied_verbatim':True,'scope':'diagnostic counters only'},indent=2)+'\n')
print('Diagnostic kernel, mapper and full-state replay controls prepared.')
