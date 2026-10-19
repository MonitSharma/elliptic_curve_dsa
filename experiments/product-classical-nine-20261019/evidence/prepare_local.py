from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent
for name in ['io.rs','factor_trace.rs']:
    (r/name).write_bytes((ws/'product-classical-factors-refresh-20261019'/name).read_bytes())
p=r/'factor_trace.rs';s=p.read_text();s=s.replace('classical-factor-control-','classical-nine-control-').replace('assert!(y.3<=x.3,"executed Toffolis cannot increase");','assert_eq!(x.3-y.3,64,"exactly one executed Toffoli removed per shot");');p.write_text(s)
text='''[package]
name="classical_nine_research"
version="0.1.0"
edition="2021"
[dependencies]
quantum_ecc={path="/home/hclau/ecdsa_research/overnight-20261014/product-b3-baseline"}
sha3="0.10"
serde_json="1"
zstd="0.13"
[[bin]]
name="classical_nine_research"
path="research.rs"
[[bin]]
name="classical_nine_trace"
path="factor_trace.rs"
[profile.release]
opt-level=3
''';(r/'Cargo.toml').write_text(text)
s=(ws/'autonomous-20261019/preflight_v5.py').read_text()
s=s.replace('workers={int(', 'own_ancestors=set(allowed)\nworkers={int(')
s=s.replace(" ('product-classical-type-probe-20261019','run.pid',1),", " ('product-classical-type-probe-20261019','run.pid',1),\n ('product-classical-control-expression-20261019','run.pid',1),\n ('product-classical-nine-20261019','run.pid',1),\n ('product-classical-nine-20261019','gate.pid',3),")
s=s.replace("'final.pid':b'run-final.sh'", "'final.pid':b'run-final.sh','gate.pid':b'run-gate.sh'")
s=s.replace('if p not in descendants(os.getpid()) and p!=os.getpid():extra_slots+=slots','if p not in own_ancestors:extra_slots+=slots')
(ws/'autonomous-20261019/preflight_v6.py').write_text(s)
s=(ws/'product-classical-factors-native-20261019/prepare_native.py').read_text()
s=s.replace("assert json.loads((f/'CONTROL-parent4.json').read_text())", "assert (r/'control.exit').read_text().strip()=='0'\nassert json.loads((f/'CONTROL-parent4.json').read_text())")
s=s.replace("expected=json.loads((f/'parent4.json').read_text());assert expected['output_full_sha3_256']=='f64a9d8c59cdc89e9b683988da84eb34fa78c5a884f0324ce824e4c07a00fa53'", "expected=json.loads((r/'RESEARCH.json').read_text());assert expected['output_count']==17889627\nassert json.loads((r/'CONTROL-nine.json').read_text())['saved_executed_Toffolis_total_on_512_control_shots']==512")
s=s.replace("mod=point/'mod.rs'", "shutil.copy2(r/'classical_xor_control.rs',point/'classical_xor_control.rs')\nmod=point/'mod.rs'")
s=s.replace("ops = classical_factors_xor::simplify_classical(ops);\\n", "ops = classical_factors_xor::simplify_classical(ops);\\n    ops = classical_xor_control::run(ops);\\n")
s=s.replace("mod classical_factors_xor;\\n", "mod classical_factors_xor;\\nmod classical_xor_control;\\n")
(r/'prepare_native.py').write_text(s)
(r/'verify_native.py').write_bytes((ws/'product-classical-factors-native-20261019/verify_native.py').read_bytes())
(r/'launch.py').write_bytes((ws/'product-classical-control-expression-20261019/launch.py').read_bytes().replace(b'exact-classical-control-expression-probe',b'classical-nine-native-and-control'))
(r/'refresh_record.py').write_bytes((ws/'autonomous-20261019/refresh_record.py').read_bytes())
