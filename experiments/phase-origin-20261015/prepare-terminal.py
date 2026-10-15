"""Give the terminal reverse merged cell the derived room for its exact flag route."""
from pathlib import Path
import subprocess,json,hashlib
root=Path(__file__).resolve().parent;dest=root/'terminal-b3';assert not dest.exists();rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
source=root.parent/'repair-integration-20261015/combined-b3'
for rel in subprocess.check_output(['git','-C',str(source),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines():
    assert rel.startswith('src/point_add/');(dest/rel).write_bytes((source/rel).read_bytes())
p=dest/'src/point_add/leapfrog.rs';s=p.read_text();needle='fn n2_pay_rev_last(c: &mut Builder, letter: &[QubitId], p: &mut [Vec<QubitId>; 2]) {';assert s.count(needle)==1
s=s.replace(needle,'''// Reserve the capacity used by merged_split's exact overflow-erasure proof:
// room >= 1 + m_fold_need(true) + two top bits makes s <= N-2.
'''+needle+'''
    let active=c.active_qubits() as usize;
    let cap=cells::cap().max(active + 1 + m_fold_need(true) + 2);
    super::pingpong::with_phase_cap(Some(cap), || n2_pay_rev_last_exact(c,letter,p));
}
fn n2_pay_rev_last_exact(c: &mut Builder, letter: &[QubitId], p: &mut [Vec<QubitId>; 2]) {''')
needle='    let (fold, proxy) = proxy_fold(w, true);';start=s.index('fn n2_pay_rev_last_exact(');at=s.index(needle,start)
s=s[:at]+s[at:].replace(needle,needle+'''
    let split=merged_split(c,proxy,true,true).expect("terminal exact overflow route must fit derived cap");
    eprintln!("TERMINAL_EXACT tick={t} active={} cap={} split={split} fold_need={}",c.active_qubits(),cells::cap(),m_fold_need(true));''',1)
p.write_text(s)
(root/'terminal.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(root/'terminal-manifest.json').write_text(json.dumps({'score':None,'revision':rev,'scope':'Combined source plus structural capacity reservation for the terminal reverse exact overflow-erasure route. No input-dependent settings, test-packet fitting or identity-tail change. Other approximate operations remain.','changed_sha256':{rel:hashlib.sha256((dest/rel).read_bytes()).hexdigest() for rel in subprocess.check_output(['git','-C',str(dest),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines()}},indent=2)+'\n')
