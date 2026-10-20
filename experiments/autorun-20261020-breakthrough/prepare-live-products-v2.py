from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-live-products-20261020';r=root/'experiments/breakthrough-live-products-v2-20261020';r.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore','PLAN.md','run.py']:shutil.copyfile(old/p,r/p)
s=(old/'main.rs').read_text();needle='o.c_condition=BitId(cc);o.validate();o}';assert s.count(needle)==1;s=s.replace(needle,'o.c_condition=BitId(cc);if k==K::AppendToRegister{o.r_target=RegisterId(0);}o.validate();o}')
needle='assert!(out.iter().all(|o|!matches!(o.kind,K::CX|K::CZ)||o.q_control1!=o.q_target));}'
assert s.count(needle)==1;s=s.replace(needle,'assert!(out.iter().all(|o|!matches!(o.kind,K::CX|K::CZ)||o.q_control1!=o.q_target));let mut ops=fixture(false,false,false);ops.truncate(7);ops.push(op(K::CCZ,0,1,4,n,n));let(out,hits,_)=simplify(&ops);paired(&ops,&out);assert_eq!(hits.len(),1);assert_eq!(out.last().unwrap().kind,K::Z);}')
where=s.rfind('\n}');assert where>0
s=s[:where]+r'''
#[test]fn sparse_parity_keeps_large_exact_support_and_detects_missing_rows_and_constants(){for one in[false,true]{let mut q=vec![(1..=21).collect::<E>(),(1..=20).collect::<E>()];if one{q[0].insert(0,0);}let mut index=HashMap::new();for(w,v)in q.iter().enumerate(){index_add(&mut index,w,v);}let(controls,constant)=parity(&vec![21],&q,&index,None).unwrap();assert_eq!(controls,vec![0,1]);assert_eq!(constant,one);assert!(parity(&vec![21],&q,&index,Some(0)).is_none());let mut bad=0;for assignment in[0u64,1,2,0x123456,0x1fffff]{let eval=|e:&E|e.iter().fold(false,|a,&v|a^if v==0{true}else{assignment>>(v-1)&1!=0});assert_eq!(eval(&vec![21]),controls.iter().fold(constant,|v,&w|v^eval(&q[w])));bad+=u64::from(eval(&vec![21])!=(eval(&q[0])^constant));}assert!(bad>0);}}
'''+s[where:];(r/'main.rs').write_text(s)
with(r/'PLAN.md').open('a')as out:out.write('\nV1 tests stopped before scans because the fixture helper validated register annotations before setting their register ID. V2 fixes only fixture construction and strengthens self-target/large-support/constant/omitted-row controls. The simplifier algorithm is unchanged. All five native controls must pass before scans. V1 source and original failed tests remain.\n')
print(r)
