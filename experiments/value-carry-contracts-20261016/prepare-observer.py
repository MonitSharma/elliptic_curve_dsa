from pathlib import Path
import subprocess,shutil,hashlib,json
r=Path('/home/hclau/ecdsa_research/value-carry-contracts-20261016')
tip=r.parent/'product-exact-20261015/tip';d=r/'observer'
rev=subprocess.check_output(['git','-C',str(tip),'rev-parse','HEAD'],text=True).strip()
assert rev=='4b2ec52fc55da796aa8f5ef851290297e8706424' and not d.exists()
subprocess.run(['git','-C',str(tip),'worktree','add','--detach',str(d),rev],check=True)
b=d/'src/point_add'
f=(r.parent/'precision-repair-20261016/fold_marks.rs').read_text().replace('precision-repair-20261016','value-carry-contracts-20261016')
(b/'fold_marks.rs').write_text(f)
p=b/'mod.rs';s='mod fold_marks;\n'+p.read_text()
needle='        circ.y33_clears();';assert s.count(needle)==1
s=s.replace(needle,'        fold_marks::dump(circ.production_fold_ops());\n'+needle);p.write_text(s)
p=b/'builder.rs';s=p.read_text();needle='    pub(crate) fn y33_clears(&mut self) {';assert s.count(needle)==1
s=s.replace(needle,'    pub(crate) fn production_fold_ops(&self)->&[Op]{&self.ops}\n'+needle);p.write_text(s)
p=b/'y15_onefold.rs';s=p.read_text()
needle='    PAYLOAD_AT.with(|x|x.set(Some((rev,t))));';assert s.count(needle)==1
s=s.replace(needle,needle+'\n    VALUE_PAYLOAD.with(|x|*x.borrow_mut()=tg.to_vec());')
needle='thread_local! { static PAYLOAD_AT:';assert s.count(needle)==1
s=s.replace(needle,'thread_local!{static VALUE_PAYLOAD:std::cell::RefCell<Vec<QubitId>>=const{std::cell::RefCell::new(Vec::new())};}\n'+needle)
for name,revflag in [('fold_fwd_v2','false'),('fold_rev_v2','true')]:
 start=s.index('fn '+name+'(');end=s.index('\n}',start)+2;part=s[start:end]
 needle='    let mw = acc.len();';assert part.count(needle)==1
 src='src'if revflag=='true'else'&[]'
 part=part.replace(needle,needle+f'\n    let observe_t=PAYLOAD_AT.with(|x|x.get().map_or(0,|(_,t)|t));\n    let observe_id=super::super::fold_marks::begin(c.op_count(),{revflag},observe_t,acc,e,nm,k1,k2,{src});')
 assert part.endswith('    plan\n}')
 part=part[:-len('    plan\n}')]+ '    super::super::fold_marks::end(observe_id,c.op_count());\n    plan\n}'
 s=s[:start]+part+s[end:]
needle='''let (ha, hb) = lin_pair_on(c, &a, &b);
            c.ccx(ha, hb, acc[hi - 1]);
            lin_pair_off(c, &a, &b);
            c.cx(ci, acc[hi - 1]);'''
assert s.count(needle)==1
replacement='''let observe_begin=c.op_count();
            let (ha, hb) = lin_pair_on(c, &a, &b);
            let observe_ccx=c.op_count();
            c.ccx(ha, hb, acc[hi - 1]);
            lin_pair_off(c, &a, &b);
            c.cx(ci, acc[hi - 1]);
            value_terminal_mark(c,acc,add,lo,hi,ci,ha,hb,&a,&b,observe_begin,observe_ccx);'''
s=s.replace(needle,replacement)
needle2=needle.replace('            ','        ');assert s.count(needle2)==1
s=s.replace(needle2,replacement.replace('            ','        '))
s+='''
// Research-only metadata: no gate emission or state mutation.
fn value_terminal_mark(c:&Builder,acc:&[QubitId],add:&[Lin],lo:usize,hi:usize,ci:QubitId,ha:QubitId,hb:QubitId,a:&Lin,b:&Lin,start:usize,at:usize){
 let (rev,t)=PAYLOAD_AT.with(|x|x.get().unwrap_or((false,usize::MAX)));
 let full=VALUE_PAYLOAD.with(|x|x.borrow().clone());
 let next=if full.len()>hi && full[..acc.len()]==*acc{full[hi].0}else{u64::MAX};
 let ids=|v:&[QubitId]|v.iter().map(|x|x.0).collect::<Vec<_>>();
 eprintln!("VALUE_TERMINAL {{\\"rev\\":{rev},\\"tick\\":{t},\\"lo\\":{lo},\\"hi\\":{hi},\\"begin\\":{start},\\"ccx\\":{at},\\"end\\":{},\\"a\\":{:?},\\"a_one\\":{},\\"b\\":{:?},\\"b_one\\":{},\\"sign\\":{:?},\\"sign_one\\":{},\\"top_sign\\":{:?},\\"top_sign_one\\":{},\\"ci\\":{},\\"ha\\":{},\\"hb\\":{},\\"top\\":{},\\"next\\":{next},\\"acc\\":{:?}}}",c.op_count(),ids(&a.w),a.one,ids(&b.w),b.one,ids(&add[hi-2].w),add[hi-2].one,ids(&add[hi-1].w),add[hi-1].one,ci.0,ha.0,hb.0,acc[hi-1].0,ids(acc));
}
'''
p.write_text(s)
(r/'observer.patch').write_bytes(subprocess.check_output(['git','-C',str(d),'diff','--binary']))
(r/'observer-source.json').write_text(json.dumps(dict(base_revision=rev,gate_inert=True,files={str(p.relative_to(d)):hashlib.sha256(p.read_bytes()).hexdigest()for p in b.rglob('*')if p.is_file()}),indent=2)+'\n')
