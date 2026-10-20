from pathlib import Path
import hashlib,json,tarfile,shutil,difflib
a=Path(__file__).parent;ex=a.parent;r=ex/'breakthrough-de8-generic-repeat-20261020';r.mkdir(exist_ok=False);t=r/'candidate';t.mkdir()
old=ex/'breakthrough-local-de8-replay-20261020';f=json.loads((old/'SOURCE-FREEZE.json').read_bytes());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
for rel,h in {**f['source_files'],**f['protected_files']}.items():
 src=old/'candidate'/rel;assert sha(src)==h;dest=t/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
cache=json.loads((ex/'breakthrough-de8-second-cache-20261020/extra0.json').read_bytes());assert len(cache['leases'])==2
s=(t/'src/point_add/witness_context_cache.rs').read_text();start=s.index('const LEASES:');end=s.index('\nfn make',start);s=s[:start]+'const LEASES:&[[u64;9]]=&'+json.dumps(cache['leases'],separators=(',',':'))+';'+s[end:]
start=s.index('pub(super)fn run(');end=s.index('\n#[cfg(test)]',start)
s=s[:start]+'''pub(super)fn run(ops:Vec<Op>)->Vec<Op>{
 bind(&ops,10995453,"d272df3f8bd9ca7d1e45dfcab6f87eca439ce3c36d2a0d24feae5092678e07cb");
 let(_,nb,_,_)=analyze_ops(ops.iter());let mut ops=rewrite_ops(ops,LEASES,nb as usize);
 bind(&ops,10995459,"9cd7196d0bbaedc5d5dfe19578f77920cb130d4f586da2f891d13d8d08dd45bf");
 let end=ops.len()-96;for(bit,pair)in ops[end..].chunks_exact(2).enumerate(){for o in pair{assert_eq!(o.kind,K::X);assert_eq!(o.q_target.0,(229u64>>bit)&1);}}ops.truncate(end);
 let mut ops=super::breakthrough_generic::run(ops);let(nq,_,_,_)=analyze_ops(ops.iter());assert!(nq<=1464);
 for _ in 0..48{let o=make(K::X,u64::MAX,u64::MAX,0,u64::MAX,u64::MAX);ops.extend([o,o]);}ops
}
''' +s[end:]
(t/'src/point_add/repeat_generic_cache.rs').write_text(s)
p=t/'src/point_add/mod.rs';s=p.read_text();needle='pub fn build()->Vec<Op>{witness_context_cache::run(native_context_parent_build())}';assert s.count(needle)==1
s=s.replace(needle,'mod repeat_generic_cache;\npub fn build()->Vec<Op>{repeat_generic_cache::run(witness_context_cache::run(native_context_parent_build()))}');p.write_text(s)
source={p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()};freeze={'source_files':source,'protected_files':f['protected_files'],'parent_official_source':f['official_public_revision'],'parent_stream':f['expected_stream_sha256'],'cache_proof_sha256':sha(ex/'breakthrough-de8-second-cache-20261020/extra0.json'),'scope':'One fixed second-cache2lease source plus a second unchanged exact generic pipeline. Literal input and cache-output bindings. Strip/check parent229 tail; append diagnostic nonce0 after all passes. Component source only, not gated/noncescreened/benchmarked or scored.'}
(r/'SOURCE-FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n')
patch=[]
for rel in source:
 before=(old/'candidate'/rel).read_text()if(old/'candidate'/rel).exists()else'';after=(t/rel).read_text()
 if before!=after:patch.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
(r/'source.patch').write_text(''.join(patch))
with tarfile.open(r/'point-add-source.tar.gz','w:gz')as ar:
 for rel in sorted(source):ar.add(t/rel,arcname=rel,recursive=False)
(r/'verify.py').write_text('''import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE-FREEZE.json').read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(r/'candidate'/n)==h for n,h in {**f['source_files'],**f['protected_files']}.items());s=r.parent/'breakthrough-public1829-width-port-local-v4-20261020/stats-tool/target/release/native_width_stats';subprocess.run([str(s),str(r/'candidate/ops.bin'),str(r/'STATS.json')],check=True);(r/'RESULT.json').write_text(json.dumps({'status':'COMPLETE_FIXED_GENERIC_REPEAT_SOURCE_NOT_SCORED','static_diagnostics':json.loads((r/'STATS.json').read_text()),'stream_sha256':sha(r/'candidate/ops.bin'),'source_files':len(f['source_files']),'protected_files':len(f['protected_files']),'scope':f['scope']},indent=2)+'\\n')
''')
s=(old/'run-local.sh').read_text().replace(old.name,r.name).replace('cd candidate\n','cd candidate\n/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo test --release --locked point_add::repeat_generic_cache::cache_tests -- --nocapture > ../tests.log 2>&1\ngrep -q "1 passed; 0 failed;" ../tests.log\n')
(r/'run-local.sh').write_bytes(s.encode());(r/'.gitignore').write_text('candidate/\n__pycache__/\n');(r/'.gitattributes').write_text('* -text\n')
(r/'PLAN.md').write_text('''# Exact generic pass repeated after two newly proved caches

Restore current officialde8 source/protected bytes. Bind full parent d272,
apply exactly the two new context-proved cache leases, bind output9cd719,
check/remove literal229 identity tail, run unchanged generic exact passes
again and append nonce0. Keep source/patch/archive before tests. Native guarded
cache phase/RNG/fault control and existing independent9 cache proofs required.
Complete generated stream/static count is diagnostic only; no gate/nonce or
benchmark. If competitive, compose any further exact phase/action lowerings
and freeze final source BEFORE all fresh point inputs.
''');print(r.name)
