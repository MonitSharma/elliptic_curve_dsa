"""Remove the terminal boundary's heuristic borrow, using one more comparison bit."""
from pathlib import Path
import subprocess,json,hashlib
root=Path(__file__).resolve().parent;dest=root/'unseeded-b3';assert not dest.exists();rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True);subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
source=root.parent/'phase-origin-20261015/terminal-b3'
for rel in subprocess.check_output(['git','-C',str(source),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines():assert rel.startswith('src/point_add/');(dest/rel).write_bytes((source/rel).read_bytes())
base=dest/'src/point_add';p=base/'leapfrog.rs';s=p.read_text();needle='    super::pingpong::with_phase_cap(Some(cap), || n2_pay_rev_last_exact(c,letter,p));';assert s.count(needle)==1
s=s.replace(needle,'''    TERMINAL_UNSEEDED.with(|flag|{assert!(!flag.replace(true));});
'''+needle+'''
    TERMINAL_UNSEEDED.with(|flag|flag.set(false));''')
s+='''
thread_local! {static TERMINAL_UNSEEDED:std::cell::Cell<bool>=const{std::cell::Cell::new(false)};}
pub(crate) fn terminal_unseeded()->bool {TERMINAL_UNSEEDED.with(|flag|flag.get())}
''';p.write_text(s)
p=base/'pingpong.rs';s=p.read_text();start=s.index('    pub(crate) fn add_consume_exact(');end=s.index('    /// Bits below `split`',start);part=s[start:end]
needle='        circ.record_replay_site(\'B\', round, split, k);';assert part.count(needle)==1
part=part.replace(needle,'''        // A source bit is a statistical borrow predictor, not an arithmetic
        // carry. The terminal policy uses an unseeded window one bit wider.
        let (k,borrow)=if super::super::leapfrog::terminal_unseeded(){
            let widened=(k+usize::from(borrow.is_some())).min(split);
            eprintln!("TERMINAL_UNSEEDED split={split} old_width={k} new_width={widened} old_seed={}",borrow.is_some());
            (widened,None)
        }else{(k,borrow)};
'''+needle);s=s[:start]+part+s[end:];p.write_text(s)
(root/'unseeded.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(root/'unseeded-manifest.json').write_text(json.dumps({'score':None,'revision':rev,'scope':'Every terminal reverse exact-overflow cell uses unseeded split-boundary comparison, widened by one when replacing a source-bit predictor. Still a truncated comparison, not a universal correctness proof. No hash/packet adjustment.','source_sha256':{rel:hashlib.sha256((dest/rel).read_bytes()).hexdigest() for rel in subprocess.check_output(['git','-C',str(dest),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines()}},indent=2)+'\n')
