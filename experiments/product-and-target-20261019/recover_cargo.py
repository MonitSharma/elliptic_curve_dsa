"""Keep the exact earlier research manifests after adding later tool binaries."""
import hashlib
from pathlib import Path
r=Path(__file__).resolve().parent
current=(r/'Cargo.toml').read_text()
for receipt,name in [('SOURCE.sha256','Cargo-initial.toml'),('CONTROL_SOURCE.sha256','Cargo-control.toml')]:
    target=next(x.split()[0] for x in (r/receipt).read_text().splitlines() if x.split()[-1]=='Cargo.toml')
    if (r/name).exists():
        assert hashlib.sha256((r/name).read_bytes()).hexdigest()==target
        print(name,target);continue
    cuts=[len(current)]+[i for i in range(len(current)) if current.startswith('\n[[bin]]',i)]
    matches=[]
    for cut in cuts:
        s=current[:cut].rstrip()
        for line in ['\n','\r\n']:
            for count in range(4):
                b=(s+'\n'*count).replace('\n',line).encode()
                if hashlib.sha256(b).hexdigest()==target:matches.append(b)
    assert matches,(receipt,target)
    (r/name).write_bytes(matches[0])
    print(name,target)
