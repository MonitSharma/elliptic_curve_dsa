"""External audit of the public qubit source's full schedule failure model."""
import argparse
import hashlib
import json
from pathlib import Path

MAIN = r'''
use quantum_ecc::{circuit,sim,weierstrass_elliptic_curve};
#[allow(dead_code)]
#[path="SOURCE_PATH/src/point_add/mod.rs"]
mod point_add;
use point_add::{frogdrop_sched as f,pointadd_frogdrop as pa,midg};
fn zstd_level()->i32 {3}
fn main(){
    let args:Vec<String>=std::env::args().collect();assert_eq!(args.len(),2);
    let packet=std::fs::read_to_string(&args[1]).unwrap();
    let sc=f::from_text(pa::SCHED_FROGDROP);
    let pp=f::p();let mut divisions=0usize;let mut failures=0usize;
    for line in packet.lines().filter(|l|!l.starts_with('#') && !l.trim().is_empty()){
        let w:Vec<&str>=line.split_whitespace().collect();
        let shot:usize=w[0].parse().unwrap();
        let parse=|i:usize|f::N::from_str_radix(w[i].trim_start_matches("0x"),16).unwrap();
        let (tx,ox,ex)=(parse(1),parse(3),parse(5));
        for (d,v) in [(1,tx),(2,ex)]{
            let dx=if v>=ox{v-ox}else{pp-(ox-v)};
            let s=f::shot(dx,f::L0);
            let envelope=f::check(&s,&sc);
            let predict=f::predict_n_geometry(dx,&sc,24,pa::KP,pa::QB,pa::TOT,pa::NQ,pa::EMAX,pa::N,midg::park_reserve(),2);
            divisions+=1;
            if envelope.is_some() || predict.is_some(){
                failures+=1;
                println!("SCHEDULE_FAILURE shot={shot} division={d} input={dx:x} envelope={envelope:?} full_model={predict:?}");
            }
            if shot==3713 {println!("SIXTH_DETAILS division={d} columns={} bt1={} bt2={} br={} full_model={predict:?}",s.recs.len(),s.bt1,s.bt2,s.br);}
        }
    }
    println!("SCHEDULE_AUDIT divisions={divisions} flagged_divisions={failures} source_model_only=true scorer=NONE");
}
'''


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("baseline",type=Path)
    a.add_argument("destination",type=Path)
    args=a.parse_args()
    base,dest=args.baseline.resolve(),args.destination.resolve()
    (dest/"src").mkdir(parents=True,exist_ok=True)
    (dest/"src/main.rs").write_text(MAIN.replace("SOURCE_PATH",base.as_posix()),encoding="utf-8")
    (dest/"Cargo.toml").write_text('[package]\nname="public_schedule_audit"\nversion="0.1.0"\nedition="2021"\n\n[dependencies]\nquantum_ecc={path='+json.dumps(str(base))+'}\nalloy-primitives="1.5"\nruint="1.12"\nsha3="0.10"\nzstd="0.13"\n',encoding="utf-8")
    (dest/"rust-toolchain").write_bytes((base/"rust-toolchain").read_bytes())
    source_hashes={name:hashlib.sha256((base/"src/point_add"/name).read_bytes()).hexdigest() for name in ["frogdrop_sched.rs","sched_frogdrop.txt","pointadd_frogdrop.rs","midg.rs"]}
    (dest/"provenance.json").write_text(json.dumps({"baseline":str(base),"source_sha256":source_hashes,"scope":"Public full failure model, including schedule envelopes; excludes unmodeled carry truncation and all quantum/phase behavior."},indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":main()
