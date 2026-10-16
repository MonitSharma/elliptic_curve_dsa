from pathlib import Path
import hashlib,json,tarfile,io
r=Path(__file__).resolve().parent;h=lambda b:hashlib.sha256(b).hexdigest()
assert(r/'evidence/mask-lazy-analysis-v1.exit').read_text().strip()=='0'
assert(r/'evidence/mask-lazy-analysis-v1-before.sha256').read_bytes()==(r/'evidence/mask-lazy-analysis-v1-after.sha256').read_bytes()
x=json.load(open(r/'evidence/mask-lazy-analysis-v1.json'));packed=[v for v in x['records']if v['mode']=='packed32'];scalar=[v for v in x['records']if v['mode']!='packed32'];assert len(packed)==2 and len(scalar)==16
text=f'''# Bounded lazy mask analysis: negative

Frozen original v3 maskSHA560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d remains unchanged. This source-only analysis uses its existing validated independent C evaluator as an immutable oracle for node values on the32 preserved audit inputs. It counts exact fixed-child-order memoized demand traversal, applying AND(first,second)=0 whenfirst=0 and OR(first,second)=1 whenfirst=1. It does not build or validate a new lazy runtime and its Python traversal timings are not runtime speedup evidence.

The audit has{x['known_bits']} known coordinate bits among32*49 potentiallycertifiable outputs, density{x['known_bit_density']:.6%}. All463 constant roots remain dependency1/known0. Packed32 demand traversal visits{min(v['fraction_full']for v in packed):.6%} to{max(v['fraction_full']for v in packed):.6%} of the complete7914981-node DAG for the two fixed child orders. Sixteen scalar traversals (eight predetermined audit lanes, both orders) visit{min(v['fraction_full']for v in scalar):.6%} to{max(v['fraction_full']for v in scalar):.6%}. The shared XOR backbone dominates; absorbing branches save little node work and scalarization loses packed execution.

This is a bounded negative on existing fixtures, not a universal lower bound. All frozen audit output words match the independent evaluator; absorbing identities pass{x['absorbing_truth_cases']} mixed-word truth controls. No source theorem, production program, library or active search was changed. A different symbolic representation might help, but no heavier lazy benchmark is justified by this evidence.
'''
(r/'mask-lazy-analysis-v1-report.md').write_text(text)
files={Path(__file__).resolve(),r/'mask-lazy-analysis-v1.py',r/'run-mask-lazy-analysis-v1.sh',r/'mask-lazy-analysis-v1-report.md'}|set(r.glob('evidence/mask-lazy-analysis-v1*'))
rows=[];data=[]
for p in sorted(files):
 if not p.is_file():continue
 b=p.read_bytes();name=str(p.relative_to(r));rows.append(dict(path=name,sha256=h(b),size=len(b)));data.append((name,b))
refs=[]
for p in[r/'evidence/mr-mask-tip-v3.bin',r.parent/'mask-evaluator-20261016/libmask8.so',r/'evidence/mr-mask-tip-v3.audit-input-u64le.bin',r/'evidence/mr-mask-tip-v3.audit-known-u64le.bin']:
 b=p.read_bytes();refs.append(dict(path=str(p),sha256=h(b),size=len(b)))
manifest=dict(status='TERMINAL_SOURCE_ONLY_LAZY_NEGATIVE',files=rows,server_only_refs=refs)
p=r/'evidence-mask-lazy-supplement.tar.gz'
with tarfile.open(p,'w:gz')as t:
 for name,b in data:
  i=tarfile.TarInfo(name);i.size=len(b);t.addfile(i,io.BytesIO(b))
 b=(json.dumps(manifest,indent=2)+'\n').encode();i=tarfile.TarInfo('MANIFEST.json');i.size=len(b);t.addfile(i,io.BytesIO(b))
with tarfile.open(p)as t:
 for row in rows:assert h(t.extractfile(row['path']).read())==row['sha256']
receipt=dict(status='ALL_MANIFEST_ENTRIES_VERIFY',archive=p.name,sha256=h(p.read_bytes()),files=len(rows),server_refs=len(refs))
(r/'evidence/mask-lazy-archive-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
