"""Parse source-bound, gate-inert fold snapshots without inferring absent calls."""
import ast, hashlib, json, re, sys
from pathlib import Path

def value(s):
    return ast.literal_eval(s.replace('false', 'False').replace('true', 'True'))

path, output = map(Path, sys.argv[1:3])
rows = []
current = None
for line in path.read_text().splitlines():
    if line.startswith('PRODUCT_FOLD_ENTRY '):
        m = re.fullmatch(r'PRODUCT_FOLD_ENTRY payload=(None|Some\(\((false|true), (\d+)\)\)) fin=(\d+) ttm=(false|true) drop=(\d+) op=(\d+) acc=(\[.*?\]) e=(\[.*?\]) nm=(\[.*?\]) k=(\[.*?\]) state=(\(.*\)) dims=(\(.*\))', line)
        assert m, line
        assert current is None, 'missing preceding exit'
        current = {'payload': None if m[1] == 'None' else [m[2] == 'true', int(m[3])], 'fin': int(m[4]), 'ttm': m[5] == 'true', 'drop': int(m[6]), 'entry_op': int(m[7]), 'acc': value(m[8]), 'e': value(m[9]), 'nm': value(m[10]), 'k': value(m[11]), 'entry_state': value(m[12]), 'entry_dims': value(m[13])}
    elif line.startswith('PRODUCT_FOLD_EXIT '):
        m = re.fullmatch(r'PRODUCT_FOLD_EXIT payload=(None|Some\(\((false|true), (\d+)\)\)) fin=(\d+) ttm=(false|true) drop=(\d+) start=(\d+) op=(\d+) plan=(\[.*?\]) state=(\(.*\)) dims=(\(.*\))', line)
        assert m and current, line
        assert current['entry_op'] == int(m[7])
        current.update(exit_op=int(m[8]), plan=value(m[9]), exit_state=value(m[10]), exit_dims=value(m[11]))
        current['emitted_ops'] = current['exit_op'] - current['entry_op']
        current['extra_guard'] = current['payload'] is not None and not current['payload'][0] and current['fin'] == 0 and not current['ttm'] and current['drop'] == 0
        rows.append(current)
        current = None
assert current is None, 'last entry has no exit'
doc = {'scope': 'physical fold contexts and exact allocator vectors; no score', 'trace_log_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'calls': len(rows), 'admitted_early': sum(r['extra_guard'] for r in rows), 'rows': rows}
output.write_text(json.dumps(doc, indent=2)+'\n', newline='\n')
print(json.dumps({k: v for k,v in doc.items() if k != 'rows'}))
