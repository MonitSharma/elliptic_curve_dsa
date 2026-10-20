from pathlib import Path
r=Path(__file__).parent;p=r/'tool/main.rs';s=p.read_text();needle='let mut replacement=None;';assert s.count(needle)==1;s=s.replace(needle,needle+'let gate=if o.c_condition==NO_BIT{base.clone()}else{alg.and(&base,&c[o.c_condition.0 as usize])};')
needle='if let Some((controls,one))=parity(&product,&q,&index,if o.kind==K::CCX{Some(t)}else{None}){';assert s.count(needle)==1
s=s.replace(needle,'let skip=if o.kind==K::CCX{Some(t)}else{None};let mut restricted=false;let reduced=parity(&product,&q,&index,skip).or_else(||{if gate==vec![0]{None}else{let target=alg.and(&product,&gate);let result=parity(&target,&q,&index,skip);restricted=result.is_some();result}});if let Some((controls,one))=reduced{')
needle='"expression":product';assert s.count(needle)==1;s=s.replace(needle,'"expression":product,"guard_restricted":restricted');s+=(r/'guarded-tests.rs').read_text();p.write_text(s)
