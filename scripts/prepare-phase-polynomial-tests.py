"""Build an external native test crate for the exact phase audit kernel."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("library",type=Path)
    a.add_argument("destination",type=Path)
    args=a.parse_args();base,dest=args.library.resolve(),args.destination.resolve()
    (dest/"src").mkdir(parents=True,exist_ok=True)
    source=Path(__file__).with_name("phase_polynomial.rs").read_bytes()
    (dest/"src/phase_polynomial.rs").write_bytes(source)
    (dest/"src/main.rs").write_text('pub mod circuit {pub use quantum_ecc::circuit::*;}\nmod phase_polynomial;\nfn main(){println!("Independent conditional Boolean phase kernel; not a scorer");}\n',encoding="utf-8")
    (dest/"Cargo.toml").write_text('[package]\nname="conditional_phase_kernel"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nquantum_ecc={path='+json.dumps(str(base))+'}\nsha3="0.10"\n',encoding="utf-8")
    (dest/"rust-toolchain").write_bytes((base/"rust-toolchain").read_bytes())
    (dest/"provenance.json").write_text(json.dumps({'kernel_sha256':hashlib.sha256(source).hexdigest(),'library':str(base),'scope':'Finite input-domain, all-measurement-outcome exact Boolean-ring audit. Support limits are inconclusive. No candidate or score.'},indent=2)+'\n',encoding="utf-8")


if __name__=="__main__":main()
