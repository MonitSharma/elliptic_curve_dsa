"""Uniform Y15 comparison policy, isolated from preserved dynamic-pool parents."""
from pathlib import Path
import subprocess,sys,hashlib,json
root=Path(__file__).resolve().parent;mode=sys.argv[1];assert mode in ('narrow','wide');dest=root/(mode+'-b3');assert not dest.exists();rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True);subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
parent=root.parent/'dynamic-pool-20261015'/('control-b3' if mode=='narrow' else 'wide-b3')
for rel in subprocess.check_output(['git','-C',str(parent),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines():assert rel.startswith('src/point_add/');(dest/rel).write_bytes((parent/rel).read_bytes())
p=dest/'src/point_add/pingpong.rs';s=p.read_text();start=s.index('    pub(crate) fn y15_split_spec(');end=s.index('    /// y15-core:',start);part=s[start:end];assert part.count('        (k, seed)')==1
part=part.replace('        (k, seed)','''        // A source bit is a statistical predictor, not a retained carry.
        // Include its position in the window, preserving refined coverage.
        let width=seed.map_or(k,|position|k.max(split-position));
        assert!(width<=split);
        if seed.is_some(){eprintln!("Y15_UNSEEDED round={round} multiply={multiply} split={split} old_width={k} new_width={width} seed={seed:?}");}
        (width, None)''');s=s[:start]+part+s[end:];p.write_text(s)
(root/(mode+'.patch')).write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(root/(mode+'-manifest.json')).write_text(json.dumps({'revision':rev,'parent':str(parent),'score':None,'scope':'Uniform Y15 split comparison: remove statistical seed, include its position, preserve all refined window bits. Still truncated and approximate. Fixed packets unchanged.','changed_sha256':{rel:hashlib.sha256((dest/rel).read_bytes()).hexdigest() for rel in subprocess.check_output(['git','-C',str(dest),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines()}},indent=2)+'\n')
