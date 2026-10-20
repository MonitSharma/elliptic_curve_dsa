import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-core-loan-preflight-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE-v2.json').read_text())
assert not t.exists() and (old/'run-v2.exit').read_text().strip()=='0';assert all(sha(old/'observer'/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items());assert json.loads((old/'ADMISSION-RESULT.json').read_text())['cases'][1]['raw_sha256']=='d6934faaa92d07c13cbdbe0297682595f21c290ebe88e8e1297f373b36e09989'
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in (old/'observer/src/point_add').rglob('*'):
 if p.is_file():q=t/p.relative_to(old/'observer');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes()
def change(a,b):
 global raw
 assert raw.count(a)==1,(a,raw.count(a));raw=raw.replace(a,b)
header=b'fn fold_fwd_forms(c: &mut Builder, x: &[Lin], e: &[Lin; 3], nm: [QubitId; 3], k1: QubitId, k2: QubitId) -> (Vec<Lin>, Vec<Rec>) {'
change(header,header+b'\n    fold_fwd_forms_borrowed(c,x,e,nm,k1,k2,None)\n}\n'+header.replace(b'fn fold_fwd_forms(',b'fn fold_fwd_forms_borrowed(').replace(b'k2: QubitId)',b'k2: QubitId, borrowed_tt: Option<QubitId>)'))
start=raw.index(b'fn fold_fwd_forms_borrowed(');end=raw.index(b'\n}',start)+2;region=raw[start:end];a=b'    let tt = r_and(c, &mut recs, l(k1), l(k2));';assert region.count(a)==1;region=region.replace(a,b'    let tt=if let Some(q)=borrowed_tt{assert!(q!=k1&&q!=k2);l(q)}else{r_and(c,&mut recs,l(k1),l(k2))};');raw=raw[:start]+region+raw[end:]
header=b'    fn new(c: &mut Builder, k1: QubitId, k2: QubitId, n: usize, bits: Vec<crate::circuit::BitId>) -> T0Phase {'
change(header,header+b'\n        Self::make(c,k1,k2,n,bits,false)\n    }\n'+header.replace(b'fn new(',b'fn owned(')+b'\n        Self::make(c,k1,k2,n,bits,true)\n    }\n'+header.replace(b'fn new(',b'fn make(').replace(b'BitId>)',b'BitId>, owned: bool)'))
change(b'let direct=Y29_FAULT==0&&k1!=k2&&hard<1234;',b'let direct=!owned&&Y29_FAULT==0&&k1!=k2&&hard<1234;')
start=raw.index(b'fn t0_forms_body(');end=raw.index(b'\n}',start)+2;region=raw[start:end]
for a,b in [(b'let mut ph = T0Phase::new(c, k1, k2, N, bits);',b'let shared=super::super::phase_fit::cap()<1234;let mut ph=if shared{T0Phase::owned(c,k1,k2,N,bits)}else{T0Phase::new(c,k1,k2,N,bits)};'),(b'let fold_wires = 31 + (Y15_WIN - 7);',b'let fold_wires = 31-usize::from(shared) + (Y15_WIN - 7);'),(b'let (w, mut recs) = fold_fwd_forms(c, &x, &e, s, k1, k2);',b'let (w, mut recs)=fold_fwd_forms_borrowed(c,&x,&e,s,k1,k2,if shared{ph.t}else{None});')]:assert region.count(a)==1;region=region.replace(a,b)
raw=raw[:start]+region+raw[end:];raw+=(r/'tests.rs').read_bytes();p.write_bytes(raw);subprocess.run(['cp','-a','--reflink=auto',str(old/'observer/target'),str(t/'target')],check=True)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
f['source_files']={p.relative_to(t).as_posix():sha(p)for p in (t/'src/point_add').rglob('*')if p.is_file()};f['scope']='Share an immutable owned T0Phase AND(k1,k2) with the forms fold, avoiding duplicate computation/ownership and direct cubic phases. Phase owner outlives fold pop_chain; controls remain unchanged. Adjust fold workspace by exactly one owned product. Enable only hard<1234; baseline1234byteexact13f6. Native phase oracle comparison covers all14 core inputs, upper words, phase flags, guards and allmeasurementcoefficients, then20retainedcontrols/fullsource generation. No arithmetic cuts or finalgate/nonce/score.';(r/'SOURCE_FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
