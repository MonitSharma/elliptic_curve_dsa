from pathlib import Path
import hashlib,json,tarfile,io
r=Path(__file__).resolve().parent
h=lambda b:hashlib.sha256(b).hexdigest()
source=r.parent/'product-exact-20261015/tip/ops.bin'
assert h(source.read_bytes())=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
assert (r/'evidence/width-terminal-recheck.exit').read_text().strip()=='0'
files=set(r.glob('run-width*.sh'))|set(r.glob('prove-peak-carry4.py'))|set(r.glob('width-contracts-proof.md'))|set(r.glob('tool/src/bin/width*.rs'))|set(r.glob('tool/src/width*.rs'))|set(r.glob('evidence/width-*'))|{r/'evidence/peak-carry4-boolean-proof.json',Path(__file__).resolve()}
files={p for p in files if p.is_file()}
# Prove the reconstructed v1 module is exactly the source originally built.
legacy=next(p for p in files if p.name.startswith('width-affine-before.sha256'))
oldhash=next(line.split()[0] for line in legacy.read_text().splitlines() if 'tool/src/width_interned_witness.rs' in line)
assert oldhash==h((r/'tool/src/width_interned_witness_affine_v1.rs').read_bytes()),(oldhash,h((r/'tool/src/width_interned_witness_affine_v1.rs').read_bytes()))
rows=[];payload=[]
for p in sorted(files):
 name=str(p.relative_to(r));logical=name.replace('\r','[CR]');b=p.read_bytes();rows.append(dict(path=logical,original_path=name,sha256=h(b),size=len(b)));payload.append((logical,b))
refs=[]
for p in sorted((r/'tool/target/release').glob('width*_audit')):
 if p.is_file():b=p.read_bytes();refs.append(dict(path=str(p),sha256=h(b),size=len(b)))
p=r/'tool/target/release/width_primitive_check';b=p.read_bytes();refs.append(dict(path=str(p),sha256=h(b),size=len(b)))
manifest=dict(status='TERMINAL_WIDTH_PARTIAL_NEGATIVE_VERIFIED',source_sha256=h(source.read_bytes()),files=rows,server_only_binaries=refs,reconstructed_v1_source_matches_original_receipt=True,actual_source_Q=1234,claimed_Q1233=False,cap512_paidT=752,unhandled=585)
name=r/'evidence-width-supplement.tar.gz'
with tarfile.open(name,'w:gz')as t:
 for n,b in payload:
  x=tarfile.TarInfo(n);x.size=len(b);t.addfile(x,io.BytesIO(b))
 b=(json.dumps(manifest,indent=2)+'\n').encode();x=tarfile.TarInfo('MANIFEST.json');x.size=len(b);t.addfile(x,io.BytesIO(b))
with tarfile.open(name)as t:
 for row in rows:assert h(t.extractfile(row['path']).read())==row['sha256']
receipt=dict(status='ALL_ARCHIVED_MANIFEST_ENTRIES_VERIFY',archive=name.name,sha256=h(name.read_bytes()),files=len(rows),server_binary_refs=len(refs))
(r/'evidence/width-archive-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
