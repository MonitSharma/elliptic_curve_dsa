"""Independently recount the complete final census, without running a circuit."""
import hashlib
import json
from pathlib import Path

root = Path('/home/hclau/ecdsa_research/product25-final-20261016')
assert (root / 'final-census.exit').read_text().strip() in ('0', '1')
reported = json.loads((root / 'FINAL_CENSUS_RESULT.json').read_text())
binding = json.loads((root / 'FINAL_CENSUS_BINDING.json').read_text())
cohorts, rows, hashes = {}, {}, {}
for role in ('parent', 'candidate'):
    path = root / 'final-fresh' / (role + '.jsonl')
    raw = path.read_bytes()
    assert raw.endswith(b'\n')
    hashes[role] = hashlib.sha256(raw).hexdigest()
    batches = [json.loads(line) for line in raw.splitlines()]
    assert len(batches) == 32768
    assert sorted(row['batch'] for row in batches) == list(range(32768))
    rows[role] = {row['batch']: row for row in batches}
    for row in batches:
        assert row['shots'] == 64
        assert isinstance(row['toffoli'], int) and row['toffoli'] >= 0
        lanes = [failure['lane'] for failure in row['failures']]
        assert len(set(lanes)) == len(lanes)
        assert all(0 <= lane < 64 for lane in lanes)
        for kind in ('value', 'phase', 'dirty'):
            assert sum(bool(failure[kind]) for failure in row['failures']) == row[kind + '_shots']
    failed = sum(bool(row['failures']) for row in batches)
    cohorts[role] = dict(batches=len(batches), shots=64*len(batches), failed_batches=failed,
                         failed_shots=sum(len(row['failures']) for row in batches),
                         lambda_failed_batches_per9024=141*failed/32768,
                         toffoli_total=sum(row['toffoli'] for row in batches),
                         **{kind + '_shots': sum(row[kind + '_shots'] for row in batches)
                            for kind in ('value', 'phase', 'dirty')})
    for key, value in cohorts[role].items():
        assert reported['cohorts'][role][key] == value, (role, key)
    assert hashes[role] == reported['raw_row_sha256'][role]
for batch in range(32768):
    parent, candidate = rows['parent'][batch], rows['candidate'][batch]
    assert parent['skipped'] == candidate['skipped']
    p = {failure['lane']: failure for failure in parent['failures']}
    c = {failure['lane']: failure for failure in candidate['failures']}
    for lane in p.keys() & c.keys():
        assert (p[lane]['k1'], p[lane]['k2']) == (c[lane]['k1'], c[lane]['k2'])
passed = (cohorts['candidate']['failed_batches'] <= cohorts['parent']['failed_batches']
          and cohorts['candidate']['lambda_failed_batches_per9024'] <= 18
          and cohorts['candidate']['dirty_shots'] == 0)
assert passed == reported['failure_gate_pass']
assert binding['source_sha256'] == reported['source_sha256']
result = dict(status='INDEPENDENT_COMPLETE_RAW_RECOUNT_AGREES', failure_gate_pass=passed,
              cohorts=cohorts, raw_row_sha256=hashes, all_65536_rows_recounted=True,
              final_result_sha256=hashlib.sha256((root / 'FINAL_CENSUS_RESULT.json').read_bytes()).hexdigest(),
              no_circuit_execution_or_resampling=True)
target = root / 'FINAL_CENSUS_INDEPENDENT_RECOUNT.json'
assert not target.exists()
target.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
