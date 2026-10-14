"""Collect compact terminal receipts while keeping bulk logs outside Git."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).parent
RAW=ROOT/"research-output/overnight-20261014/toffoli"
def hashed(path):return hashlib.sha256(path.read_bytes()).hexdigest()
manifest=json.loads(HERE.joinpath("native-fixture-manifest.json").read_text())
log=RAW/"toffoli-native-fold-v4-20261014.log"
text=log.read_text()
native={"status":"passing_baseline_component_fixture","tests_passed":2,"tests_failed":0,
        "command":manifest["command"],"source":manifest,
        "host":"LHC-104-070","server_directory":"/home/hclau/ecdsa_research/overnight-20261014/toffoli",
        "job_pid":2337904,"exit_status":0,"log_sha256":hashed(log),
        "server_log":"/home/hclau/ecdsa_research/overnight-20261014/toffoli/toffoli-native-fold-v4-20261014.log",
        "settings_sha256":hashed(RAW/"toffoli-native-fold-v4-20261014.settings"),
        "memory_limit_KiB":16777216,"build_threads":4,"runtime_threads":1,
        "peak_RSS_KiB":int(re.search(r"Maximum resident set size \(kbytes\):\s*(\d+)",text)[1]),
        "elapsed":re.search(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\):\s*(\S+)",text)[1],
        "fixtures":[{"width":56,"fin":0,"raw_low_inputs":16384,"high_words":38,"measurement_basis_coefficients":79,"zero_outcome_word":True,"simulated_cases":49807360},
                    {"width":57,"fin":1,"raw_low_inputs":16384,"high_words":38,"phase_words":4,"simulated_cases":2490368},
                    {"width":56,"fin":2,"raw_low_inputs":16384,"high_words":38,"phase_words":4,"simulated_cases":2490368}],
        "negative_control":"Removed final low-carry CZ repair; phase garbage detected.",
        "phase_scope":"Fin0 structurally excludes measurement-conditioned value operations, nested measurement conditions and combined direct/stack conditions. Phase is linear in measurements; zero and all79 coefficient checks cover all outcome words for the38 selected high words. Fin1/2 cover4 words only.",
        "limits":"No arbitrary high-word proof, no full point-addition validation, no original circuit change or score."}
joint=json.loads(HERE.joinpath("toffoli-joint-thirty-and-20261014.json").read_text())
result={"qualification":"No original submission-ready candidate. Baseline component tests and synthesis/negative research only.",
        "native_fixture":native,
        "complete_constructor_obstruction":json.loads(HERE.joinpath("closed-subspace-certificate.json").read_text()),
        "failed_or_superseded":[
            {"experiment":"Initial native fixture","status":"Positive fixtures passed; unexercised top-CZ negative control did not detect fault","exit_status":101,"log_sha256":hashed(RAW/"toffoli-native-fold-20261014.log"),"preserved_source":"toffoli_native_fold_fault_v1.rs"},
            {"experiment":"v2 launcher","status":"Failed before tests due to CRLF shell script","log_sha256":hashed(RAW/"toffoli-native-fold-v2-20261014.log"),"preserved_source":"toffoli_native_failed_crlf_v2.sh"},
            {"experiment":"4AND SAT cut","status":"canceled_superseded_by_exhaustive_closure","signal":"SIGTERM","exit_status":143,"job_pid":2315250,"solver_pid":2315296,"log_sha256":hashed(RAW/"toffoli-cut0-four-and-20261014.log"),"limits":"Cancellation is not an UNSAT result."}],
        "sparse_thirty_AND_search":{"status":joint["status"],"planes":len(joint["planes"]),"pairs_checked":sum(x["pairs_checked"] for x in joint["planes"]),"seconds":joint["seconds"],"limits":joint["limits"],"receipt_sha256":hashed(HERE/"toffoli-joint-thirty-and-20261014.json")}}
HERE.joinpath("first-checkpoint-receipt.json").write_bytes((json.dumps(result,indent=2)+"\n").encode())
print(json.dumps({"native_status":native["status"],"constructor_bound":26,"original_candidates":0,"sparse_pair_checks":result["sparse_thirty_AND_search"]["pairs_checked"]},indent=2))
