"""Collect a terminal frozen qubit benchmark; never launch or repeat evaluation.

Run on smu_server from the preserved cycle. The receipt combines the candidate
source binding with the separately compiled, protected evaluator binding.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

ROOT=Path('/home/hclau/ecdsa_research/overnight-20261014')
def digest(path):
    h=hashlib.sha256()
    with path.open('rb')as file:
        while chunk:=file.read(8*1024*1024):h.update(chunk)
    return h.hexdigest()

def collect(variant):
    qroot=ROOT/'qubits';e=qroot/'evidence'
    definitions={
        'n275-v2':('candidate-n275-v2-manifest.json','n275-v2-protected-harness-manifest.json','ad1205994a3927ba76e90a086eadcf800d5876efe36425495cc8e83e21c6a26f','892c6c0c8ab7546dcee4fb08deb8146d4ca250b8ea941d02ce9bc43711ccb4dc'),
        'headflag-v1':('candidate-headflag-v1-manifest.json','headflag-v1-protected-harness-manifest.json','6b0046e2470cabf150fa6d2892e0b8206a683d3975b5d268cd7b80ed2cfdc902','8333555d82603e07c735e56db12cf8ce9c6355c92f2afa2ce7670ec3b8578a18')}
    candidate_name,harness_name,stream_sha,binary_sha=definitions[variant]
    terminal=e/(variant+'-official-eval.exit')
    if not terminal.exists():
        print(json.dumps({'status':'pending','variant':variant,'required_terminal_marker':str(terminal)}))
        return
    native=e/(variant+'-official-eval-native.exit')
    assert terminal.read_text().strip()==native.read_text().strip(),'wrapper/native exit mismatch'
    candidate=json.loads((e/candidate_name).read_text());harness=json.loads((e/harness_name).read_text())
    source=Path(candidate['checkout']);trusted=Path(harness['checkout'])
    assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()==candidate['base_revision']
    patch=subprocess.check_output(['git','-C',str(source),'diff','HEAD','--','src/point_add/'])
    assert hashlib.sha256(patch).hexdigest()==candidate['patch_sha256']
    for path,sha in candidate['source_sha256'].items():assert digest(source/path)==sha,path
    changed=subprocess.check_output(['git','-C',str(source),'diff','HEAD','--name-only'],text=True).splitlines()
    assert sorted(changed)==sorted(candidate['candidate_changed_paths'])
    assert all(path.startswith('src/point_add/')for path in changed)
    assert subprocess.check_output(['git','-C',str(trusted),'rev-parse','HEAD'],text=True).strip()==harness['base_revision']==candidate['base_revision']
    for path,sha in harness['protected_source_sha256'].items():assert digest(trusted/path)==sha,path
    assert harness.get('protected_binary_sha256',binary_sha)==binary_sha
    assert digest(trusted/'target/release/eval_circuit')==binary_sha
    stream=e/(variant+'-ops.bin');assert digest(stream)==stream_sha
    assert (trusted/'ops.bin').is_symlink()and(trusted/'ops.bin').resolve()==stream.resolve()
    spec=importlib.util.spec_from_file_location('receipt',ROOT/'research-receipt.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    output=ROOT/('coordinator-'+variant+'-terminal')
    receipt=module.collect(source,output,e/(variant+'-official-eval.log'),terminal,stream,
                           e/(variant+'-official-score.json'),True)
    receipt['frozen_candidate_manifest']=candidate
    receipt['protected_harness_manifest']=harness
    receipt['protected_binary_sha256']=binary_sha
    receipt['native_exit_marker']=str(native)
    receipt['classification']='original_candidate_finite_official_benchmark'
    receipt['placeholder_used']=False
    receipt['collection_command']='python3 collect-overnight-qubit-result.py '+variant
    # Diagnostic counts are retained only in the full log/results artifacts.
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    print(json.dumps({key:receipt[key]for key in('status','candidate_patch_sha256','qualified_score','failure_counts')},indent=2))

if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('variant',choices=['n275-v2','headflag-v1'])
    collect(a.parse_args().variant)
