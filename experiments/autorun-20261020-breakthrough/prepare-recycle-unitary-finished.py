from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,tarfile,re,difflib,sys
a=Path(__file__).resolve().parent;ex=a.parent;old=ex/'breakthrough-de8-repeat-final-20261020';proof=ex/'breakthrough-recycle-zero-measurements-v5-20261021';r=ex/(sys.argv[1] if len(sys.argv)>1 else 'breakthrough-recycle-unitary-finished-20261021');r.mkdir(exist_ok=False);t=r/'candidate';t.mkdir();sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
f=json.loads((old/'SOURCE-FREEZE.json').read_bytes());v=json.loads((proof/'RESULT.json').read_bytes());assert (proof/'run.exit').read_text().strip()=='0';assert all(x['exit']==0 and x['qualification']['protected_fullstream_comparisons']==24 for x in v['cases'].values());p=v['cases']['official_ffe20'];assert len(p['stats']['leases'])==13 and p['stats']['qubits']==1477 and p['stats']['input_records_sha3']=='373e44f24e185dd662b59a4ff683555b66a05c9995ff2684eefb6723446100cc';assert len(f['source_files'])==206
for path,h in f['protected_files'].items():
 source=ex/'breakthrough-value-guard-fusion-audit-20261020/local-protected'/path;assert sha(source)==h;dest=t/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
original={}
with tarfile.open(old/'point-add-source.tar.gz')as ar:
 assert {m.name for m in ar.getmembers()}==set(f['source_files'])
 for m in ar.getmembers():
  assert m.isfile()and m.name.startswith('src/point_add/')and'..'not in Path(m.name).parts;data=ar.extractfile(m).read();assert hashlib.sha256(data).hexdigest()==f['source_files'][m.name];original[m.name]=data;dest=t/m.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
path=t/'src/point_add/mod.rs';s=path.read_text();matches=list(re.finditer(r'pub fn build\s*\(\)\s*->\s*Vec<Op>\s*\{',s));assert len(matches)==1;m=matches[0];s=s[:m.start()]+s[m.start():m.end()].replace('pub fn build','fn recycle_original_parent_build')+s[m.end():];s+='\nmod recycle_measurements;\npub fn build()->Vec<Op>{recycle_measurements::run(recycle_original_parent_build())}\n';path.write_text(s)
source=(proof/'discover.rs').read_text();source=source[:source.index('fn qualify(')].replace('mod io;\n','',1)
source='\n'.join(line for line in source.splitlines() if not line.startswith(('fn flatten(', 'fn recycle(')))+'\n'
assert 'serde_json' not in source
source+='''
pub(super)const IDENTITY_NONCE:u64=0;
fn strip_identity_tail(mut ops:Vec<Op>)->Vec<Op>{let n=u64::MAX;assert!(ops.len()>=96);let end=ops.len()-96;for pair in ops[end..].chunks_exact(2){assert_eq!(pair[0],pair[1]);let o=pair[0];assert_eq!(o.kind,K::X);assert!(o.q_target.0<2);assert_eq!([o.q_control2.0,o.q_control1.0,o.c_target.0,o.c_condition.0,o.r_target.0],[n;5]);}ops.truncate(end);ops}
pub(super)fn run(ops:Vec<Op>)->Vec<Op>{assert_eq!(ops.len(),10995456);assert_eq!(hash(&ops),"373e44f24e185dd662b59a4ff683555b66a05c9995ff2684eefb6723446100cc","Exact official FFE parent binding");let leases=recycle_plan(&ops);let triples:Vec<_>=leases.iter().map(|p|(p.first,p.last,p.reset)).collect();assert_eq!(triples,vec![(5184983,5390191,5390191),(5232928,5246880,5246880),(5860757,5875383,5875383),(7392534,7394064,7394064),(7407948,7409478,7409478),(7423362,7424892,7424892),(7423366,7424901,7424901),(7438776,7440306,7440306),(7454190,7455720,7455720),(7469604,7471134,7471134),(7485018,7486548,7486548),(7485022,7486557,7486557),(7500432,7501962,7501962)]);let out=recycle_emit(&ops,&leases,true);assert_eq!(hash(&out),"f4445a684a2a1a5c22e177c375f7f27bb76c8c492fb9d7116649f0a9c422e0cb","Complete native14/fresh48 protected qualified emitter binding");let mut out=strip_identity_tail(out);assert!(IDENTITY_NONCE<(1u64<<48));for bit in 0..48{let o=make(K::X,u64::MAX,u64::MAX,(IDENTITY_NONCE>>bit)&1,u64::MAX,u64::MAX);out.extend([o,o]);}eprintln!("EXACT_ORIGINAL_MEASUREMENT_RECYCLE leases=13 unitary_cleanup no_new_random_word nonce={IDENTITY_NONCE}");out}
#[cfg(test)]mod finished_tail_tests{use super::*;fn tail(n:u64)->Vec<Op>{let mut out=vec![];for bit in 0..48{let o=make(K::X,u64::MAX,u64::MAX,(n>>bit)&1,u64::MAX,u64::MAX);out.extend([o,o]);}out}
#[test]fn all_tail_bits_are_checked(){for n in[0,261,(1u64<<48)-1]{assert!(strip_identity_tail(tail(n)).is_empty());}}
#[test]#[should_panic]fn mismatched_pair_is_rejected(){let mut x=tail(0);x[95].q_target=QubitId(1);strip_identity_tail(x);}
#[test]#[should_panic]fn nonidentity_data_qubit_is_rejected(){let mut x=tail(0);x[94].q_target=QubitId(2);x[95].q_target=QubitId(2);strip_identity_tail(x);}}
'''
(t/'src/point_add/recycle_measurements.rs').write_text(source)
files={p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()};assert len(files)==207
patch=[]
for path in ['src/point_add/mod.rs','src/point_add/recycle_measurements.rs']:
 patch.extend(difflib.unified_diff(original.get(path,b'').decode().splitlines(True),(t/path).read_text().splitlines(True),fromfile='a/'+path,tofile='b/'+path))
(r/'source.patch').write_text(''.join(patch))
with tarfile.open(r/'point-add-source.tar.gz','w:gz')as ar:
 for path in sorted(files):ar.add(t/path,arcname=path,recursive=False)
spec={'declared_at_utc':datetime.now(timezone.utc).isoformat(),'base':'4033714fd5f0a038c9823b78d992f29533dabc43','source_files':files,'protected_files':f['protected_files'],'identity_nonce':0,'operations':11292560,'expected_qubits':1477,'parent_record':'ffe20d35-ecb7-47da-9dde-1b8d80ffde60','parent_stream_sha256':'9185ad8965bec47212849d3569e2e4ce4ef86a2e15d0248bee392107beac4927','parent_records_sha3':'373e44f24e185dd662b59a4ff683555b66a05c9995ff2684eefb6723446100cc','semantic_records_sha3_with_original_tail':'f4445a684a2a1a5c22e177c375f7f27bb76c8c492fb9d7116649f0a9c422e0cb','source_archive_sha256':sha(r/'point-add-source.tar.gz'),'source_patch_sha256':sha(r/'source.patch'),'semantic_proof_native_controls':14,'new_runtime_native_controls':17,'semantic_proof_source_freeze_sha256':sha(proof/'SOURCE-FREEZE.json'),'semantic_proof_result_sha256':sha(proof/'RESULT.json'),'scope':'Finished exact full-prefix measurement-recycling candidate versus current FFE Toffoli record. Source206 parent files byte-identical except build wrapper, new207th module rederives all13 leases on original full trace. All13 leases discharged by exact original-wire CX uncompute, including same-last-operation transfer. Original measurements unchanged. Helpers zero, arbitrary input/phase/classical/RNG semantics preserved. Measurement branch is available but unused on this frozen source. Prior native14/fresh48 complete protected comparisons PASS. New runtime native17 and local/official1.93 bytecontrol, NEWfinished development and OWNsolefinalgate vs exactcurrentFFE required. Extra width acceptable for independent Toffoli objective. No nonce/benchmark/upload beforePASS.'}
(r/'SOURCE-SPEC.json').write_text(json.dumps(spec,indent=2)+'\n');(r/'.gitignore').write_text('candidate/\n__pycache__/\n*.ops.bin\n');(r/'.gitattributes').write_text('* -text\n');(r/'PLAN.md').write_text('# Finished original-measurement recycling candidate\n\n'+spec['scope']+'\n')
template=ex/'breakthrough-public-semantic-finished-20261021'
s=(template/'verify.py').read_text().replace('==1234','==1477').replace("'qubits':1234","'qubits':1477").replace('NATIVE4','NATIVE17').replace("'native_controls':4","'native_controls':17").replace("'prior_semantic_native_proof':12","'prior_semantic_native_proof':14");(r/'verify.py').write_text(s)
s=(template/'run-local.sh').read_text().replace(template.name,r.name).replace('exact_semantic_product','recycle_measurements').replace('point_add::recycle_measurements::tests','point_add::recycle_measurements::').replace('4 passed;','17 passed;');(r/'run-local.sh').write_bytes(s.encode())
print(r.name,len(files))
