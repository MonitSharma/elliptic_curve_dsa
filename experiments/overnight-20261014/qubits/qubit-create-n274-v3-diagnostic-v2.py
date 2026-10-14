"""Research-only stage diagnostics; frozen candidate sources never modified."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
source,dest,ev=map(lambda s:Path(s).resolve(),sys.argv[1:4])
for name in subprocess.check_output(['git','-C',str(source),'diff','HEAD','--name-only'],text=True).splitlines():shutil.copyfile(source/name,dest/name)
p=dest/'src/point_add/tests_midg_k24.rs';t=p.read_text();a=t.index('#[test]\nfn reserve9_crossing_payload_3713_exact_shadow_native');z=t.index('#[test]',a+10);test=t[a:z]
test=test.replace('reserve9_crossing_payload_3713_exact_shadow_native','n274_diagnostic_payload3713_stages')
old='let record=rec(&mut b,|b|column_pl(b,&mut fd,cp,&sc,Some(&pl)));let forward=emitted(&mut b,&record,false);let inverse=emitted(&mut b,&record,true);'
assert old in test
test=test.replace(old,'''std::env::set_var("FD_MARK","1");std::env::set_var("D3_TRACE_PHASE","1");let original_fd=Fd{ring:ring.clone(),q:q.clone(),sy:sy.clone(),sx:sx.clone(),ph,cnt:q[121..].to_vec()};
    super::frogdrop_col::MARKS.with(|m|m.borrow_mut().clear());column_pl(&mut b,&mut fd,cp,&sc,Some(&pl));let forward=b.ops.clone();let marks=super::frogdrop_col::MARKS.with(|m|m.borrow().clone());
    let mut rb=builder();let _all=rb.alloc_n(691);let mut rfd=original_fd;super::frogdrop_col::MARKS.with(|m|m.borrow_mut().clear());column_pl(&mut rb,&mut rfd,cp,&sc,None);let reference=rb.ops.clone();let rmarks=super::frogdrop_col::MARKS.with(|m|m.borrow().clone());''')
test=test.replace('for seed in 0..4','for seed in 0..1')
start=test.index('        let got=run(&forward,691');test=test[:start]+r'''
        for &(off,stage) in &marks{if !(stage<=11||[1501,1502,1503,1504,1505].contains(&stage)){continue;}let got=run(&forward[..off],691,&|w|*w=input.clone());let mismatched:Vec<_>=if let Some(&(rpos,_))=rmarks.iter().find(|(_,s)|*s==stage){let baseline=run(&reference[..rpos],691,&|w|*w=input.clone());got.q[..432].iter().zip(&baseline.q[..432]).enumerate().filter_map(|(i,(x,y))|if x!=y{Some(i)}else{None}).collect()}else{vec![]};
            eprintln!("N274_STAGE stage={stage} ops={off} no_payload_mismatch={mismatched:?} q118={:x} sx={:x} pool_g={:x} ph={:x} sy={:x} phase={:x}",got.q[q[118].0 as usize],get(&got.q,&sx,0),got.q[pool[12].0 as usize],got.q[ph.0 as usize],get(&got.q,&sy,0),got.phase);
        }
        let got=run(&forward,691,&|w|*w=input.clone());let bad:Vec<_>=got.q.iter().zip(&expected).enumerate().filter_map(|(i,(x,y))|if x!=y{Some(i)}else{None}).collect();eprintln!("N274_DIAGNOSTIC_FINAL bad={bad:?} phase={:x}",got.phase);
    }
}
'''
p.write_text(t+test)
manifest=dict(scope='research-only n274-v3 diagnostic; not candidate/score',parent_source=str(source),parent_manifest_sha256=hashlib.sha256((ev/'candidate-n274-v3-manifest.json').read_bytes()).hexdigest(),source_sha256={p:hashlib.sha256((dest/p).read_bytes()).hexdigest()for p in subprocess.check_output(['git','-C',str(dest),'diff','HEAD','--name-only'],text=True).splitlines()})
(ev/'n274-v3-diagnostic-v2-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
