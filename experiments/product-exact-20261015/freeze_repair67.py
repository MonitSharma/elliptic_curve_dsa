"""Freeze only the declared corrected-source67 endpoint after its512 replay."""
import copy,hashlib,json,re,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'repair-to67-rank-20261016';assert (d/'launcher.exit').read_text().strip()=='0'
plan=json.loads((d/'DECLARATION.json').read_text());base=json.loads((r/plan['source_freeze']).read_text());target=r/'REPAIR67_FREEZE.json';assert not target.exists();spec=plan['stages'][-1]
path=d/f"repair-67-{spec['family']}-{spec['atom_cap']}-{spec['rank']}.bin";packets={}
for packet in ['independent','structured']:
    line=next(x for x in (d/f'stage-67-{packet}.log').read_text().splitlines() if x.startswith('DIAGNOSTIC_ONLY '));row=dict(re.findall(r'(\w+)=([^ ]+)',line));assert row['unequal_batches']=='0';packets[packet]=row
prefix=subprocess.check_output(['python3',str(r/'stream_prefix_manifest.py'),str(path)],text=True);(r/'repair67-prefix-manifest.jsonl').write_text(prefix)
row={k:copy.deepcopy(base[k]) for k in ['base_revision','repair_parent_stream','repair_parent_sha256','repair_source_snapshot','repair_source_manifest','repair_parent_prefix_manifest']}
row.update(stages=copy.deepcopy(plan['stages']),external_stream=str(path.relative_to(r)),external_stream_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),resources=json.loads((d/'stage-67-resources.jsonl').read_text()),prefix_manifest=json.loads(prefix),packets=packets,native_source_port='pending',fresh_failure_census_vs_original4b='pending; sole final32768 plan in declaration',nonce_search_performed=False,score=None,declaration=str((d/'DECLARATION.json').relative_to(r)),chain_manifest=str((d/'stage-67.manifest').relative_to(r)),scope='Fixed corrected-source67 endpoint; all512 original-A29-versus-final quantum/classical/phase/scratch comparisons pass. All14 added stages were fixed before metrics, no packet-selected stop. Source and class IDs are u64, exact census uses u32; an obsolete16-bit limit does not reject or truncate this source.')
assert row['resources']['qubits']==1234;target.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)
