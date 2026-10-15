"""Strict fresh-wire restoration, retaining historical pinned allocation behavior."""
from pathlib import Path
import subprocess,sys,json,hashlib
root=Path(__file__).resolve().parent;mode=sys.argv[1];assert mode in ['control','wide'];dest=root/(mode+'-b3');assert not dest.exists();rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True);subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
source=root.parent/'carry-frame-20261015'/('unseeded-b3' if mode=='control' else 'cap1536-b3')
for rel in subprocess.check_output(['git','-C',str(source),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines():assert rel.startswith('src/point_add/');(dest/rel).write_bytes((source/rel).read_bytes())
base=dest/'src/point_add';p=base/'builder.rs';p.write_text(p.read_text()+'\n'+(root/'dynamic_pool.rs').read_text())
p=base/'leapfrog.rs';s=p.read_text();changes={'use super::builder::Builder;':'use super::builder::{Builder,Y42Checkpoint};','fn y42_after(c: &mut Builder, rev: bool, t: usize, before: &(Vec<u32>, Vec<u32>, u32), spent: bool) {':'fn y42_after(c: &mut Builder, rev: bool, t: usize, checkpoint: &Y42Checkpoint, spent: bool) {\n    let before=&checkpoint.0;','''            let (q, b, n) = before.clone();
            let keep = b.len();
            c.y42_alloc_set(before, &q, keep, &[], n);''':'''            c.y42_dynamic_restore(checkpoint);'''}
for a,b in changes.items():assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
assert s.count('let mut y42_alloc: Option<(Vec<u32>, Vec<u32>, u32)> = None;')==2
s=s.replace('let mut y42_alloc: Option<(Vec<u32>, Vec<u32>, u32)> = None;','let mut y42_alloc: Option<Y42Checkpoint> = None;')
assert s.count('y42_alloc = Some(c.y42_alloc_state());')==2;s=s.replace('y42_alloc = Some(c.y42_alloc_state());','y42_alloc = Some(c.y42_dynamic_checkpoint());');p.write_text(s)
(root/(mode+'.patch')).write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(root/(mode+'-manifest.json')).write_text(json.dumps({'score':None,'revision':rev,'parent':str(source),'scope':'Dynamic allocator snapshot gains fresh-ID boundary/live count. Restoration checks all old/fresh quantum and classical ownership before restoring stack order. Original pinned path and assertions unchanged.','sources':{rel:hashlib.sha256((dest/rel).read_bytes()).hexdigest() for rel in subprocess.check_output(['git','-C',str(dest),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines()}},indent=2)+'\n')
