"""Repair ambiguous empty-vector types; preserve original failed source."""
import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'tool';assert(r/'run.exit').read_text().strip()=='1'
shutil.copyfile(t/'alias.rs',r/'alias-failed-v1.rs')
p=t/'alias.rs';s=p.read_text();s=s.replace('**x==vec![vec![]]','x.len()==1&&x[0].is_empty()').replace('assert_eq!(norm(terms),vec![vec![]])','assert_eq!(norm(terms),vec![Vec::<i64>::new()])');p.write_text(s)
subprocess.run(['/home/hclau/.cargo/bin/cargo','+1.93.0','generate-lockfile','--offline'],cwd=t,check=True)
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();f=json.loads((r/'SOURCE_FREEZE.json').read_text());f['tool_source_files']={p.relative_to(t).as_posix():sha(p)for p in t.iterdir()if p.is_file()};f['correction']='V1 compiler rejected ambiguous empty-vector comparison types. V2 changes only those annotations and freezes the generated lockfile before tests; original source and failure retained. No v1 stream probe ran.';(r/'SOURCE_FREEZE-v2.json').write_text(json.dumps(f,indent=2)+'\n')
