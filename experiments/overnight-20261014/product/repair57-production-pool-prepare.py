"""Gate-inert original C5 full104 allocator/physical ABI observation."""
from pathlib import Path
import subprocess,sys
base,out,evidence=map(Path,sys.argv[1:]);s=subprocess.check_output(['git','-C',str(base),'show','c5bb1ec876db859a3f9f8a9052c140a145df834e:src/point_add/y15_onefold.rs'],text=True)
needle='pub(super) fn fwd_tick(c: &mut Builder, t: usize, letter: &[QubitId], p: &mut [Vec<QubitId>; 2]) {';assert s.count(needle)==1
s=s.replace(needle,needle+'\n    if t==104{product_repair57_pool(c,"before",letter,p);}')
needle='    if room_trace() {\n        eprintln!("Y15_TICK fwd t={t} active={a0} cost={:.1}", c.expected_total() - e0);\n    }\n}'
assert s.count(needle)==1;s=s.replace(needle,needle[:-1]+'    if t==104{product_repair57_pool(c,"after",letter,p);}\n}')
s+='''
fn product_repair57_pool(c:&Builder,label:&str,letter:&[QubitId],p:&[Vec<QubitId>;2]){
 let(fq,fb,nb)=c.y42_alloc_state();let dims=c.i13_dims();let ids=|a:&[QubitId]|a.iter().map(|q|q.0).collect::<Vec<_>>();
 let text=format!("{{\\"label\\":\\"{label}\\",\\"op\\":{},\\"dims\\":[{},{}],\\"active\\":{},\\"expected_proxy\\":{},\\"p\\":[{:?},{:?}],\\"letter\\":{:?},\\"freeq\\":{fq:?},\\"freeb\\":{fb:?},\\"nb\\":{nb}}}\\n",c.op_count(),dims.0,dims.1,c.active_qubits(),c.expected_total(),ids(&p[0]),ids(&p[1]),ids(letter));
 std::fs::write(std::path::Path::new(DIRECTORY).join(format!("{label}.json")),text).unwrap();
}
'''.replace('DIRECTORY',json_literal:=('"'+str(evidence)+'"'))
(out/'y15_onefold.rs').write_text(s,newline='\n')
