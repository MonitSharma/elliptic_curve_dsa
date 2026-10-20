from pathlib import Path
import hashlib,json,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-global-semantic-component-20261020';r=ex/'breakthrough-semantic-lifetime-color-20261020';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir()
for n in ['Cargo.toml','Cargo.lock','io.rs']:shutil.copyfile(old/'local-tool'/n,t/n)
s=(old/'discover.rs').read_text();head=s[:s.index('// Full-prefix exact Boolean replay.')];tests=s[s.index('#[cfg(test)]mod semantic_algebra_controls'):]
main='''fn main(){let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),3);let ops=io::load_ops(&args[1]);let(out,result,_)=semantic_color(&ops);std::fs::write(format!("{}.json",args[2]),serde_json::to_string_pretty(&result).unwrap()+"\\n").unwrap();io::save_ops(&format!("{}.ops.bin",args[2]),&out);println!("{result}");}\n'''
s=head+(a/'semantic-lifetime-color.rs').read_text()+tests+main;(t/'discover.rs').write_text(s);(r/'discover.rs').write_text(s)
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();f=json.loads((old/'SOURCE-FREEZE.json').read_bytes());f.update(tool_source_files={n:sha(t/n)for n in ['Cargo.toml','Cargo.lock','io.rs','discover.rs']},native_controls=7,scope='Exact semantic full-prefix zero lifetime coloring. Pinned registered inputs, active mapping injective, only globally provenzero helper release. Operation types/guards/classical/RNG sequence unchanged. Native3 truth/cofactor algebra plus4 complete protected lifetime/phase/dirtynegative/random controls. Emit component stream only; no gate/nonce/score.')
(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
for n in ['run.py','run-local.sh']:
 s=(old/n).read_text().replace(old.name,r.name).replace("'native_controls':12","'native_controls':7").replace('12 passed; 0 failed;','7 passed; 0 failed;');(r/n).write_bytes(s.encode())
(r/'.gitignore').write_text('local-tool/\n__pycache__/\n*.ops.bin\n');(r/'.gitattributes').write_text('* -text\n')
(r/'PLAN.md').write_text('''# Reuse workspace using stronger exact zero proofs

Earlier conservative lifetime audit found no width gain because it only
closed lifetimes at lexically dominating resets. Here full-prefix exact
semantic replay may also prove uncomputation and logically dominated
conditional resets. Free helper only when its value is exactly zero for all
original registered inputs and arbitrary measurement words. Pin all registered
quantum inputs; injective active map, reused physical wire zero by induction.
Keep every operation, guard, phase correction and RNG draw in original order.

Native3 qualified algebra plus4 lifetime controls compare every logical value
via final map, all free physical wires zero, classical bits, absolute phase,
and identical executed Toffolis. Include live-dirty negative control and16x100
randomized circuits. Fixed current public1829/de8 streams,5GiB/900s each.
Component only; any gain needs bound final source/full independent pipeline.
''');print(r.name)
