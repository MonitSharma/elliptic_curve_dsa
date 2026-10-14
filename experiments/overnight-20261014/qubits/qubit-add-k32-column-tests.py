"""Generate independent exact-Euclid column cases from a preserved packet.

Selected cases are tests, not changes to nonce, packet or submission schedule.
Payload is absent; phase coefficients and every scratch/passenger are checked.
"""
from pathlib import Path
import hashlib
import json
import sys

root,packet,out=map(Path,sys.argv[1:4]);P=2**256-2**32-977


def states(dx):
    r,t=[P,dx],[0,1]
    while r[-1]:
        q=r[-2]//r[-1];r.append(r[-2]-q*r[-1]);t.append(t[-2]+q*t[-1])
    j=1;ph=False;dq=False;first=False;result=[]
    while j<len(r)-2:
        if dq:
            kind='Dq';before=(t[j],r[j+1],r[j],r[j+1].bit_length(),1,1)
            after=(t[j+1],r[j+1],r[j],r[j+1].bit_length(),1,0);dq=False;jnext=j+1
        elif ph:
            kind='firstHT' if first else 'HT'
            before=(t[j],r[j-1] if first else r[j],r[j] if first else r[j-1],(r[j-1] if first else r[j]).bit_length(),1,0)
            after=(t[j+1],r[j+1],r[j],r[j+1].bit_length(),1,0);first=False;jnext=j+1
        elif r[j].bit_length()<=128 and r[j].bit_length()>t[j].bit_length():
            kind='Dl';before=(r[j],t[j],t[j-1],t[j].bit_length(),0,0)
            after=(t[j],r[j+1],r[j],r[j+1].bit_length(),1,1);ph=True;dq=True;jnext=j
        elif r[j].bit_length()<=128:
            kind='Sw';before=(r[j],t[j],t[j-1],t[j].bit_length(),0,0)
            after=(t[j],r[j-1],r[j],r[j-1].bit_length(),1,0);ph=True;first=True;jnext=j
        else:
            kind='HR';before=(r[j],t[j],t[j-1],t[j].bit_length(),0,0)
            after=(r[j+1],t[j+1],t[j],t[j+1].bit_length(),0,0);jnext=j+1
        result.append(dict(kind=kind,j=j,before=before,after=after,sy_actual=(r[j] if kind in ('HT','firstHT') else t[j]).bit_length(),quotient=r[j-1]//r[j]))
        j=jnext
    return result


selected={}
for line in packet.read_text().splitlines():
    if line.startswith('#'):continue
    w=line.split();idx=int(w[0]);tx,ty,ox,oy,ex,ey=[int(x,16) for x in w[1:7]]
    for division,dx in ((1,(tx-ox)%P),(2,(ex-ox)%P)):
        for ci,state in enumerate(states(dx)):
            kind=state['kind'];sy=state['sy_actual'];q=state['quotient']
            # Components stay inside the current quotient/parking domain.
            if q>=2**23 or sy+q.bit_length()>136:continue
            labels=[]
            if kind in ('HR','HT') and sy in (98,99,128):labels.append(f'{kind}_SY{sy}')
            if kind in ('firstHT','Dl','Dq','Sw'):labels.append(kind)
            if idx==1937 and division==2 and state['j']==10:labels.append('shot1937_HR')
            if idx==4131 and division==1 and state['j']==100:labels.append('shot4131_HT')
            for label in labels:
                if label not in selected:selected[label]=dict(label=label,shot=idx,division=division,dx=hex(dx),column=ci,**state)
    if len(selected)==12 and idx>4131:break
required={f'{kind}_SY{sy}' for kind in ('HR','HT') for sy in (98,99,128)}|{'firstHT','Dl','Dq','Sw','shot1937_HR','shot4131_HT'}
assert required<=selected.keys(),required-selected.keys()
cases=[]
for label in sorted(required):
    row=selected[label];a=row['before'];z=row['after']
    cases.append('("'+label+'",'+str(row['column'])+',['+','.join('"'+format(v,'x')+'"' for v in a[:3])+'],'+str(a[3])+','+str(a[4]).lower()+','+str(a[5]).lower()+',['+','.join('"'+format(v,'x')+'"' for v in z[:3])+'],'+str(z[3])+','+str(z[4]).lower()+','+str(z[5]).lower()+')')
test=r'''

#[test]
fn k32_exact_column_crossings_boundaries_independent_phase(){
    use super::frogdrop_col::{Fd,ColScr,column_pl};
    let cases=&[CASES];let (cols,_,_)=super::pointadd_frogdrop::col_pars(&super::frogdrop_sched::from_text(super::pointadd_frogdrop::SCHED_FROGDROP));let mut coefficients=0;
    for &(label,ci,values,size,phase,switch,outvalues,outsize,outphase,outswitch)in cases{
        let mut b=builder();let ring=b.alloc_n(276);let q=b.alloc_n(128);let sy=b.alloc_n(8);let sx=b.alloc_n(8);let ph=b.alloc();let pool=b.alloc_n(13);let dirty=b.alloc_n(259);let rev:Vec<_>=ring.iter().rev().copied().collect();let mut fd=Fd{ring:ring.clone(),q:q.clone(),sy:sy.clone(),sx:sx.clone(),ph,cnt:q[121..].to_vec()};let cp=&cols[ci];let sc=ColScr::carve_col(&pool,&sx,&dirty,24,23,40,cp.sz.1>255);
        let parse=|s:&str|N::from_str_radix(s,16).unwrap();let mut input=vec![0u64;693];let mut rng=Rng::new(0x20261014_1234+ci as u64);for &id in &dirty{input[id.0 as usize]=rng.next();}
        for lane in 0..64{put(&mut input,&ring,lane,parse(values[0]));put(&mut input,&rev[..parse(values[1]).bit_len()],lane,parse(values[1]));put(&mut input,&q,lane,parse(values[2]));put(&mut input,&sy,lane,N::from(size as u64));}input[ph.0 as usize]=if phase!=0{u64::MAX}else{0};input[sc.sw.0 as usize]=if switch!=0{u64::MAX}else{0};
        let mut expected=input.clone();for &id in &ring{expected[id.0 as usize]=0;}for lane in 0..64{put(&mut expected,&ring,lane,parse(outvalues[0]));put(&mut expected,&rev[..parse(outvalues[1]).bit_len()],lane,parse(outvalues[1]));put(&mut expected,&q,lane,parse(outvalues[2]));put(&mut expected,&sy,lane,N::ZERO);put(&mut expected,&sx,lane,N::from(outsize as u64));}expected[ph.0 as usize]=if outphase!=0{u64::MAX}else{0};expected[sc.sw.0 as usize]=if outswitch!=0{u64::MAX}else{0};
        let record=rec(&mut b,|b|column_pl(b,&mut fd,cp,&sc,None));let forward=emitted(&mut b,&record,false);let inverse=emitted(&mut b,&record,true);let got=run(&forward,693,&|words|*words=input.clone());assert_eq!(got.q,expected,"case {label} col{ci} exact Euclid shadow plus all scratch/passengers");assert_eq!(got.phase,0,"case {label}");let(sym,n)=symbolic(&forward,input.clone());assert_eq!(sym,got.q);coefficients+=n;let back=run(&inverse,693,&|words|*words=got.q.clone());assert_eq!(back.q,input,"case {label} inverse");assert_eq!(back.phase,0);let(sym,n)=symbolic(&inverse,got.q);assert_eq!(sym,input);coefficients+=n;eprintln!("K32_COLUMN_CASE_PASS label={label} column={ci} width=693 lanes=64 payload=false independent_measurement_coefficients={n}");
    }
    eprintln!("K32_COLUMN_SUITE_PASS columns={} lanes={} independent_measurement_coefficients={coefficients} scope=full_columns_no_payload",cases.len(),cases.len()*64);
}
'''.replace('CASES',','.join(cases))
path=root/'src/point_add/tests_midg_k24.rs';assert 'fn k32_exact_column_crossings' not in path.read_text();path.write_text(path.read_text()+test)
report=dict(scope='Independent exact-Euclid native column fixtures; no payload or complete circuit score',packet_sha256=hashlib.sha256(packet.read_bytes()).hexdigest(),cases=list(selected.values()))
out.write_text(json.dumps(report,indent=2)+'\n')
