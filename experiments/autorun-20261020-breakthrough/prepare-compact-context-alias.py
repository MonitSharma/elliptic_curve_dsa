from pathlib import Path
import hashlib,json,re,shutil
a=Path(__file__).resolve().parent;ex=a.parent
old=ex/'breakthrough-global-quantum-alias-v3-20261021'
r=ex/'breakthrough-compact-context-alias-20261021';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir()
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
f=json.loads((old/'SOURCE-FREEZE.json').read_bytes())
assert all(sha(old/'local-tool'/p)==h for p,h in f['tool_source_files'].items())
for n in ['Cargo.toml','Cargo.lock','io.rs']:shutil.copyfile(old/'local-tool'/n,t/n)
p=t/'Cargo.toml';p.write_text(p.read_text().replace('name = "global_quantum_alias"','name = "compact_context_alias"'))
s=(old/'local-tool/discover.rs').read_text()
q=(ex/'breakthrough-flat-guard-control-20261021/discover.rs').read_text();q=q[q.index('fn qualify('):q.index('fn main(')]
q=q.replace('assert_eq!(a.stats,b.stats,"executed resource counts case{case}");','assert!(b.stats.toffoli_gates<=a.stats.toffoli_gates,"executed Toffolis may only decrease");').replace('FULL_PROTECTED_FLAT_GUARD_PASS','FULL_PROTECTED_COMPACT_ALIAS_PASS').replace('executed T/Clifford count and all original random-word consumption match','original random-word consumption match; executed Toffolis do not increase')
start=s.index('fn main(');end=s.index('\n',start)
main='''fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),3);let ops=io::load_ops(&a[1]);let(out,stats)=global_prefix_simplify(&ops,1024);let q=qualify(&ops,&out);io::save_ops(&format!("{}.ops.bin",a[2]),&out);let r=serde_json::json!({"status":"COMPACT_CONTEXT_EXACT_ALIAS_COMPONENT_NOT_A_SCORE","input_records_sha3":hash(&ops),"output_records_sha3":hash(&out),"proof":stats,"qualification":q});std::fs::write(format!("{}.json",a[2]),serde_json::to_string_pretty(&r).unwrap()+"\\n").unwrap();}'''
s=s[:start]+q+main+s[end:];(t/'discover.rs').write_text(s);(r/'discover.rs').write_text(s)
f.update(tool_source_files={n:sha(t/n)for n in ['Cargo.toml','Cargo.lock','io.rs','discover.rs']},input_streams={'cap1233-r012':'6c02ca2dfe4735cac58a4ab71024a5b53c3baff5e8a935f0a2f268074018519c','cap1234-t21':'0f8ff70b928eb2a64ba5d9990e4f2117608167881075b549b83e9abae244ade2'},scope='Fresh application of unchanged fifteen-test full-prefix exact Boolean alias rules to current public compact-carry streams with independently qualified existing-wire context caches. Every accepted rewrite uses exact symbolic equality. Twenty-four complete protected arbitrary-input quantum/classical/absolute-phase/RNG comparisons per stream. No point census, final gate, nonce or scored benchmark; diagnostic counts only.')
(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
s=(old/'run.py').read_text().replace(old.name,r.name).replace("target/release/global_quantum_alias'","target/release/compact_context_alias'")
left=s.index("for name,path in [");right=s.index(']:',left)+2
s=s[:left]+"for name,path in [(n,r.parent/'breakthrough-public1829-context-audit-20261020'/(n+'.ops.bin'))for n in f['input_streams']]:"+s[right:]
s=s.replace('8*1024**3','6*1024**3');(r/'run.py').write_text(s)
s=(old/'run-local.sh').read_text().replace(old.name,r.name).replace('--bin global_quantum_alias','--bin compact_context_alias');(r/'run-local.sh').write_bytes(s.encode())
(r/'PLAN.md').write_text(f['scope']+'\n');(r/'.gitignore').write_text('local-tool/\n*.ops.bin\n__pycache__/\n');(r/'.gitattributes').write_text('* -text\n')
print(r.name)
