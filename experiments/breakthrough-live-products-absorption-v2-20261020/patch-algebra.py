from pathlib import Path
p=Path(__file__).resolve().parent/'tool/algebra.rs';s=p.read_text();needle='products:HashMap<Triple,u32>, cap:';assert s.count(needle)==1;s=s.replace(needle,'products:HashMap<Triple,u32>, witness:HashMap<u32,Triple>, cap:')
needle=' fn and(&mut self,a:&E,b:&E)->E {';assert s.count(needle)==1
helpers=r""" fn implied(&self,r:u32,e:&E,depth:usize)->Option<bool>{if e.is_empty(){return Some(false);}if e==&vec![0]||e==&vec![r]{return Some(true);}if e==&Self::xor_raw(&vec![0],&vec![r]){return Some(false);}if depth==0{return None;}if let Some(t)=self.witness.get(&r){for f in t{if e==f{return Some(true);}if e==&Self::xor_raw(&vec![0],f){return Some(false);}}for f in t{if f.len()==1&&f[0]!=0{if let Some(v)=self.implied(f[0],e,depth-1){return Some(v);}}}}None}
 fn absorb(&mut self,p:&E,e:&E)->Option<E>{if p.len()!=1||p[0]==0{return None;}let r=p[0];if let Some(v)=self.implied(r,e,32){return Some(if v{p.clone()}else{vec![]});}let mut rest=vec![];let mut one=false;let mut changed=false;for &x in e{if let Some(v)=self.implied(r,&vec![x],32){one^=v;changed=true;}else{rest.push(x);}}if changed{let z=self.and(p,&rest);return Some(if one{self.xor(&z,p)}else{z});}None}
"""
s=s.replace(needle,helpers+needle)
needle='  let t=Self::triple(a,b);';assert s.count(needle)==1;s=s.replace(needle,'  if let Some(v)=self.absorb(a,b){return v;}if let Some(v)=self.absorb(b,a){return v;}'+chr(10)+needle)
needle='self.products.insert(t,v);vec![v]';assert s.count(needle)==1;s=s.replace(needle,'self.products.insert(t.clone(),v);self.witness.insert(v,t);vec![v]');p.write_text(s)
