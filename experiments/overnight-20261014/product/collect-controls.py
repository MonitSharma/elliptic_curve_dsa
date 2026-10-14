"""Compact receipts for completed exact-control research, never scored results."""
from pathlib import Path
import hashlib,json,re
root=Path(__file__).resolve().parents[3];raw=root/'research-output/overnight-20261014/product'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def source(name):
    p=raw/(name+'-source.sha256')
    return {line.split()[1]:line.split()[0] for line in p.read_text().splitlines()}
def result(name,status,counts):
    p=raw/(name+'.log')
    return dict(status=status,log_sha256=digest(p),source_sha256=source(name),**counts)
data=dict(baseline_revision='c5bb1ec876db859a3f9f8a9052c140a145df834e',baseline_stream_sha256='49b35cf7640ebd529d76894eb8bef93ebf57e7e970fe14b3c27c8c5feb6e73e4',evidence_kind='research_diagnostics',qualified_score=None,official_builder_binding='Pending: clean candidate patch is preserved; current stream came from external source-bound postpass.',nonce_policy='No nonce search or packet selection; inherited nonce unchanged.',positive=result('classical-positive','completed_diagnostic',dict(exit_status=0,native_suites_passed=2,emitted_ccx_before=813269,emitted_ccx_after=813265,depth_proxy_saving=4)),fresh_complement_prototype=result('classical-factors-failed','failed_component_tests',dict(exit_status=101,native_suites_passed=1,native_suites_failed=2,failure='New private classical helper remained nonzero in full-state checks. No full stream generated.')),xor_factors=result('classical-xor-factors','completed_diagnostic',dict(exit_status=0,native_suites_passed=3,emitted_ccx_before=813269,emitted_ccx_after=813261,native_rewrites=8,complement_rewrites=4,depth_proxy_saving=6.5,stream_sha256='b026a2d0c7e346158e665dada830d636a010ca93097a1f60b3daa87219b6505a',added_qubits=0,added_bits=0,added_measurements=0)))
p=raw/'classical-xor-paired.log';t=p.read_text()
data['paired']=dict(exit_status=0,log_sha256=digest(p),input_and_runner_sha256={line.split()[1]:line.split()[0] for line in (raw/'classical-xor-paired-inputs.sha256').read_text().splitlines()},results=[])
for line in t.splitlines():
    if not line.startswith('DIAGNOSTIC_ONLY'):continue
    fields={k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',line)};data['paired']['results'].append(fields)
data['paired']['scope']='All final original quantum/classical slots and phase agree. First9024 baseline point packet uses a common independent measurement transcript, with one inherited phase-garbage batch on both streams. No official score.'
data['negative_analyses']=dict(anf8=dict(log_sha256=digest(raw/'anf8.log'),saving=0),commuting_pairs=dict(log_sha256=digest(raw/'commute-fixed.log'),saving=0),peak_and_phase=dict(log_sha256=digest(raw/'peak-phase.log'),exact_known_zero_at_peak=[1233],pscan_generic_phase_counterexample='All-one input changes phase1->0 while q/b values agree;9ops->6ops. This guards against applying parity rewrites without proving the phase premise.'))
Path(__file__).with_name('controls-receipt.json').write_text(json.dumps(data,indent=2)+'\n',newline='\n')
