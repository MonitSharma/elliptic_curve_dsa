from pathlib import Path
import shutil
r=Path(__file__).resolve().parent;d=r/'audit-tool'
assert not d.exists();(d/'src').mkdir(parents=True)
shutil.copyfile(r/'audit.rs',d/'src/main.rs')
(d/'Cargo.toml').write_text('[package]\nname="scope_proposal_audit"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nzstd="0.13"\nserde_json="1"\n[profile.release]\nopt-level=3\n')
