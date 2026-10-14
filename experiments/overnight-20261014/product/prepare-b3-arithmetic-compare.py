"""Fixed point value comparison of attested C5/B3/raw positive-bias bodies."""
from pathlib import Path
import hashlib, subprocess, sys
base,dest,paired=map(Path,sys.argv[1:4])
subprocess.run([sys.executable,str(Path(__file__).with_name('prepare-b3-stage-replay.py')),str(base),str(dest),str(paired)],check=True)
p=dest/'src/main.rs';s=p.read_text()
old='assert_eq!(a.len(),4,"stage directory, selected official packet, independent packet");'
new='assert_eq!(a.len(),6,"C5 raw, B3 raw, positive-bias C5 raw, selected official packet, independent packet");'
assert s.count(old)==1;s=s.replace(old,new)
old='for stage in["before-square-guard","after-square-guard","after-linear-restore","final"]{\n  let file=std::path::Path::new(&a[1]).join(format!("{stage}.bin"));'
new='for(stage,input)in[("c5_raw",&a[1]),("b3_raw",&a[2]),("positive_bias_raw",&a[3])]{\n  let file=std::path::Path::new(input);'
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace('for (packet,mode) in[(&a[2],"official_known_bad"),(&a[3],"independent")]', 'for (packet,mode) in[(&a[4],"official_known_bad"),(&a[5],"independent")]')
p.write_text(s,newline='\n')
print('arithmetic_comparison_sha256='+hashlib.sha256(p.read_bytes()).hexdigest())
