from pathlib import Path
root=Path(__file__).resolve().parent
old=root.parent/'toffoli-readiness-20261015/wide-replay/crate'
dest=root/'exact-replay';(dest/'src').mkdir(parents=True,exist_ok=True)
src=(old/'src/main.rs').read_text()
needle='let(map,nold)=reconstruction(&left,&right,&std::fs::read_to_string(&args[3]).unwrap(),nb);'
assert src.count(needle)==1
src=src.replace(needle,'''let(map,nold)=if args[3]=="=" {
        let a:Vec<_>=left.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).copied().collect();
        let b:Vec<_>=right.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).copied().collect();
        assert_eq!(a,b,"original reset/measurement event order or operands changed");
        println!("IDENTICAL_MR_EVENTS count={}",a.len());((0..a.len()).collect(),a.len())
    }else if let Some(path)=args[3].strip_prefix("+"){
        let nold=left.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).count();
        let mut combined:Vec<usize>=(0..nold).collect();let mut previous=left.clone();let mut stages=0;
        for line in std::fs::read_to_string(path).unwrap().lines(){
            let fields:Vec<_>=line.split_whitespace().collect();assert_eq!(fields.len(),2);
            let next=load_ops(fields[0]).unwrap();let(_,previous_nb,_,_)=analyze_ops(previous.iter());
            let(local,nprevious)=if fields[1]=="="{
                let a:Vec<_>=previous.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).copied().collect();
                let b:Vec<_>=next.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).copied().collect();assert_eq!(a,b);((0..a.len()).collect(),a.len())
            }else{reconstruction(&previous,&next,&std::fs::read_to_string(fields[1]).unwrap(),previous_nb)};
            assert_eq!(nprevious,combined.len());
            combined=local.into_iter().map(|old|if old==usize::MAX{usize::MAX}else{combined[old]}).collect();
            previous=next;stages+=1;
        }
        assert_eq!(previous,right);println!("COMPOSED_MR_EVENTS stages={stages} original={nold} final={}",combined.len());(combined,nold)
    }else if let Some(path)=args[3].strip_prefix("@"){
        let old:Vec<_>=left.iter().enumerate().filter(|(_,o)|matches!(o.kind,OperationType::R|OperationType::Hmr)).collect();
        let right_mr:Vec<_>=right.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).collect();
        let index:std::collections::HashMap<usize,usize>=old.iter().enumerate().map(|(ordinal,(at,_))|(*at,ordinal)).collect();
        let positions:Vec<usize>=std::fs::read_to_string(path).unwrap().lines().map(|s|s.parse().unwrap()).collect();
        assert_eq!(positions.len(),right_mr.len());assert_eq!(positions.len(),old.len());
        let mut seen=std::collections::HashSet::new();let mut map=vec![];
        for (o,at) in right_mr.iter().zip(positions){assert!(seen.insert(at));assert_eq!(**o,left[at]);map.push(index[&at]);}
        println!("PERMUTED_MR_EVENTS count={}",map.len());(map,old.len())
    }else{reconstruction(&left,&right,&std::fs::read_to_string(&args[3]).unwrap(),nb)};''')
(dest/'src/main.rs').write_text(src)
for name in ['Cargo.toml','Cargo.lock']:(dest/name).write_bytes((old/name).read_bytes())
