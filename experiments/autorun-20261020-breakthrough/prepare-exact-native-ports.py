from pathlib import Path
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-exact-native-ports-20261020';r.mkdir(exist_ok=False)
(r/'.gitattributes').write_text('* -text\n');(r/'.gitignore').write_text('observer/\n__pycache__/\n*resource-preflight*\nevidence.tar.gz\n')
(r/'PLAN.md').write_text('''# Exact native ports from the newly official stack-v3 result

Public snapshot20261020T121753Z: product e3b5c51f, Q1234/T756481,
source88869d8c; T record remains a4ee, Q1464/T750911/sourcebe2902c2.
Port only two disclosed exact techniques from88869d8c into the validated local
a4ee source: rail strip R1/R2/EXT2 (all leapfrog diff hunks except recipe retune),
and G6-prime x257 top-column phase erase (only that body block in y15_onefold).
Copy the two rail netlist files with exact public Git-object provenance. Keep
the strengthened comparison settings and exact public140 schedule, square1408,
all unrelated native source and17 protected files. No new approximate windows,
square witness truncation, retunes, C3 selection or bound postpass table port.

Four declared research cases: control, rail-only, G6-only, both. The control RAW
records must exactly reproduce a4ee's frozen10543037 records/SHA318f7fc00 before
any new comparison. Each emits raw and one unchanged generic pass, nonce0. The
old bound finish/cache modules remain unchanged and unused by this research
wrapper; positive cases need a fresh self-contained bound finish and independently
derived lease proofs. Additional native rail controls exhaust all valid signed
inputs through16bits, sample larger odd/even widths through64, forward/inverse,
all four garbage-letter combinations and several measurement patterns; missing
phase repairs must be detected. Retained27 native controls precede all cases.
No final gate/nonce/official benchmark or scored result in this research run.
''')
(r/'rail-tests.rs').write_text('''
#[cfg(test)]mod exact_strip_port_tests{
 use super::*;use crate::sim::Simulator;use sha3::digest::XofReader;
 struct Fixed(u8);impl XofReader for Fixed{fn read(&mut self,out:&mut[u8]){out.fill(self.0);}}
 #[test]fn exact_strip_signed_all_inputs_phase_garbage_inverse_and_fault(){
  let mut checked=0u64;let mut faults=0u64;std::env::remove_var("LF_STRIP");
  for w in(4usize..=18).chain([25,26,31,32,63,64]){let mask=if w==64{u64::MAX}else{(1u64<<w)-1};let total=if w<=16{1usize<<w}else{4096};for inverse in[false,true]{for garbage in[false,true]{if !sb_avail(w,inverse,garbage){continue;}for combo in 0..if garbage{4}else{1}{
   let mut c=Builder::new();let ks=c.alloc_qubits(2);let t=c.alloc_qubits(w);let aux=c.alloc_qubits(2);let dropped=strip_barrel(&mut c,ks[0],ks[1],&t,inverse,garbage.then_some((aux[0],aux[1])));assert_eq!(dropped,!inverse);let(nq,nb)=c.i13_dims();let ops=c.take_ops();let faulty:Vec<_>=ops.iter().filter(|o|!matches!(o.kind,crate::circuit::OperationType::CZ|crate::circuit::OperationType::Z)).copied().collect();
   for begin in(0..total).step_by(64){for pattern in[0u8,255,0xa5,0x5a]{let mut rng=Fixed(pattern);let mut frng=Fixed(pattern);let mut s=Simulator::new(nq,nb,&mut rng);let mut f=Simulator::new(nq,nb,&mut frng);let mut expected=vec![0u64;nq];
    for lane in 0..64{let index=(begin+lane)as u64;let mut x=if w<=16{index}else{index.wrapping_mul(0x9e3779b97f4a7c15).rotate_left((index%63)as u32)}&mask;if x&15==0{x^=1;}let k2=u64::from(x&3==0);let k1=u64::from(x&1==0)^(k2*((x>>2)&1));let e=(k1+2*k2)as usize;let sign=x>>(w-1)&1;let y=if e==0{x}else{(x>>e)|if sign==1{mask^(mask>>e)}else{0}};assert_eq!(y&1,1);let ell=((combo&1)^((combo>>1)&1))as u64;let garbage_x=if garbage&&e>0{x.wrapping_sub(2*ell)&mask}else{x};let input=if inverse{y}else{garbage_x};let output=if inverse{garbage_x}else{y};
     for i in 0..w{s.qubits[t[i].0 as usize]|=((input>>i)&1)<<lane;expected[t[i].0 as usize]|=((if !inverse&&i==0{0}else{output>>i&1}))<<lane;}
     for(i,value)in[k1,k2].into_iter().enumerate(){s.qubits[ks[i].0 as usize]|=value<<lane;expected[ks[i].0 as usize]|=value<<lane;}
     for i in 0..2{let value=(combo>>i&1)as u64;s.qubits[aux[i].0 as usize]|=value<<lane;expected[aux[i].0 as usize]|=value<<lane;}
    }
    f.qubits.clone_from(&s.qubits);s.apply_iter(ops.iter());f.apply_iter(faulty.iter());assert_eq!(s.qubits,expected,"w={w} inverse={inverse} garbage={garbage} combo={combo} begin={begin} pattern={pattern}");assert_eq!(s.phase,0,"strip phase w={w} inverse={inverse} garbage={garbage} combo={combo} begin={begin} pattern={pattern}");faults+=u64::from(f.phase!=0);checked+=64;
   }}
  }}}}assert!(faults>0,"Missing phase repair must be detected");eprintln!("EXACT_STRIP_NATIVE checked={checked} phase_fault_batches={faults} exhaustive_widths=4..16 sampled_widths=17,18,25,26,31,32,63,64");
 }
}
''')
(r/'prepare.py').write_text("""import hashlib,json,re,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;parent=ws/'breakthrough-public322-square-final-20261020';old=parent/'candidate';t=r/'observer';repo=ws/'toffoli';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();f=json.loads((parent/'SOURCE-FREEZE.json').read_text());new='88869d8cc23fb72120dd52533f3e48277e9b36e4';base='0c3a0751ab66bd9144358d67563bcb79201cf636';assert all(sha(old/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());assert not t.exists();revision=subprocess.check_output(['git','-C',str(old),'rev-parse','HEAD']).decode().strip();subprocess.run(['git','-C',str(repo),'worktree','add','--detach',str(t),revision],check=True)
for p in f['source_files']:dest=t/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(old/p,dest)
patch=subprocess.check_output(['git','-C',str(repo),'diff','--no-ext-diff',base,new,'--','src/point_add/leapfrog.rs']);lines=patch.decode().splitlines(keepends=True);header=''.join(lines[:next(i for i,l in enumerate(lines)if l.startswith('@@'))]);hunks=re.split(r'(?m)(?=^@@)',patch.decode()[len(header):]);assert 'HEO_PIN_SQ_LEND_RETAINED_ANDS' in hunks[0];assert all('HEO_PIN_SQ_LEND_RETAINED_ANDS'not in h for h in hunks[1:]);selected=(header+''.join(hunks[1:])).encode();(r/'public-rail-exact.patch').write_bytes(selected);subprocess.run(['git','-C',str(t),'apply','--check',str(r/'public-rail-exact.patch')],check=True);subprocess.run(['git','-C',str(t),'apply',str(r/'public-rail-exact.patch')],check=True)
provenance={}
for name in['strip_barrel.rs','strip_small.rs']:
 data=subprocess.check_output(['git','-C',str(repo),'show',new+':src/point_add/'+name]);(t/'src/point_add'/name).write_bytes(data);provenance[name]=hashlib.sha256(data).hexdigest()
read=lambda rev,name:subprocess.check_output(['git','-C',str(repo),'show',rev+':src/point_add/'+name]);old_y=read(base,'y15_onefold.rs');new_y=read(new,'y15_onefold.rs');start=b"        // x257's bit set: the chain now.";newstart=b"        // G6' (round-10 gate, own copy):";end=b'        c.free_bit(bitx);';a=old_y.index(start);z=old_y.index(end,a)+len(end);aa=new_y.index(newstart);zz=new_y.index(end,aa)+len(end);oldblock=old_y[a:z];newblock=new_y[aa:zz];p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();assert raw.count(oldblock)==1;raw=raw.replace(oldblock,b'        if std::env::var("EXACT_NATIVE_G6").is_ok_and(|v|v=="1"){\\n'+newblock+b'\\n        }else{\\n'+oldblock+b'\\n        }');p.write_bytes(raw);(r/'old-g6-body.rs').write_bytes(oldblock);(r/'new-g6-body.rs').write_bytes(newblock)
p=t/'src/point_add/mod.rs';raw=p.read_bytes();a=b'pub fn build() -> Vec<Op> {';assert raw.count(a)==1;raw=raw.replace(a,a+b'\\n    let mode=std::env::var("EXACT_NATIVE_PORT_MODE").expect("Declared exact native port case");assert!(["control","rail","g6","both"].contains(&mode.as_str()));');a=b'    let mut ops = build_point_add();';assert raw.count(a)==1;raw=raw.replace(a,b'    std::env::set_var("LF_STRIP",if mode=="rail"||mode=="both"{"1"}else{"0"});std::env::set_var("LF_R1",if mode=="rail"||mode=="both"{"1"}else{"0"});std::env::set_var("EXACT_NATIVE_G6",if mode=="g6"||mode=="both"{"1"}else{"0"});\\n'+a);a=b'    finished_square_pipeline::run(ops)';assert raw.count(a)==1;raw=raw.replace(a,b'    exact_native_port::run(ops)');raw+=b'\\nmod exact_native_port;\\n';p.write_bytes(raw)
runtime='''use crate::circuit::{Op,OperationType,QubitId};
pub(super)fn run(ops:Vec<Op>)->Vec<Op>{super::break_profile::save_ops("raw.ops.bin",&ops);let mut ops=super::breakthrough_generic::run(ops);for _ in 0..96{let mut o=Op::empty();o.kind=OperationType::X;o.q_target=QubitId(0);o.validate();ops.push(o);}ops}
''';(t/'src/point_add/exact_native_port.rs').write_text(runtime);p=t/'src/point_add/leapfrog.rs';p.write_bytes(p.read_bytes()+b'\\n'+(r/'rail-tests.rs').read_bytes());assert all(sha(t/p)==h for p,h in f['protected_files'].items());assert all(sha(t/'src/point_add'/n)==sha(old/'src/point_add'/n)for n in['finished_square_pipeline.rs','square_lease_cache.rs','square.rs','sqtop_pass.rs','census_anchored.rs']);subprocess.run(['cp','-a','--reflink=auto',str(old/'target'),str(t/'target')],check=True);subprocess.run(['git','-C',str(t),'add','--intent-to-add','src/point_add'],check=True);(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD','--','src/point_add']));(r/'SOURCE-FREEZE.json').write_text(json.dumps({'base':revision,'public_exact_components':new,'public_prior_base':base,'public_new_files':provenance,'source_files':{p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()},'protected_files':f['protected_files'],'modes':['control','rail','g6','both'],'identity_nonce':0,'baseline_raw_count':10543037,'baseline_raw_sha3':'18f7fc00af40daeda201761064a6ce33a6ac74da78054df3464bdce6a4f0bcb9','scope':'Only exact native rail and G6 body ports; no new approximations or bound table transport. Old finish/cache guards untouched, unused research. Each fixedmode frozen before generation, control must reproduce raw.'},indent=2)+'\\n')
""")
print(r)
