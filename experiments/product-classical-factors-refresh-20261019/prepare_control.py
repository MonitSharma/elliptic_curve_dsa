from pathlib import Path
r=Path(__file__).resolve().parent
s=(r.parent/'product-order-20261019/trace-tool/trace.rs').read_text()
s=s[:s.index('fn main()')].replace('#[path="../io.rs"]mod io;','mod io;')
s=s.replace('order-control-physical-RNG-20261019','classical-factor-control-physical-RNG-20261019')
s+='''fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),4);let old=io::load_ops(&a[1]);let new=io::load_ops(&a[2]);assert_eq!(dims(&old),dims(&new));let mut rows=vec![];let mut total_saved=0u64;
 for batch in 0..8{let mut r=rng("classical-factor-control-raw-inputs-20261019",batch);let mut input=vec![];let mut seen=std::collections::BTreeSet::new();for o in &old{if o.kind==K::AppendToRegister{for(q,i)in [(true,o.q_target.0),(false,o.c_target.0)]{if i!=NO&&seen.insert((q,i)){input.push((q,i as usize,word(&mut r)));}}}}let phase=word(&mut r);let x=run(&old,batch,&input,phase);let y=run(&new,batch,&input,phase);assert_eq!(x.0,y.0,"every original quantum wire");assert_eq!(x.1,y.1,"every original classical bit");assert_eq!(x.2,y.2,"phase");assert_eq!(x.4,y.4,"physical RNG continuation");assert!(y.3<=x.3,"executed Toffolis cannot increase");total_saved+=x.3-y.3;rows.push(serde_json::json!({"batch":batch,"shots":64,"all_quantum_classical_phase_and_RNG_equal":true,"old_executed_Toffolis":x.3,"new_executed_Toffolis":y.3,"saved":x.3-y.3}));}
 let result=serde_json::json!({"status":"PROTECTED_SIMULATOR_CLASSICAL_FACTOR_FULL_TRANSCRIPT_CONTROL_PASS","scope":"512 raw assignments with same physical RNG and arbitrary initial phase; finite integration diagnostic, no statistical gate or full benchmark","original_Q":dims(&old).0,"output_Q":dims(&new).0,"saved_executed_Toffolis_total_on_512_control_shots":total_saved,"rows":rows});std::fs::write(&a[3],serde_json::to_string_pretty(&result).unwrap()).unwrap();println!("all eight full transcript controls pass; total saved={total_saved}");}
'''
(r/'factor_trace.rs').write_text(s,encoding='utf-8',newline='\n')
c=(r/'Cargo.toml').read_text()+'\n[[bin]]\nname="factor_trace"\npath="factor_trace.rs"\n'
(r/'Cargo-control.toml').write_text(c,encoding='utf-8',newline='\n')
p=(r/'preflight.py').read_text()
needle="allowed.update(parent(pid) for pid in workers)"
assert p.count(needle)==1
p=p.replace(needle,needle+'''
# Admit only the recorded source-screen process tree in this same experiment.
screen_pid=int((r/'run.pid').read_text())
if Path(f'/proc/{screen_pid}').exists():
    assert Path(f'/proc/{screen_pid}/cwd').resolve()==r
    assert b'bash' in Path(f'/proc/{screen_pid}/cmdline').read_bytes()
    table=[tuple(map(int,line.split())) for line in subprocess.check_output(['ps','-e','-o','pid=,ppid='],text=True).splitlines()]
    screen_tree={screen_pid};changed=True
    while changed:
        old_size=len(screen_tree);screen_tree.update(pid for pid,ppid in table if ppid in screen_tree);changed=len(screen_tree)!=old_size
    allowed.update(screen_tree)
''')
p=p.replace("'build_jobs':1,'screen_threads':1,","'build_jobs':1,'screen_threads':1,'concurrent_recorded_source_screen_threads':1,")
p=p.replace("assert 60+record['build_jobs']<=64","assert 60+record['build_jobs']+record['screen_threads']+record['concurrent_recorded_source_screen_threads']<=64")
p=p.replace('available>160*1024**3','available>192*1024**3')
(r/'control-preflight.py').write_text(p,encoding='utf-8',newline='\n')
