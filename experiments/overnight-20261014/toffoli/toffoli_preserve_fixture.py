"""Preserve the isolated native research fixture as a reapplicable permitted patch."""
import difflib
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).parent
local=ROOT/"research-output/overnight-20261014/toffoli/source/src/point_add"
base=subprocess.run(["git","-C",str(ROOT/"agents/product"),"show","c5bb1ec876db859a3f9f8a9052c140a145df834e:src/point_add/y15_onefold.rs"],check=True,capture_output=True).stdout
candidate=local.joinpath("y15_onefold.rs").read_bytes().replace(b"\r\n",b"\n")
fixture=HERE.joinpath("toffoli_native_fold.rs").read_bytes().replace(b"\r\n",b"\n")
parts=list(difflib.unified_diff(base.decode().splitlines(keepends=True),candidate.decode().splitlines(keepends=True),fromfile="a/src/point_add/y15_onefold.rs",tofile="b/src/point_add/y15_onefold.rs"))
parts += list(difflib.unified_diff([],fixture.decode().splitlines(keepends=True),fromfile="/dev/null",tofile="b/src/point_add/toffoli_native_fold.rs"))
patch="".join(parts).encode()
HERE.joinpath("native-fixture.patch").write_bytes(patch)
manifest={"base_revision":"c5bb1ec876db859a3f9f8a9052c140a145df834e",
          "qualification":"Baseline component verification only; no production arithmetic change, no original full-circuit improvement or score.",
          "patch_sha256":hashlib.sha256(patch).hexdigest(),
          "source_lf_sha256":{"src/point_add/y15_onefold.rs":hashlib.sha256(candidate).hexdigest(),
                              "src/point_add/toffoli_native_fold.rs":hashlib.sha256(fixture).hexdigest()},
          "apply_to":"Clean base only; all added source remains under src/point_add/; protected harness untouched.",
          "command":"CARGO_BUILD_JOBS=4 cargo test --offline --locked --release --bin build_circuit toffoli_native_fold -- --nocapture --test-threads=1",
          "scope":"Width56 fin0: all16384 low input states,38 high words, zero plus79 independent measurement coefficients. Width57fin1 and56fin2: same values,4 phase words each. Arbitrary high-word coverage is not established."}
HERE.joinpath("native-fixture-manifest.json").write_bytes((json.dumps(manifest,indent=2)+"\n").encode())
print(json.dumps(manifest,indent=2))
