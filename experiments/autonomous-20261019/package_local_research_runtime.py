"""Copy only compiler/link dependencies for independent local one-core research."""
import hashlib,io,json,os,subprocess,tarfile
from pathlib import Path
ws=Path('/home/hclau/ecdsa_research');r=ws/'portable-rust-20261019';r.mkdir(exist_ok=False)
profile=json.loads(subprocess.check_output(['python3',str(ws/'autonomous-20261019/preflight_v13.py')],env=dict(os.environ,RESEARCH_SLOTS='1'),text=True))
t=Path('/home/hclau/.rustup/toolchains/stable-x86_64-unknown-linux-gnu');d=ws/'product-order-20261019/target/release/deps'
files={}
for p in [t/'bin/rustc',*t.glob('lib/libLLVM*'),*t.glob('lib/librustc_driver*'),*(t/'lib/rustlib/x86_64-unknown-linux-gnu/lib').glob('*')]:
    if p.is_file():files['compiler/'+p.relative_to(t).as_posix()]=p
for p in d.iterdir():
    if p.suffix in ['.rlib','.so']:files['deps/'+p.name]=p
items={key:{'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()} for key,p in files.items()}
manifest={'status':'READ_ONLY_SERVER_COMPILER_AND_EXISTING_RELEASE_DEPENDENCIES','profile':profile,'included_files':items,'server_compilation_or_jobs_changed':False}
p=r/'runtime.tar.gz'
with tarfile.open(p,'x:gz',compresslevel=1) as a:
    for key,path in sorted(files.items()):a.add(path,arcname=key,recursive=False)
    raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
(r/'RUNTIME.json').write_text(json.dumps({'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest(),'files':len(files)},indent=2)+'\n')
print((r/'RUNTIME.json').read_text())
