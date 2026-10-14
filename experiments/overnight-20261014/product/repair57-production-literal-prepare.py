"""Literal original complete prefix state, actual live classical preserved."""
from pathlib import Path
import subprocess,sys,json,hashlib
base,out,*args=map(Path,sys.argv[1:]);snap=args.pop();subprocess.run([sys.executable,str(Path(__file__).with_name('repair57-production-sixteen-r1-prepare.py')),str(base),str(out),*map(str,args)],check=True)
assert int((snap/'run.exit').read_text())==0
states={}
for f in snap.glob('*-batch*.tsv'):
 for l in f.read_text().splitlines():
  src,mode,index,phase,q,b=l.split('\t');assert src=='c5_raw';assert len(q)==1234 and len(b)==1575;assert set(q+b)<=set('01');states[(mode,int(index))]=(int(phase),q,b)
dataset=json.loads((out/'product_repair57_sixteen.json').read_text());pool=json.loads(args[3].joinpath('before.json').read_text());literals=[]
def word(q,ids):return sum(int(q[i])<<j for j,i in enumerate(ids))
for c in dataset['cases']:
 phase,q,b=states[(c['mode'],c['index'])];assert word(q,pool['p'][0])==int(c['T'],16) and word(q,pool['p'][1])==int(c['B'],16);assert ''.join(q[i]for i in pool['letter'])==c['letter'];assert all(q[i]=='0'for i in pool['freeq']);literals.append((c['index'],phase,q,b))
assert len(literals)==16
(out/'product_repair57_literal.json').write_text(json.dumps({'scope':'Exact original finalizedraw fixedpastMR literal1234q/1575b/incomingphase atdepth0 pendingY33=0 old/finalindex3282766. Internal futureMR only quantified.','snapshot_files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in snap.glob('*-batch*.tsv')},'cases':[{'index':i,'phase':ph,'q':q,'b':b}for i,ph,q,b in literals]},indent=2)+'\n')
s=(out/'product_repair57_tests.rs').read_text();table='const LITERALS:&[(usize,u64,&str,&str)]=&[\n'+',\n'.join('(%d,%d,"%s","%s")'%l for l in literals)+'\n];\n';s=table+s
start=s.index('let mut q:Vec<_>=(0..nq).map');stop=s.index('let expected=q.clone();',start)
s=s[:start]+'''let ids=|a:&[QubitId]|a.iter().map(|x|x.0).collect::<Vec<_>>();let mut q=vec![0;nq];for lane in 0..64{let(_,_,qb,_)=LITERALS[lane%16];for(i,v)in qb.bytes().enumerate(){q[i]|=((v-b'0')as u64)<<lane;}}let actualphase=(0..64).fold(0u64,|p,l|p|(LITERALS[l%16].1<<l));'''+s[stop:]
needle='for dirty in[0,u64::MAX,0xa5a5a5a5a5a5a5a5]{let b=vec![dirty;nb];';assert s.count(needle)==1
s=s.replace(needle,'''for dirty in[0x123456789abcdef0,0,u64::MAX,0xa5a5a5a5a5a5a5a5]{let mut b=vec![0;nb];for lane in 0..64{let(_,_,_,bb)=LITERALS[lane%16];for(i,v)in bb.bytes().enumerate(){b[i]|=((v-b'0')as u64)<<lane;}}if dirty!=0x123456789abcdef0{for &i in BODY_FB{b[i as usize]=dirty;}for i in BODY_NB..nb{b[i]=dirty;}}''')
s=s.replace('0x124897da','actualphase').replace('REPAIR57_SIXTEEN_BDD_PROVED','REPAIR57_LITERAL_BDD_PROVED').replace('REPAIR57_SIXTEEN_FORWARD','REPAIR57_LITERAL_FORWARD')
(out/'product_repair57_tests.rs').write_text(s,newline='\n')
