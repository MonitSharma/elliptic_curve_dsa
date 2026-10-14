"""Read-only static source/provenance audit; no execution of candidate code."""
from pathlib import Path
import subprocess,json,hashlib,collections,sys,datetime
store,evidence=map(Path,sys.argv[1:]);base='c5bb1ec876db859a3f9f8a9052c140a145df834e';leader='441d9ef9f5fe05107f4390e9f623caffdf77349d'
def git(*args):return subprocess.check_output(['git','--git-dir='+str(store),*args])
changed=git('diff','--name-only',base,leader).decode().splitlines();assert len(changed)==15 and all(p.startswith('src/point_add/')for p in changed)
hashes={p:hashlib.sha256(git('show',leader+':'+p)).hexdigest()for p in changed};protected={}
for p in ['Cargo.toml','Cargo.lock','rust-toolchain','benchmark.sh','src/bin/build_circuit.rs','src/bin/eval_circuit.rs','src/circuit.rs','src/sim.rs','src/weierstrass_elliptic_curve.rs']:
 a,b=git('show',base+':'+p),git('show',leader+':'+p);assert a==b;protected[p]=hashlib.sha256(a).hexdigest()
data=git('show',leader+':src/point_add/census_cut_data.txt').decode();rows=[l.split()for l in data.splitlines()if l.strip() and not l.lstrip().startswith('#')];assert len(rows)==144 and all(len(r)==7 for r in rows)
counts=collections.Counter((r[1],r[6].split(':')[0])for r in rows)
r={'status':'STATIC_SOURCE_REVIEW_ONLY','qualified_local_score':None,'base':base,'leader':leader,'object_store':str(store),'changed_files':changed,'changed_blob_sha256':hashes,'protected_equal_sha256':protected,'shipped_census_rows':len(rows),'census_action_counts':{':'.join(k):v for k,v in sorted(counts.items())},'narrowing_classes':[{'multiply':False,'width':21,'bits_removed':1},{'multiply':True,'width':16,'bits_removed':1},{'multiply':True,'width':21,'bits_removed':1},{'multiply':True,'width':22,'bits_removed':2}],'nonce_changed':['1024000750122','18364062961376'],'patch_sha256':hashlib.sha256((evidence/'actual-source.patch').read_bytes()).hexdigest(),'no_candidate_edits':True,'no_workloads_or_benchmarks':True,'collected_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(evidence/'static-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'changed_files':len(changed),'census_rows':len(rows),'counts':r['census_action_counts'],'protected_equal':True},indent=2))
