import shutil
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'factor-witness-tool';assert not d.exists()
shutil.copytree(r/'factor-cache-tool',d,ignore=shutil.ignore_patterns('target'))
p=d/'src/main.rs';s=p.read_text();needle='        "witness"=>interned_witness::witnesses(ops),';assert s.count(needle)==1
s=s.replace(needle,needle+'\n        "witness-only-retained"=>interned_anf_retained::witnesses(ops),');p.write_text(s)
p=d/'src/interned_anf_retained.rs';s=p.read_text();needle='        if let Some(q)=replacement{';assert s.count(needle)==1
s=s.replace(needle,needle+'\n            println!("I25_WITNESS_ROW at={at} control={q}");');p.write_text(s)
print('Only exact CCX-to-CX live witnesses; every changed row logged, no new qubits/bits/MR events.')
