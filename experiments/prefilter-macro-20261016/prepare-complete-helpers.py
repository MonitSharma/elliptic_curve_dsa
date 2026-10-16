from pathlib import Path
import shutil,re,json,hashlib,subprocess
root=Path('/home/hclau/ecdsa_research/prefilter-macro-20261016');out=root/'additional'
point=root/'observer-tip/src/point_add';changed=[]
for name in ['y15_onefold.rs','leapfrog.rs','square.rs']:
 p=point/name;s=p.read_text();shutil.copy2(p,out/(name+'.before-complete'))
 if name=='leapfrog.rs':
  a='fn pacc(c: &Builder, name: &str, t0: f64) {';assert s.count(a)==1;s=s.replace(a,a+'\n    eprintln!("COMPONENT_END name={} at={}",name,c.op_count());')
 # Log complete void Builder helpers; no gates or argument evaluation changes.
 insert=[]
 for m in re.finditer(r'\bfn\s+(\w+)\s*\(',s):
  fn=m[1];body=s.find('{',m.end());sig=s[m.start():body]
  if not sig or '->'in sig or not re.search(r'\b(c|circ):\s*&mut Builder',sig):continue
  arg=re.search(r'\b(c|circ):\s*&mut Builder',sig)[1]
  # Lexical brace matching including strings and nested block comments.
  depth=1;i=body+1;mode='code';block=0
  while depth and i<len(s):
   ch=s[i];two=s[i:i+2]
   if mode=='line':
    if ch=='\n':mode='code'
   elif mode=='string':
    if ch=='\\':i+=1
    elif ch=='"':mode='code'
   elif mode=='block':
    if two=='/*':block+=1;i+=1
    elif two=='*/':block-=1;i+=1;mode='code'if not block else'block'
   elif two=='//':mode='line';i+=1
   elif two=='/*':mode='block';block=1;i+=1
   elif ch=='"':mode='string'
   elif ch=='{':depth+=1
   elif ch=='}':depth-=1
   i+=1
  assert depth==0,(name,fn)
  insert.append((body+1,f'\n    let macro_full_start={arg}.op_count();\n'))
  insert.append((i-1,f'\n    eprintln!("FULL_HELPER\\t{name}::{fn}\\t{{}}\\t{{}}",macro_full_start,{arg}.op_count());\n'))
 for at,text in sorted(insert,reverse=True):s=s[:at]+text+s[at:]
 p.write_text(s);changed.append((name,len(insert)//2))
(out/'complete-helper-source.patch').write_bytes(subprocess.check_output(['git','-C',str(root/'observer-tip'),'diff','--binary']))
(out/'complete-helper-source.json').write_text(json.dumps(dict(gate_inert=True,component_only=True,instrumented=changed,files={str(p.relative_to(root/'observer-tip')):hashlib.sha256(p.read_bytes()).hexdigest()for p in point.rglob('*')if p.is_file()}),indent=2)+'\n');print(changed)
