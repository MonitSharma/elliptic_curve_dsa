from pathlib import Path
import hashlib,json,tarfile,io
r=Path(__file__).resolve().parent/'scalar-split-v1';h=lambda b:hashlib.sha256(b).hexdigest()
assert(r/'run-v2.exit').read_text().strip()=='0' and(r/'steady-v1.exit').read_text().strip()=='0'
for a,b in[('before-v2.sha256','after-v2.sha256'),('steady-v1-before.sha256','steady-v1-after.sha256')]:assert(r/a).read_bytes()==(r/b).read_bytes()
v=json.load(open(r/'validation-benchmark.json'));t=json.load(open(r/'steady-benchmark-v1.json'));assert v['protected_coordinates']==24576 and v['protected_pairs']==4096 and v['independent_python_edge_pairs']==81
old=r.parents[1]/'scalar-fast-20261015';(r/'COPYING.secp256k1').write_bytes((old/'COPYING.secp256k1').read_bytes());(r/'VENDOR.txt').write_bytes((old/'VENDOR.txt').read_bytes())
text=f'''# Deferred expected-sum scalar API

Research-only immutable library:libscalar_split.so SHA256{v['new_library_sha256']}. Source scalar_split.c SHA256{v['new_source_sha256']}. It includes byte-identical copied original scalar_batch.c/public_comb.h and pinned clean bitcoin-core/secp256k1 commit1a53f4961f337b4d166c25fce72ef0dc88806618. Original files/library remain unchanged. MIT license preserved.

Initialize scalar_fast_fixed_init(20) once before worker threads. scalar_fast_inputs(count,scalar_pairs_be,triples_be) takes count<=64, each input64bytes, and writes P64,A64,DUMMY SUM64ZERO (192bytes/input). This dummy is not an expected value. Caller must track expectedReady and call scalar_fast_add_pairs before every witness comparison or full fallback comparison. scalar_fast_add_pairs(count,affine_pairs_be,expected_be) takes contiguous P64,A64 pairs128bytes/input and returns expected64bytes/input. Infinity is00; finite coordinates must be canonical/oncurve; invalid inputs/counts return0 before output writes. Count0 succeeds without pointers. Functions use local workspaces and immutable initialized table.

Protected validation passes all4096 reference pairs/24576 coordinates (fixtureSHA{v['protected_fixture_sha256']}),81 independent Python curve edge pairs including0/order/order+1/max/opposites/infinity, and{v['partial_invalid_guard_controls']} partial/invalid/canary controls. Failed first attempt was only an eight-field fixture parser mismatch; original script/log/exit1 are retained; corrected v2 exits0 with before/after hashes equal. No API source repair was needed.

Nine balanced paired timing rounds each use131072 fresh inputs (1179648unique pairs), pinned to one core. Original full P/A/sum median{t['median_us']['old_full']:.6f}us/pair; same-new-library full reference{t['median_us']['new_full']:.6f}us; P/A-only{t['median_us']['inputs']:.6f}us. Median paired input/original ratio{t['median_paired_ratio']['inputs_vs_original']:.6f}; same-library full/original{t['median_paired_ratio']['same_library_vs_original_full']:.6f}. Thus input preparation saves about5.1% time here, with a small/no change in full-function compiler control. Initial noisier five-round benchmark is preserved separately.

Deferred addition costs{v['deferred_add_api'][-1]['us_per_selected_input']:.6f}us/selected input at count64 and{v['deferred_add_api'][0]['us_per_selected_input']:.6f}us at count1 (PythonFFIincluded). At roughly1selected witness/512 prepared inputs, amortized deferred cost is small. A full9024 fallback requires all expected sums and may lose the preparation saving; full pipeline throughput has not been tested here. Root owns separate disabled integration/Ready controls. Active operational libraries are unchanged.
'''
(r/'REPORT.md').write_text(text)
files={p for p in r.iterdir()if p.is_file()and p.suffix!='.so'}|{Path(__file__).resolve()};rows=[];payload=[]
for p in sorted(files):
 b=p.read_bytes();name='scalar-split-v1/'+p.name if p.parent==r else p.name;rows.append(dict(path=name,sha256=h(b),size=len(b)));payload.append((name,b))
refs=[]
for p in[r/'libscalar_split.so',old/'libscalar_fast_batch.so',old/'validation-vectors.tsv']:
 b=p.read_bytes();refs.append(dict(path=str(p),sha256=h(b),size=len(b)))
manifest=dict(status='VALIDATED_DEFERRED_SUM_APIS_AND_FRESH_TIMING',files=rows,server_only_refs=refs,production_changed=False)
p=r.parent/'evidence-scalar-split-supplement.tar.gz'
with tarfile.open(p,'w:gz')as t:
 for name,b in payload:
  i=tarfile.TarInfo(name);i.size=len(b);t.addfile(i,io.BytesIO(b))
 b=(json.dumps(manifest,indent=2)+'\n').encode();i=tarfile.TarInfo('MANIFEST.json');i.size=len(b);t.addfile(i,io.BytesIO(b))
with tarfile.open(p)as t:
 for f in rows:assert h(t.extractfile(f['path']).read())==f['sha256']
rec=dict(status='ALL_MANIFEST_ENTRIES_VERIFY',archive=p.name,sha256=h(p.read_bytes()),files=len(rows),server_refs=len(refs));(r.parent/'evidence/scalar-split-archive-receipt.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec))
