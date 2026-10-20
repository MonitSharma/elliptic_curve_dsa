from pathlib import Path
import hashlib,json,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-value-normalized-aig-20261020';r=ex/'breakthrough-value-normalized-aig-v2-20261020';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir()
for n in ['Cargo.toml','Cargo.lock','io.rs','aig.rs','FAILURE-FIXTURES.json']:
 shutil.copyfile(old/'local-tool'/n,t/n)
s=(old/'audit.rs').read_text();assert s.count('.chain(outputs)')==1;s=s.replace('.chain(outputs)','.chain(outputs.iter())');(r/'audit.rs').write_text(s);(t/'audit.rs').write_text(s)
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
f=json.loads((old/'SOURCE-FREEZE.json').read_bytes());f['source_files']={n:sha(t/n)for n in ['Cargo.toml','Cargo.lock','io.rs','audit.rs','aig.rs','FAILURE-FIXTURES.json']};(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
for n in ['aig.rs','FAILURE-FIXTURES.json','verify-input.py','run-local.sh','.gitignore','.gitattributes','PLAN.md']:
 (r/n).write_bytes((old/n).read_text().replace(old.name,r.name).encode())
(old/'STATUS.md').write_text('# Compilation stopped before native/input tests\n\nNumeric cache exporter chained a slice iterator with owned Vec instead of its iterator. V2 fixes only that iterator argument; exact semantic/AIG/CNF logic unchanged. No source input or gate/nonce work ran.\n')
print(r.name)
