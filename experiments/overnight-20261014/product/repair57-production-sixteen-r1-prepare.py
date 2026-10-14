"""Actual16 prefix payloads; independent integer field reference per real letter."""
from pathlib import Path
import subprocess,json,sys,re,hashlib
base,out,*args=map(Path,sys.argv[1:]);log=args.pop();subprocess.run([sys.executable,str(Path(__file__).with_name('repair57-production-bdd-prepare.py')),str(base),str(out),*map(str,args)],check=True)
rows=[dict(re.findall(r'(\w+)=(\S+)',l))for l in log.read_text().splitlines()if l.startswith('PRODUCT_WALK_FRAME ')];bykey={(r['source'],r['mode'],r['index'],r['scope'],int(r['seq'])):r for r in rows};cases=[];p=2**256-2**32-977
for i,r in enumerate(rows):
 if r['source']=='c5_raw' and r['scope']=='div' and r['t']=='104' and r['label']=='fwd_tick_before':
  a=bykey[(r['source'],r['mode'],r['index'],r['scope'],int(r['seq'])+1)]
  # Original bitpacked export emits every frame's16 cases before next frame.
  assert a['label']=='fwd_tick_after' and a['index']==r['index'] and a['t']=='104'
  T,B=int(r['p0'],16),int(r['p1'],16);letter=a['letter'];assert len(letter)==5 and set(letter)<={'0','1'}
  weights=sum((1 if letter[j]=='0' else -1)*(1<<j)for j in range(3));shift=3+int(letter[3])+2*int(letter[4]);expected=(T+weights*B)*pow(1<<shift,-1,p)%p
  cases.append({'index':int(r['index']),'mode':r['mode'],'T':f'{T:064x}','B':f'{B:064x}','letter':letter,'weights':weights,'shift':shift,'expected':f'{expected:064x}','old_native':a['p0']})
assert len(cases)==16 and any(r['index']==94 for r in cases)
(out/'product_repair57_sixteen.json').write_text(json.dumps({'scope':'Original fixedprefix real payloads/letters; pastMR not quantified.','walk_log_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),'formula':'(T+sum_{j=0..2}(-1)^s_j*2^j*B)*2^-(3+k1+2*k2) modp','cases':cases},indent=2)+'\n')
s=(out/'product_repair57_tests.rs').read_text();tables='const CASES:&[(usize,&str,&str,u64,&str)]=&[\n'+',\n'.join('(%d,"%s","%s",%d,"%s")'%(c['index'],c['T'],c['B'],sum(int(v)<<j for j,v in enumerate(c['letter'])),c['expected'])for c in cases)+'\n];\n'
s=tables+s
start=s.index('hexbits(&mut q,&ids(&target),"71d7');end=s.index('let expected=q.clone();',start)
s=s[:start]+'''for id in ids(&target).iter().chain(ids(&source).iter()).chain(ids(&letter).iter()){q[*id as usize]=0;}for lane in 0..64{let(_,t,b,l,_)=CASES[lane%16];for(a,h)in[(&target,t),(&source,b)]{for(i,ch)in h.chars().rev().enumerate(){let v=ch.to_digit(16).unwrap();for j in 0..4{q[a[4*i+j].0 as usize]|=(((v>>j)&1)as u64)<<lane;}}}for(j,id)in letter.iter().enumerate(){q[id.0 as usize]|=(l>>j&1)<<lane;}}'''+s[end:]
needle='hexbits(&mut correct,&ids(&target),"d1e938360b1b3edd71badfc50840471cf63398873a042480743bffffb61167c2");';assert s.count(needle)==1
s=s.replace(needle,'''for id in &target{correct[id.0 as usize]=0;}for lane in 0..64{let(_,_,_,_,h)=CASES[lane%16];for(i,ch)in h.chars().rev().enumerate(){let v=ch.to_digit(16).unwrap();for j in 0..4{correct[target[4*i+j].0 as usize]|=(((v>>j)&1)as u64)<<lane;}}}''')
needle='if widths.0==57{assert_eq!(a.qubits,correct,"independent field reference and clean forward scratch");}'
assert s.count(needle)==1
s=s.replace(needle,'''if widths.0==57{for lane in 0..16{let bad=a.qubits.iter().zip(&correct).any(|(x,y)|(x^y)>>lane&1!=0);eprintln!("REPAIR57_SIXTEEN_FORWARD widths={widths:?} index={} dirty={dirty:#x} independent_allq_correct={} letter={:05b}",CASES[lane].0,!bad,CASES[lane].3);}assert_eq!(a.qubits,correct,"independent16 sourcebound field references and clean forward scratch");}''')
s=s.replace('REPAIR57_PRODUCTION_BDD_PROVED','REPAIR57_SIXTEEN_BDD_PROVED');(out/'product_repair57_tests.rs').write_text(s,newline='\n')
