from pathlib import Path
import subprocess
root=Path(__file__).resolve().parent
dest=root/'single-replay'
subprocess.run(['python3',str(root.parent/'toffoli-readiness-20261015/prepare-wide-replay.py'),str(dest)],check=True)
p=dest/'src/main.rs'
s=p.read_text()
needle='    let(map,nold)=reconstruction(&left,&right,&std::fs::read_to_string(&args[3]).unwrap(),nb);'
assert s.count(needle)==1
s=s.replace(needle,'''    let nold=left.iter().filter(|o|matches!(o.kind,OperationType::Hmr|OperationType::R)).count();
    assert_eq!(nold,right.iter().filter(|o|matches!(o.kind,OperationType::Hmr|OperationType::R)).count());
    let map:Vec<usize>=(0..nold).collect();''')
p.write_text(s)
