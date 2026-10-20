from pathlib import Path
import hashlib,json,shutil
a=Path(__file__).parent; ex=a.parent
old=ex/'breakthrough-global-phase-component-20261020'
r=ex/'breakthrough-global-phase-component-v2-20261020';r.mkdir(exist_ok=False)
(r/'local-tool').mkdir()
for n in ['Cargo.toml','Cargo.lock','io.rs']:
 shutil.copyfile(old/'local-tool'/n,r/'local-tool'/n)
s=(old/'local-tool/discover.rs').read_text()
production=s[:s.index('#[cfg(test)]mod global_prefix_tests')]
needle='make(K::CCZ,4,5,4,n,1)'; assert s.count(needle)==1
s=s.replace(needle,'make(K::R,n,n,0,n,n),make(K::X,n,n,0,n,n),make(K::CCZ,4,5,0,n,1)')
start=s.index('#[test]fn phase_product_relation_can_remove_one_t_without_sampling')
end=s.index('\n #[test]',start)
section=s[start:end];assert section.count('["ccz_to_cz"]')==1
s=s[:start]+section.replace('["ccz_to_cz"]','["ccz_to_z"]')+s[end:]
assert s[:s.index('#[cfg(test)]mod global_prefix_tests')]==production
(r/'local-tool/discover.rs').write_text(s)
(r/'discover.rs').write_text(s)
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
f=json.loads((old/'SOURCE-FREEZE.json').read_bytes());f['tool_source_files']={n:sha(r/'local-tool'/n)for n in ['Cargo.toml','Cargo.lock','io.rs','discover.rs']}
f['fixture_correction']='Original native16/18 passed. Invalid repeated-wire CCZ in constant-phase fixture stopped at unchanged validator. Product relation correctly lowered to Z(product) before CZ, test expectation was wrong. V2 fixes ONLY those tests, production prefix byte-identical.'
(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
for n in ['run.py','run-local.sh','.gitignore','.gitattributes','PLAN.md']:
 (r/n).write_bytes((old/n).read_text().replace(old.name,r.name).encode())
(old/'STATUS.md').write_text('# Native fixture failures; no stream input executed\n\n'+f['fixture_correction']+'\n')
print(r.name)
