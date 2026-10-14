"""Copy a frozen qubit source into an external conditional phase-proof crate.

No candidate checkout or protected harness is changed. The two native reserve9
fixtures retain their exact value/inverse checks and gain all-outcome phase ANF.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
import shutil
import subprocess


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("source",type=Path)
    a.add_argument("library",type=Path)
    a.add_argument("destination",type=Path)
    args=a.parse_args();source,library,dest=map(lambda p:p.resolve(),[args.source,args.library,args.destination])
    tree=dest/"source/point_add";assert not tree.exists(),"frozen proof tree already exists"
    shutil.copytree(source/"src/point_add",tree)
    kernel=Path(__file__).with_name("phase_polynomial.rs").resolve()
    frozen_kernel=dest/"phase-audit-kernel.rs"
    frozen_kernel.write_bytes(kernel.read_bytes())
    width=692 if re.search(r'pub const N:\s*usize\s*=\s*275\s*;', (tree/'pointadd_frogdrop.rs').read_text()) else 693
    path=tree/"tests_midg_k24.rs";text=path.read_text()
    begin=text.index("fn symbolic(ops:")
    end=text.index("\nfn apply(",begin)
    replacement='#[path='+json.dumps(frozen_kernel.as_posix())+']\nmod conditional_phase_kernel;\n'
    replacement+='fn symbolic(ops: &[Op], q: Vec<u64>) -> (Vec<u64>,u64) {\n'
    replacement+='let proof=conditional_phase_kernel::audit(ops,&q,&[]).expect("Exact conditional phase/value proof; cap failure is inconclusive");\n'
    replacement+='eprintln!("CONDITIONAL_PHASE_PROOF ops={} input_lanes=64 measurement_variables={} maximum_phase_terms={} maximum_quantum_terms={} scope=all_measurement_outcomes_fixed_inputs",ops.len(),proof.measurements,proof.maximum_phase_terms,proof.maximum_quantum_terms);\n'
    replacement+='(proof.qubits,proof.measurements*64)\n}\n'
    text=text[:begin]+replacement+text[end:]
    text=text.replace("fn reserve9_columns_crossing_3713_positive_native", "fn coordinator_reserve9_columns_phase_proof")
    text=text.replace("fn reserve9_crossing_payload_3713_exact_shadow_native", "fn coordinator_reserve9_payload_phase_proof")
    text=text.replace("fn cap24_counterexample8048_exact_column_payload_native", "fn coordinator_cap24_8048_payload_phase_proof")
    text=text.replace("fn cap24_sc_sw_preposition_boundary_inverse_dirty_phase", "fn coordinator_cap24_preposition_phase_proof")
    text=text.replace("fn ph_owner_structured_q22_one_column_payload_native", "fn coordinator_ph_structured_payload_phase_proof")
    text=text.replace("fn ph_owner_two_qbits_preposition_inverse_dirty_phase", "fn coordinator_ph_preposition_phase_proof")
    text=text.replace("fn n275_sz_donor_boundaries_inverse_phase", "fn coordinator_n275_donor_phase_proof")
    text=text.replace("fn n275_k32_k24_partition_all_sy_words", "fn coordinator_n275_partition_phase_proof")
    text=text.replace("    n275_k32_k24_partition_all_sy_words();", "    coordinator_n275_partition_phase_proof();")
    text=text.replace("fn n275_v2_full_column_new_boundaries_native", "fn coordinator_n275_new_columns_phase_proof")
    needle=f'let back=run(&inverse,{width},&|words|*words=got.q.clone());'
    insert='let (fq,_)=symbolic(&forward,input.clone());assert_eq!(fq,expected);let(iq,_)=symbolic(&inverse,got.q.clone());assert_eq!(iq,input);'
    chunks=text.split("\n#[test]");changed=[]
    for i,chunk in enumerate(chunks):
        if re.search(r"fn coordinator_(?:reserve9|cap24|ph|n275)",chunk) and needle in chunk:
            assert chunk.count(needle)==1
            chunks[i]=chunk.replace(needle,insert+needle)
            changed.append(re.search(r"fn (coordinator_\w+)",chunk)[1])
    assert 2<=len(changed)<=8,changed
    text="\n#[test]".join(chunks)
    path.write_text(text,encoding="utf-8")
    (dest/"src").mkdir(parents=True,exist_ok=True)
    builder_source=(library/"src/bin/build_circuit.rs").read_text()
    serializer=builder_source[builder_source.index('const MAGIC:'):builder_source.index('\nfn main()')]
    main='use quantum_ecc::{circuit,sim,weierstrass_elliptic_curve};\nuse circuit::Op;\nuse std::fs::{self,File};\nuse std::io::{BufWriter,Write};\nuse std::path::Path;\n#[allow(dead_code)]\n#[path='+json.dumps((tree/"mod.rs").as_posix())+']\nmod point_add;\n'+serializer+'\nfn main(){println!("Source-bound conditional phase proof; not a scorer");}\n'
    (dest/"src/main.rs").write_text(main,encoding="utf-8")
    (dest/"Cargo.toml").write_text('[package]\nname="qubit_conditional_phase_proof"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nquantum_ecc={path='+json.dumps(library.as_posix())+'}\nalloy-primitives="1.5"\nruint="1.12"\nsha3="0.10"\nzstd="0.13"\n',encoding="utf-8")
    (dest/"rust-toolchain").write_bytes((library/"rust-toolchain").read_bytes())
    hashes={p.relative_to(source/'src/point_add').as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((source/'src/point_add').rglob('*')) if p.is_file()}
    (dest/'complete-source-binding.json').write_text(json.dumps({'revision':subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip(),'point_add_patch_sha256':hashlib.sha256(subprocess.check_output(['git','-C',str(source),'diff','HEAD','--','src/point_add'])).hexdigest(),'source_sha256':hashes,'component_constructor_width':width,'frozen_kernel_sha256':hashlib.sha256(frozen_kernel.read_bytes()).hexdigest()},indent=2)+'\n',encoding='utf-8')
    (dest/"provenance.json").write_text(json.dumps({'source':source.as_posix(),'source_sha256':hashes,'kernel_sha256':hashlib.sha256(kernel.read_bytes()).hexdigest(),'research_test_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'public_builder_serializer_source_sha256':hashlib.sha256((library/"src/bin/build_circuit.rs").read_bytes()).hexdigest(),'added_phase_calls':changed,'scope':'13 no-payload columns plus modeled payload inputs for3713 and optionally8048. Exact Boolean ANF for all independent R/HMR outcomes; finite admitted INPUT domain only. No score or full-circuit qualification.'},indent=2)+'\n',encoding="utf-8")


if __name__=="__main__":main()
