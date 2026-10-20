import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;parent=ws/'public-product-54fc-20261020/parent';utility=ws/'breakthrough-public322-square-finished-20261020/candidate';t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();base='3dee0cd67d09d40af62da06bc1c1c6b16adc8f56';assert subprocess.check_output(['git','-C',str(parent),'rev-parse','HEAD']).decode().strip()==base and sha(parent/'ops.bin')=='51671a28145ce015d31b90db57c5bb248d544b0daacecfae1a015753056fa2e8'and not t.exists()
with(parent/'ops.bin').open('rb',buffering=0)as source:
 header=source.read(16);assert header[:8]==b'QECCOPSZ';count=int.from_bytes(header[8:],'little');h=hashlib.sha3_256();size=0;p=subprocess.Popen(['zstd','-dc'],stdin=source,stdout=subprocess.PIPE)
 while chunk:=p.stdout.read(1<<20):h.update(chunk);size+=len(chunk)
 assert p.wait()==0 and size==count*56 and count==11628847
parent_hash=h.hexdigest();subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),base],check=True)
for name in ['breakthrough_generic.rs','break_profile.rs']:shutil.copyfile(utility/'src/point_add'/name,t/'src/point_add'/name)
p=t/'src/point_add/mod.rs';raw=p.read_bytes();a=b'pub fn build() -> Vec<Op> {';assert raw.count(a)==1;raw=raw.replace(a,b'fn public_product_parent_build() -> Vec<Op> {');raw+=b'''
// Research transform of the exact public stream; external input must be removed
// for any final candidate and replaced by public_product_parent_build().
pub fn build()->Vec<Op>{let path=std::env::var("BREAK_PRODUCT_INPUT").expect("Declared public input");clear_process_env();install_skywalk_submission_recipe();std::env::set_var("EXACT_PAIR_CARRY","1");leapfrog::install_recipe();std::env::remove_var("SL_COND");product_repeat::run(break_profile::load_ops(&path))}
mod breakthrough_generic;
mod break_profile;
mod product_repeat;
''';p.write_bytes(raw)
runtime=f'''use crate::circuit::{{Op,OperationType,QubitId}};use sha3::{{Digest,Sha3_256}};
const PARENT_COUNT:usize={count};const PARENT_SHA3:&str="{parent_hash}";pub(super)const IDENTITY_NONCE:u64=0;
pub(super)fn run(mut ops:Vec<Op>)->Vec<Op>{{assert_eq!(ops.len(),PARENT_COUNT);let mut h=Sha3_256::new();for o in &ops{{for x in[o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{{h.update(x.to_le_bytes());}}}}assert_eq!(format!("{{:x}}",h.finalize()),PARENT_SHA3,"Exact current public product source");
let end=ops.len()-96;for pair in ops[end..].chunks_exact(2){{assert_eq!(pair[0].kind,OperationType::X);assert_eq!(pair[1].kind,OperationType::X);assert_eq!(pair[0].q_target,pair[1].q_target);}}ops.truncate(end);let mut ops=super::breakthrough_generic::run(ops);assert!(IDENTITY_NONCE<(1u64<<48));for bit in 0..48{{let mut o=Op::empty();o.kind=OperationType::X;o.q_target=QubitId((IDENTITY_NONCE>>bit)&1);o.validate();ops.extend([o,o]);}}ops}}
''';(t/'src/point_add/product_repeat.rs').write_bytes(runtime.encode());subprocess.run(['cp','-a','--reflink=auto',str(parent/'target'),str(t/'target')],check=True);subprocess.run(['git','-C',str(t),'add','--intent-to-add','src/point_add'],check=True);(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD','--','src/point_add']));protected={path:sha(t/path)for path in subprocess.check_output(['git','-C',str(t),'ls-files']).decode().splitlines()if not path.startswith('src/point_add/')};assert len(protected)==17
(r/'SOURCE-FREEZE.json').write_text(json.dumps({'base':base,'source_files':{p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()},'protected_files':protected,'public_input':str(parent/'ops.bin'),'public_input_sha256':sha(parent/'ops.bin'),'public_input_count':count,'public_input_records_sha3':parent_hash,'identity_nonce':0,'reused_generic_source_sha256':sha(utility/'src/point_add/breakthrough_generic.rs'),'scope':'Repeat the unchanged generic exact pipeline after ALL public54fc optimizations. Research wrapper loads exact source-bound public stream, strips only its checked identity tail, applies generic passes, appends nonce0. No source-bound table is altered/rebound. If promising, final source must call unchanged public parent constructor directly, be frozen/rebuilt, gated afresh vs exact54fc, then nonce qualification and unchanged benchmark. Static diagnostics only; no packet/census/nonce screening here.'},indent=2)+'\n')
