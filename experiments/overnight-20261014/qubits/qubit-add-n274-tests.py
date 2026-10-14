"""Finish N274 component fixtures before source freezing; original inputs fixed."""
from pathlib import Path
import hashlib,json,sys
source,packet,out=map(Path,sys.argv[1:4])
p=source/'src/point_add/midg.rs';t=p.read_text();old='preposition_qk(b,&q129a,&fd.sy,sx[6],21';assert old in t;t=t.replace(old,'preposition_qk(b,&q129a,&fd.sy[..7],sx[6],21');p.write_text(t)
p=source/'src/point_add/tests_midg_k24.rs';t=p.read_text();a=t.index('#[test]\nfn n274_sz_donor_boundaries');tail=t[a:];tail=tail.replace('chain(243..275)','chain(242..274)').replace('%275','%274').replace('[101usize,127,128,160,0,100,160,255]','[101usize,127,128,160,161,100,160,255]').replace('(101..=160)','(101..=161)').replace('width=692','width=691');t=t[:a]+tail
script=Path(__file__).with_name('qubit-add-k32-column-tests.py').read_text();prefix=script[script.index('def states(dx):'):script.index('\n\nselected={}')];ns={'P':2**256-2**32-977};exec(prefix,ns);states=ns['states'];P=ns['P'];selected={}
for line in packet.read_text().splitlines():
    if line.startswith('#'):continue
    w=line.split();idx=int(w[0]);tx,ty,ox,oy,ex,ey=[int(x,16)for x in w[1:7]]
    for division,dx in ((1,(tx-ox)%P),(2,(ex-ox)%P)):
        for ci,state in enumerate(states(dx)):
            labels=[]
            if idx==0 and division==1 and ci==0:labels.append('wide_first_column')
            if state['kind']in('HR','HT')and state['sy_actual']in(95,96):labels.append(f"{state['kind']}_SY{state['sy_actual']}")
            if idx==1170 and division==2 and ci==35:labels.append('mixed_q21_shot1170')
            for label in labels:
                if label not in selected:selected[label]=dict(label=label,shot=idx,division=division,dx=hex(dx),column=ci,**state)
    if len(selected)==6:break
assert len(selected)==6,selected.keys()
cases=[]
for label,row in sorted(selected.items()):
    a,z=row['before'],row['after'];cases.append('("'+label+'",'+str(row['column'])+',['+','.join('"'+format(v,'x')+'"'for v in a[:3])+'],'+','.join(str(v)for v in a[3:])+',['+','.join('"'+format(v,'x')+'"'for v in z[:3])+'],'+','.join(str(v)for v in z[3:])+')')
a=t.index('#[test]\nfn n274_v2_full_column_new_boundaries_native');z=t.index('#[test]',a+10);part=t[a:z];start=part.index('let cases=&[')+len('let cases=&[');end=part.index('];let (cols',start);part=part[:start]+','.join(cases)+part[end:];t=t[:a]+part+t[z:]
# Exact original1170 payload extends the inherited true offset recurrence.
a=t.index('#[test]\nfn cap24_counterexample8048_exact_column_payload_native');z=t.index('#[test]',a+10);payload=t[a:z]
for old,new in [('cap24_counterexample8048_exact_column_payload_native','n274_q21_counterexample1170_payload_native'),('36f0fbac70592fc4b0dd5063485688e95619d5bfd049d59dddf6c7f7dc28b5a4','e1a14a46e6340fd02bde43002b9b85d32649195df078b8aa7efe88ce0964f802'),('let j=25','let j=36'),('8505374','2216631'),('cols[24]','cols[35]'),('cp.sz.1<=255&&cp.sy.1+23<128','cp.sz.1<=255&&cp.sy.1+23>=128'),('24,24,40,false','24,22,40,false'),('1u64)<<23','1u64)<<21'),('8048','1170'),('CAP24','Q21_SX6'),('width=692 column=24 euclid_step=25','width=691 column=35 euclid_step=36'),('q23_owner=sw','q21_owner=SX6')]:payload=payload.replace(old,new)
t+='\n'+payload
t+=r'''

#[test]
fn n274_q21_owned_preposition_dirty_inverse_phase(){
    let mut total=0;let mut coefficients=0;
    for mode in 0..3 {
        let mut b=builder();let ring=b.alloc_n(274);let q=b.alloc_n(128);let sy=b.alloc_n(8);let sx=b.alloc_n(8);let ph=b.alloc();let pool=b.alloc_n(13);let dirty=b.alloc_n(259);assert_eq!(b.width(),691);
        let control=if mode==1{pool[8]}else{pool[12]};let mut cycle=q.clone();cycle.push(pool[9]);
        cycle.extend([pool[11],pool[10],sx[7],pool[6],pool[7],ph]);
        if mode==1{cycle.extend([pool[12],sx[1]]);}else{cycle.extend([pool[8],sy[7]]);}
        cycle.push(sx[6]);assert_eq!(cycle.len(),138);assert!(!cycle.contains(&control));
        let first=if mode==1{super::midg::preposition_owned_qk(&mut b,&cycle,&sy,sx[1],16,control,(1,128),&dirty)}else{vec![]};
        let pre21=super::midg::preposition_qk(&mut b,&cycle,if mode==1{&sy}else{&sy[..7]},sx[6],21,control,(1,116),&dirty);
        let pre22=if mode==2{super::midg::preposition_nonlast_qk(&mut b,&cycle,&sy,ph,22,control,(1,104),&dirty)}else{vec![]};
        let pre23=if mode==2{super::midg::preposition_nonlast_qk(&mut b,&cycle,&sy,pool[8],23,control,(1,104),&dirty)}else{vec![]};
        let record=rec(&mut b,|b|{b.play(&first,false);b.play(&pre21,false);b.play(&pre22,false);b.play(&pre23,false);});let forward=emitted(&mut b,&record,false);let inverse=emitted(&mut b,&record,true);
        let mut rng=Rng::new(0x20261014_210016+mode as u64);
        for pattern in 0..8{for block in 0..4{
            let mut input:Vec<_>=(0..691).map(|_|rng.next()).collect();input[control.0 as usize]=0;let mut expected=input.clone();
            for lane in 0..64{let size=block*64+lane;put(&mut input,&sy,lane,N::from(size as u64));let active=(1..=if mode==2{104}else{128}).contains(&size);if !active{continue;}let mask=1u64<<lane;input[control.0 as usize]|=mask;
                for &wire in &cycle{input[wire.0 as usize]&=!mask;}
                // Restore the size register after clearing its borrowed high bit.
                put(&mut input,&sy,lane,N::from(if mode==1{size}else{size&127}as u64));
                for i in 0..size.min(128){if (i+lane)%3!=0{input[q[i].0 as usize]|=mask;}}
                if mode==1&&size<=121&&pattern&1!=0{input[sx[1].0 as usize]|=mask;}
                if size<=116&&pattern&2!=0{input[sx[6].0 as usize]|=mask;}
                if mode==2&&pattern&1!=0{input[ph.0 as usize]|=mask;}
                if mode==2&&pattern&4!=0{input[pool[8].0 as usize]|=mask;}
            }
            expected.clone_from(&input);
            for lane in 0..64{let size=block*64+lane;if input[control.0 as usize]>>lane&1==0{continue;}let mut swap=|owner:QubitId,index:usize|{if index>=cycle.len()||cycle[index]==owner{return;}let a=owner.0 as usize;let z=cycle[index].0 as usize;let delta=((expected[a]^expected[z])>>lane)&1;expected[a]^=delta<<lane;expected[z]^=delta<<lane;};
                if mode==1{swap(sx[1],size+16);}if size<=116{swap(sx[6],size+21);}if mode==2{swap(ph,size+22);swap(pool[8],size+23);}
            }
            let got=run(&forward,691,&|words|*words=input.clone());assert_eq!(got.q,expected,"q21 prepared; normalized A/B target ownership, inactive dirty aliases");assert_eq!(got.phase,0);let(sym,n)=symbolic(&forward,input.clone());assert_eq!(sym,got.q);coefficients+=n;let back=run(&inverse,691,&|words|*words=got.q.clone());assert_eq!(back.q,input);assert_eq!(back.phase,0);let(sym,n)=symbolic(&inverse,got.q);assert_eq!(sym,input);coefficients+=n;total+=64;
        }}
    }
    eprintln!("Q21_SX6_OWNER_PASS cases={total} modes=A,B,pure24 full_SY_words=256 admitted_q21_SY_max=116 admitted_q16_SY_max=121 inactive_arbitrary=true all_wire_inverse=true phase=0 measurement_coefficients={coefficients} width=691 scope=normalized_preposition_only");
}
'''
p.write_text(t)
# Add source schedule's exact tightcounter maps and early/lateswitch cases.
p=source/'src/point_add/tests_frogdrop.rs';t=p.read_text();a=t.index('#[test]\nfn n274_ordinary_four_lane_map_exact');z=t.index('#[test]',a+10);prototype=t[a:z]
loop=prototype.replace('n274_ordinary_four_lane_map_exact','n274_maps_counter_and_switch_lifetimes_native')
loop=loop.replace('let cp = &cols[0];','for index in [35usize,85,96,110,113,114,115,116,117,118,119]{\n    let cp = &cols[index];')
loop=loop.replace('assert!(!cp.sw && cp.emax == 21 && cp.n == 274);','assert!(cp.emax == 21 && cp.n == 274);')
loop=loop.replace('let mut cases = Vec::new();','let mut cases = Vec::new();\n    input[ph.0 as usize]=u64::MAX;')
loop=loop.replace('put(&mut input, &q, lane, &x);','put(&mut input, &q[..121], lane, &x);\n        if cp.dn{put(&mut input,&q[121..],lane,&N::from(1+(lane as u64%((1u64<<cp.cntw)-1))));}\n        else if cp.sw && lane%2==0{input[sc.sw.0 as usize]|=1u64<<lane;}')
loop=loop.replace('assert_eq!(get(&f.q, &q, lane), *y','assert_eq!(get(&f.q, &q[..121], lane), *y')
loop=loop.replace('let both = run(&b.ops,','for &wire in &q[121..]{assert_eq!(f.q[wire.0 as usize],input[wire.0 as usize],"counter parked and returned column{index}");}\n    let both = run(&b.ops,')
loop=loop.replace('D2_MAP_EXTENSION_PASS shots=64 width={} forward_ops={forward}','N274_MAP_COUNTER_PASS column={index} cntw={} sw={} shots=64 width={} forward_ops={forward}').replace('b.width());','cp.cntw,cp.sw,b.width());')
loop=loop.rstrip();assert loop.endswith('}');loop=loop[:-1]+'}\n}\n';t+='\n'+loop;p.write_text(t)
out.write_text(json.dumps(dict(scope='N274 component fixtures only; no benchmark/nonce tuning',packet_sha256=hashlib.sha256(packet.read_bytes()).hexdigest(),cases=list(selected.values()),source_owner='q21:SX6 last; A decoder reads low7 SY to avoid borrowedSY7 target alias; B pre16 then21'),indent=2)+'\n')
