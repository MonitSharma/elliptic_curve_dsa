"""Gate-inert source frame snapshots at tick, seed and endpoint boundaries."""
from pathlib import Path
import subprocess,sys
base,output,evidence=map(Path,sys.argv[1:4])
subprocess.run([sys.executable,str(Path(__file__).with_name('prepare-body-boundaries-v2.py')),str(base),str(output),str(evidence)],check=True)
s=(output/'leapfrog.rs').read_text()
def frame(label,t='usize::MAX',r='None',p='None',letter='&[]',skip='false'):
 return f'    product_walk_frame(c,"{label}",{t},{r},{p},{letter},{skip});\n'
for name,direction in [('fwd_tick','fwd'),('rev_tick','rev')]:
 needle=f'fn {name}(c: &mut Builder, wk: &mut Walk, t: usize, mut pay: Option<&mut [Vec<QubitId>; 2]>) {{'
 assert s.count(needle)==1
 s=s.replace(needle,needle.replace(name,name+'_product_inner',1))
 wrapper=needle+'\n'+frame(name+'_before','t','Some(&wk.r)','pay.as_deref()','wk.tape.get(t).map(|x|x.as_slice()).unwrap_or(&[])','SKIP_PAY_ROT_AT.with(|x|x.get()==t)')
 wrapper+=f'    {name}_product_inner(c,wk,t,pay.as_deref_mut());\n'
 wrapper+=frame(name+'_after','t','Some(&wk.r)','pay.as_deref()','wk.tape.get(t).map(|x|x.as_slice()).unwrap_or(&[])','SKIP_PAY_ROT_AT.with(|x|x.get()==t)')+'}\n'
 s+='\n'+wrapper
for name in ['pay_fwd_tick','pay_rev_tick']:
 needle=f'fn {name}(c: &mut Builder, t: usize, letter: &[QubitId], p: &mut [Vec<QubitId>; 2]) {{'
 assert s.count(needle)==1
 s=s.replace(needle,needle.replace(name,name+'_product_inner',1))
 s+='\n'+needle+'\n'+frame(name+'_before','t','None','Some(p)','letter')+f'    {name}_product_inner(c,t,letter,p);\n'+frame(name+'_after','t','None','Some(p)','letter')+'}\n'
needle='            y15::fwd_tick0_one(c, &letter, &mut pay);'
assert s.count(needle)==1
s=s.replace(needle,frame('pay_fwd_tick0_before','t','None','Some(&pay)','&letter')+needle+'\n'+frame('pay_fwd_tick0_after','t','None','Some(&pay)','&letter'))
for name,forward in [('n2_pay_fwd_last',True),('n2_pay_rev_last',False)]:
 args='c: &mut Builder, letter: &[QubitId], p: &mut [Vec<QubitId>; 2]'+(', skip_rot: bool' if forward else '')
 needle=f'fn {name}({args}) {{';assert s.count(needle)==1
 s=s.replace(needle,needle.replace(name,name+'_product_inner',1))
 skip='skip_rot'if forward else'false'
 s+='\n'+needle+'\n'+frame(name+'_before','rounds()-1','None','Some(p)','letter',skip)+f'    {name}_product_inner(c,letter,p'+(',skip_rot'if forward else'')+');\n'+frame(name+'_after','rounds()-1','None','Some(p)','letter',skip)+'}\n'
needle='pub(crate) fn divide_dbg(c: &mut Builder, y: &[QubitId], x: &[QubitId], keep_p1: bool) -> Vec<QubitId> {'
assert s.count(needle)==1
s=s.replace(needle,needle+'\n    PRODUCT_WALK_SCOPE.with(|s|s.set("div"));')
needle='pub fn multiply(c: &mut Builder, y: &[QubitId], x: &[QubitId]) {'
assert s.count(needle)==1
s=s.replace(needle,needle+'\n    PRODUCT_WALK_SCOPE.with(|s|s.set("mul"));')
needle='    let mut wk = Walk { r, tape: Vec::new() };';assert s.count(needle)==2
s=s.replace(needle,needle+'\n'+frame('walk_seed','usize::MAX','Some(&wk.r)'))
needle='    let q0 = pmark(c);\n    // endpoint: rails (+-1, +-1); P = (s0 lam, s1 lam)';assert s.count(needle)==1
s=s.replace(needle,frame('div_before_endpoint','rounds()','Some(&wk.r)','Some(&pay)')+needle)
needle='    let mut pay = if Y29_ENDNEG {';assert s.count(needle)==1
s=s.replace(needle,frame('mul_before_endpoint','rounds()','Some(&wk.r)')+needle)
needle='    pacc(c, "mul.endpoint", q0);';assert s.count(needle)==1
s=s.replace(needle,needle+'\n'+frame('mul_after_endpoint','rounds()','Some(&wk.r)','Some(&pay)'))
s+=r'''
thread_local!{static PRODUCT_WALK_SCOPE:std::cell::Cell<&'static str>=const{std::cell::Cell::new("none")};}
fn product_walk_frame(c:&Builder,label:&str,t:usize,r:Option<&[Vec<QubitId>;2]>,p:Option<&[Vec<QubitId>;2]>,letter:&[QubitId],skip:bool){
 use std::io::Write;let ids=|q:&[QubitId]|if q.is_empty(){"-".to_owned()}else{q.iter().map(|q|q.0.to_string()).collect::<Vec<_>>().join(",")};
 let rs=r.map(|r|[ids(&r[0]),ids(&r[1])]).unwrap_or(["-".into(),"-".into()]);let ps=p.map(|p|[ids(&p[0]),ids(&p[1])]).unwrap_or(["-".into(),"-".into()]);
 let scope=PRODUCT_WALK_SCOPE.with(|s|s.get());let mut file=std::fs::OpenOptions::new().append(true).create(true).open(PRODUCT_WALK_PATH).unwrap();
 writeln!(file,"{scope}\t{label}\t{t}\t{}\t{}\t{skip}\t{}\t{}\t{}\t{}\t{}",c.op_count(),lowrel(),rs[0],rs[1],ps[0],ps[1],ids(letter)).unwrap();
}
'''
s+='\nconst PRODUCT_WALK_PATH:&str="'+str((evidence/'walk-frames.tsv').resolve()).replace('\\','/')+'";\n'
(output/'leapfrog.rs').write_text(s,newline='\n')
