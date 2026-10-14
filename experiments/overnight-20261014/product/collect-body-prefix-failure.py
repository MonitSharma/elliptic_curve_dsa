"""Preserve failed mapping verification; no arithmetic result was produced."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[3]
raw=root/'research-output/overnight-20261014/product/body-prefix-replay-v1'
out=root/'experiments/overnight-20261014/product'
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in raw.iterdir() if p.is_file()}
receipt=dict(status='FAILED_VERIFICATION_ASSERTION',exit=101,qualified_score=None,arithmetic_points_evaluated=0,
 server_evidence='/home/hclau/ecdsa_research/overnight-20261014/product-evidence/body-prefix-replay',local_artifact_hashes=hashes,
 native=(raw/'native.sha256').read_text().strip(),source_hashes=(raw/'source.sha256').read_text(),
 failure='Emission divide-seamed prefix SHA3 differs from same-index prefix after Builder.y33_clears retroactive measurement/reset movement.',
 expected_sha3='254f312f8344b5c6f0e19f625aa6f4e560a12639989f67bd7fa7aea10d767a97',actual_sha3='490cbf505dcfc26f1eb5a0fb01eed8c29075186385987531afc00d2718f8ea3c',
 interpretation='No scalar, coordinate or phase diagnostics from this run are admissible. Replaced by separately versioned exact Y33 map/overlay validation, without weakening the hash guard.')
(out/'body-prefix-v1-failed-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',newline='\n')
(out/'body-prefix-v1-failure.md').write_text('''# Failed first body-boundary mapping

The source-attested native replay exited 101 before evaluating any points. Its emission-time `divide-seamed` prefix hash did not equal the same-index prefix of the finalized raw circuit. The first coordinate-subtraction boundary matched.

Source audit identifies `Builder.y33_clears()` before `finalize_records()` as the retroactive operation mutation. It replaces a run's first write with HMR plus a phase twin, rewrites later writes as phase twins and removes the eventual reset. A pending run shifts prefix operation indices and makes its physical target zero before its original logical release. Whole-body length is unchanged. `finalize_records()` changes no operations, as its before/after hashes independently show.

This is a failed verification assumption, not an arithmetic counterexample. No old arithmetic flag or phase is interpreted. V2 preserves the failed source/binary/log and adds both pre-cleanup and final hash domains, exact copied-source whole-vector transformation equality, exact event boundary remapping and logical pending-target reconstruction.

No qualified score. The protected circuit, simulator, scorer and reference remain unchanged.
''',newline='\n')
for name in ['receipt.json','candidate.patch']:
 p=root/'research-output/overnight-20261014/product/b3-body-boundaries-v1/receipt'/name
 (out/('b3-body-boundaries-v1-'+name)).write_bytes(p.read_bytes())
