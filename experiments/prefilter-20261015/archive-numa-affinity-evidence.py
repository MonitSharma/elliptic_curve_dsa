from pathlib import Path
import hashlib,json,tarfile,io,statistics
base=Path(__file__).resolve().parent;r=base/'numa-affinity-v1';h=lambda b:hashlib.sha256(b).hexdigest()
assert(r/'run.exit').read_text().strip()=='0';assert(r/'before.json').read_bytes()==(r/'after.json').read_bytes();x=json.load(open(r/'RESULT.json'));locality=json.load(open(r/'LOCALITY_VALIDATION.json'));assert x['all4096_rows_identical']and not x['FAST_ZERO_DISPATCH_present']
canonical=None
for trial in range(3):
 for mode in['unbound','numa3']:
  rows=sorted(map(json.loads,(r/f'{mode}-{trial}.jsonl').read_text().splitlines()),key=lambda v:v['nonce']);assert len(rows)==4096 and[v['nonce']for v in rows]==list(range(1,4097))and all(v['proof_accepted']is False and v['authoritative_rejection']is False for v in rows)
  if canonical is None:canonical=rows
  else:assert canonical==rows
ratio=x['median_seconds']['numa3']/x['median_seconds']['unbound']
text=f'''# Disabled NUMA-affinity comparison: no robust node3 win

Frozen disabled product-dispatch-filter binary SHA256fa676f130fdeae547c8e40eb7fd20375d1058c5285609c93f4a3e8e9155f3356; candidate25 source180af069; FAST_ZERO_DISPATCH absent in both environments. Three predeclared paired4096-nonce trials use4threads,first1,look4096, alternating mode order. Every complete sorted JSON row matches the frozen disabled reference d4118048 and all paired runs; all proof/authoritative-rejection gates remain false.24576 repeated timing attempts cover4096 distinct nonces, not an operational search.

| Trial | Unbound seconds | Node3 seconds | Bound/unbound |
|---|---:|---:|---:|
'''
for j in range(3):text+=f"|{j}|{x['times_seconds']['unbound'][j]:.6f}|{x['times_seconds']['numa3'][j]:.6f}|{x['paired_ratio'][j]:.6f}|\n"
text+=f'''
Medians:unbound{x['median_seconds']['unbound']:.6f}s,node3{x['median_seconds']['numa3']:.6f}s,ratio{ratio:.6f}. Bound median is about{(ratio-1)*100:.2f}% slower; paired results vary in both directions. This is a bounded negative under the existing concurrent load, not a universal claim about NUMA affinity. No active worker affinity or production library/source changed.

The new isolated bound processes use numactl --cpunodebind=3 --membind=3, CPUs54-71/126-143. Captured child CPU masks match; maximum recorded resident-page samples are~99.9% onnode3. The identical separate policy probe reports bind/membind3. Mems_allowed_list remains the cpuset allowance0-3 and is not the per-process numactl memory policy. Unbound parent policy/default and all144CPUs are checked before launch. Resource preflight found261GiB available and~62GiBnode3free, with60 aggregate agent compute threads including this4-thread job. Separate unrelated lattice jobs were left untouched.

Reported wall_seconds measures the frozen tool's work section after initialization. Subprocess durations include initialization, output parsing and up to2seconds polling overhead, so they are not a separate steady-state comparison. Inputs, source binary and model hashes are unchanged before/after. Raw resource/process inventories remain server-only hash references; complete outcome rows, declarations, scripts, receipts and locality samples are archived. The runtime is terminal and its4-thread budget released.
'''
(r/'REPORT.md').write_text(text)
files=[];refs=[]
for p in sorted(r.iterdir()):
 if not p.is_file():continue
 if p.name.endswith('-resources.json')or p.name=='preflight-processes.txt':refs.append(dict(path=str(p),sha256=h(p.read_bytes()),size=p.stat().st_size))
 else:files.append(p)
files.append(Path(__file__).resolve());rows=[];payload=[]
for p in files:
 b=p.read_bytes();name=str(p.relative_to(base));rows.append(dict(path=name,sha256=h(b),size=len(b)));payload.append((name,b))
for p in[base.parent/'product-dispatch-filter-20261016/tool/target/release/value_prefilter',base.parent/'product-exact-20261015/candidate-product-final25/ops.bin',base.parent/'product-early-filter-20261016/rows4096.jsonl']:
 b=p.read_bytes();refs.append(dict(path=str(p),sha256=h(b),size=len(b)))
manifest=dict(status='DISABLED_NUMA_BOUNDED_NEGATIVE_ALL_ROWS_IDENTICAL',files=rows,server_only_refs=refs,active_worker_affinity_changed=False)
p=base/'evidence-numa-affinity-supplement.tar.gz'
with tarfile.open(p,'w:gz')as t:
 for name,b in payload:
  i=tarfile.TarInfo(name);i.size=len(b);t.addfile(i,io.BytesIO(b))
 b=(json.dumps(manifest,indent=2)+'\n').encode();i=tarfile.TarInfo('MANIFEST.json');i.size=len(b);t.addfile(i,io.BytesIO(b))
with tarfile.open(p)as t:
 for row in rows:assert h(t.extractfile(row['path']).read())==row['sha256']
rec=dict(status='ALL_MANIFEST_ENTRIES_VERIFY',archive=p.name,sha256=h(p.read_bytes()),files=len(rows),server_refs=len(refs));(base/'evidence/numa-affinity-archive-receipt.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec))
