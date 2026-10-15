from pathlib import Path
import shutil
root=Path(__file__).resolve().parent
text=(root/'cond_pass_original.rs').read_text()
# Retain the original pass as reference; independently extend classical-outcome
# admission and snapshot exact physical holder aliases at every quantum read.
needle='    bcreator: Vec<u32>, bslot: Vec<u32>, bderived: Vec<bool>, depth_after: Vec<u8>,'
assert text.count(needle)==1;text=text.replace(needle,needle+'\n    guard_readhold: HashMap<(u32,u32),(u32,u32)>,')
needle='    let mut misc = Vec::new(); let mut unc = Vec::new();';assert text.count(needle)==1;text=text.replace(needle,needle+'''
    let mut guard_readhold=HashMap::new();
    let mut guard_eligible=HashSet::new();let mut pending=vec![None;nq as usize];
    for (j,o)in ops.iter().enumerate(){match o.kind{
      K_CCX=>pending[o.t as usize]=Some(j as u32),
      K_HMR=>{if let Some(p)=pending[o.t as usize].take(){guard_eligible.insert(p);}},
      K_CX|K_X|K_R=>pending[o.t as usize]=None,
      K_SWAP=>{pending[o.t as usize]=None;pending[o.c1 as usize]=None;},_=>{}
    }}
''')
needle='                if !c.zonly { continue; }';assert text.count(needle)==1
text=text.replace(needle,'                if c.ctx==0 && guard_eligible.contains(&c.op) {let alias=|v|holders.get(&v).and_then(|qs|qs.iter().copied().find(|&q|q!=c.wire)).unwrap_or(NQ);let pair=(alias(c.va),alias(c.vb));if pair.0!=NQ&&pair.1!=NQ{guard_readhold.insert((ci,k32),pair);}}\n'+needle)
needle='bcreator, bslot, bderived, depth_after }';assert text.count(needle)==1;text=text.replace(needle,'bcreator, bslot, bderived, depth_after, guard_readhold }')
text=text.replace('pub fn lazy_single(ops:Vec<Op>)->Vec<Op>{','pub fn lazy_single_reference(ops:Vec<Op>)->Vec<Op>{',1)
start=text.index('pub fn lazy_single_reference(');end=text.index('\n#[cfg(test)]',start)
new=text[start:end].replace('pub fn lazy_single_reference(','pub fn lazy_single(')
new=new.replace('for c in &a.contribs {','for (ci,c) in a.contribs.iter().enumerate() {')
new=new.replace(' || a.bderived[c.end_bit as usize]','')
new=new.replace(' || !c.end_sole','')
new=new.replace('if c.ctx!=0 || c.swapped','if c.swapped')
new=new.replace('if original.cc!=NQ || l[e].cc!=NQ','if (p>0&&a.depth_after[p-1]!=0) || l[e].cc!=NQ')
new=new.replace('a.cx.sets[a.opctx[j as usize] as usize]==vec![c.end_bit]','a.cx.sets[a.opctx[j as usize] as usize]=={let mut ctx=a.cx.sets[c.ctx as usize].clone();ctx.push(c.end_bit);ctx.sort_unstable();ctx.dedup();ctx}')
new=new.replace('let valid=nb;let temporary=nb+1;nb+=2;','let valid=nb;let temporary=nb+1;let enabled=nb+2;nb+=3;')
new=new.replace('ed.replace.insert(c.op,vec![store(valid,false),store(temporary,false)]);','let mut init=vec![store(valid,false),store(temporary,false),store(enabled,original.cc==NQ)];if original.cc!=NQ{init.push(L{kind:K_BINV,c2:NQ,c1:NQ,t:NQ,ct:enabled,cc:original.cc,rt:NQ});}ed.replace.insert(c.op,init);')
new=new.replace('push(temporary)];','push(temporary),push(enabled)];')
new=new.replace('block.push(pop);block.push(store(temporary,false));','block.push(pop);block.push(pop);block.push(store(temporary,false));')
new=new.replace('extend([store(valid,false),store(temporary,false)]);','extend([store(valid,false),store(temporary,false),store(enabled,false)]);')
needle='  if outcome_uses.get(&c.end_bit).is_none_or(|v|v.as_slice()!=[fix]){continue;}'
assert new.count(needle)==1;new=new.replace(needle,'  // Unchanged HMR draws make arbitrary original outcome uses and descendants safe.')
needle='  let Some(forms)=forms_at(&l,&a,p,&[original.c1,original.c2],&reads) else{continue;};'
assert new.count(needle)==1
new=new.replace(needle,'''
  let affine=forms_at(&l,&a,p,&[original.c1,original.c2],&reads);
  let mut forms=Vec::new();let mut admitted=true;let mut holder_uses=0;
  for (ri,&at)in reads.iter().enumerate(){
   let aliases=a.guard_readhold.get(&(ci as u32,at as u32));
   let alias=aliases.and_then(|&(x,y)|{
    if [x,y].iter().any(|&q|q==c.wire||kept.iter().any(|&(w,s,z,_)|w==q&&s<(at as u32)&&(at as u32)<=z)){None}else{Some((x,y))}
   });
   if let Some((x,y))=alias{forms.push(vec![(vec![x],false),(vec![y],false)]);holder_uses+=1;}
   else if let Some(ref fs)=affine{forms.push(fs[ri].clone());}
   else{admitted=false;break;}
  }
  if !admitted{continue;}
''')
text+='\n'+new+'\n'+(root/'guard_tests.rs').read_text()
needle='        let k32 = k as u32;'
assert text.count(needle)>=1
text=text.replace(needle,needle+'''
        if std::env::var("GUARD_VALUE_AT").ok().and_then(|s|s.parse::<usize>().ok())==Some(k){
          fn form(v:&Vals,id:u32,d:usize)->String{if d==0{return format!("v{id}");}match v.node[id as usize]{(0,_,_)=>"0".into(),(1,_,_)=>"1".into(),(T_OPQ,_,_)=>format!("opaque{id}"),(T_AND,x,y)=>format!("({}&{})",form(v,x,d-1),form(v,y,d-1)),(T_COND,c,x)=>format!("ctx{c}*{}",form(v,x,d-1)),(T_SET,x,_)=>format!("xor{:?}",v.store[x as usize].iter().map(|&x|form(v,x,d-1)).collect::<Vec<_>>()),_=>format!("v{id}")}}
          for q in [379usize,380,381,967,968,918]{println!("GUARD_VALUE at={k} q={q} value_id={} form={}",qv[q],form(&v,qv[q],5));}
          break;
        }
''',1)
text+='\npub fn guard_values(ops:&[Op],at:usize){std::env::set_var("GUARD_VALUE_AT",at.to_string());let l:Vec<_>=ops.iter().map(to_l).collect();let _=analyze(&l);}\n'
text+='\n'+(root/'phase_expand.rs').read_text()
(root/'tool/src/cond_pass.rs').write_text(text)
main=root/'tool/src/main.rs';s=main.read_text();needle='if a.get(1).is_some_and(|v|v=="values")';phase='if a.get(1).is_some_and(|v|v=="phase"){let ops=cond_pass::phase_expand(load_ops(&a[2]).unwrap());write_ops(&ops,Path::new(&a[3])).unwrap();return;}'
if phase not in s:s=s.replace(needle,phase+needle);main.write_text(s)
print('prepared guard-tree pass',len(text))
