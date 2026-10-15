"""Spend additional clean qubits on exact AND caches, independent of product."""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parent
dest=root/'candidate-wide-v1'
assert not dest.exists()
subprocess.run(['git','clone','--shared','--no-checkout','/home/hclau/ecdsa_research/upstream',str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach','b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'],check=True)
base=dest/'src/point_add'
s=(root/'lazy_cache_audit.rs').read_text()
start=s.index('    let startset:HashSet')
end=s.index('\nfn gate(')
s=s[:start]+'''
    // All new quantum slots are initially clean. Reuse a slot only after its
    // earlier lease has measured it to zero and discharged the phase.
    let eligible=proposals.len();
    let mut free_after=Vec::<usize>::new();
    let mut chosen=vec![];
    for w in proposals {
        let slot=free_after.iter().position(|end|*end<=w.start).unwrap_or_else(||{
            free_after.push(0);free_after.len()-1
        });
        free_after[slot]=w.end;let donor=nq+slot;
        println!("LAZY_WINDOW donor={donor} start={} end={} proxy={} uses={:?}",w.start,w.end,w.proxy,w.uses);
        chosen.push((donor,w));
    }
    let width=nq+free_after.len();
    println!("LAZY_SUMMARY base_width={nq} width={width} repeated_groups={repeated} raw_repetitions={repetitions} eligible={eligible} selected={}",chosen.len());
    render(ops,chosen,nb,width)
}
'''+s[end:]
(base/'lazy_cache.rs').write_text(s+(root/'wide_tests.rs').read_text())
query=(root/'prepare.py').read_text().split("query='''",1)[1].split("'''",1)[0]
p=base/'interned_witness.rs';p.write_text(p.read_text()+query)
p=base/'mod.rs';s=p.read_text();needle='    let nonce: u64 = required_env("TAIL_NONCE");';assert s.count(needle)==1
p.write_text('mod lazy_cache;\n'+s.replace(needle,'    ops = lazy_cache::optimize(ops);\n'+needle))
print(dest)
