from pathlib import Path
import hashlib,json,difflib,tarfile,io
d=Path(__file__).resolve().parent;p=d.parent/'prefilter-20261015'
def sha(x):return hashlib.sha256(x.read_bytes()).hexdigest()
def js(path,x):path.write_bytes((json.dumps(x,indent=2)+'\n').encode())
assert (d/'run.exit').read_text().strip()=='0'
assert (d/'before.sha256').read_bytes()==(d/'after.sha256').read_bytes()
assert (d/'compile-mask-fused.py').read_bytes()==(p/'compile-mask-fused.py').read_bytes()
original=(p/'verify-mask-fused.py').read_text()
adapted=original.replace("r=Path(__file__).parent;prefix=r/'evidence/mr-mask-tip-v3-fused'","r=Path(__file__).parent;prefix=r/'guard-fused'").replace("source=(r/'evidence/mr-mask-tip-v3.bin').read_bytes()","source=(r/'guard512.bin').read_bytes()").replace("(r/'evidence/mask-fused-verification.json')","(r/'whole-plan-verification.json')")
assert (d/'verify-mask-fused.py').read_text()==adapted
(d/'CHECKER-PATH-ONLY-DIFF.patch').write_bytes(''.join(difflib.unified_diff(original.splitlines(True),adapted.splitlines(True),fromfile='prefilter/verify-mask-fused.py',tofile='guard-fused/verify-mask-fused.py')).encode())
for name in ['mask_fused.c','mask_fused.h']:(d/name).write_bytes((p/name).read_bytes())
v=json.loads((d/'whole-plan-verification.json').read_text());w=json.loads((d/'WRAPPER-EQUIVALENCE.json').read_text());result=json.loads((d/'RESULT.json').read_text())
assert v['source_sha256']==w['wrapper_sha256']==result['wrapper_sha256']
assert v['plan_sha256']==result['plan_sha256']
assert v['slots']==1656 and v['instructions']==1130985
prior=p/'evidence/mask-fused-runtime.json'
lineage={'status':'UNIVERSAL_NODE_IDENTITY_COMPILED_FUNCTION_EQUIVALENCE_PLUS_WRAPPER_LINEAGE_NO_AUTHORITY',
 'original_guard_sha256':w['original_guard_sha256'],'wrapper_sha256':w['wrapper_sha256'],
 'node_body_sha256':w['unchanged_node_body_sha256'],'wrapper_equivalence_receipt_sha256':sha(d/'WRAPPER-EQUIVALENCE.json'),
 'compiler':{'source_path':'/home/hclau/ecdsa_research/prefilter-20261015/compile-mask-fused.py','sha256':sha(p/'compile-mask-fused.py'),'private_copy_path':'/home/hclau/ecdsa_research/guard-fused-20261016/compile-mask-fused.py','byte_identical':True},
 'checker':{'original_path':'/home/hclau/ecdsa_research/prefilter-20261015/verify-mask-fused.py','original_sha256':sha(p/'verify-mask-fused.py'),'private_path':'/home/hclau/ecdsa_research/guard-fused-20261016/verify-mask-fused.py','private_sha256':sha(d/'verify-mask-fused.py'),'only_changes':'Three file-path literals, independently asserted by freeze-evidence.py; all proof/admission logic unchanged.'},
 'plan':{'path':'/home/hclau/ecdsa_research/guard-fused-20261016/guard-fused.bin','sha256':v['plan_sha256'],'embedded_source_sha256':v['source_sha256'],'slots':v['slots'],'instructions':v['instructions'],'slot16_capacity_checked':True},
 'sidecar':{'path':'/home/hclau/ecdsa_research/guard-fused-20261016/guard-fused.nodeids-u32le.bin','sha256':v['nodeids_sha256'],'schema':'Two u32LE per instruction: original source node ID, absorbed child ID or0xffffffff. Strictly increasing original IDs.','role':'Mandatory universal independent-verifier witness, not a runtime input. Reconstructs every retained/fused instruction and current slot contents against exact original nodes, then each final root; prevents accepting sample-equivalent but structurally different plans.'},
 'universal_equivalence_argument':['Wrapper header n/np, every node byte and all input references are identical to rawG355f; all512 wrapper root IDs equal the original sole root. Thus every wrapper output equals rawG on every1024-bit assignment.',
 'Whole-plan verifier symbolically labels each live slot with its exact original-node ID. Every ordinary instruction must reconstruct that original node from current child IDs; every fused instruction reconstructs an exact two-level original XOR/AND/OR expression with the correct third child. No sampled values establish this step.',
 'Every final output slot must contain the original root ID. Slot reuse is sound only when the complete reconstruction succeeds. The resulting function equals all512 wrapper roots for every public input, hence rawG.',
 'The already proven Ckernel dc8219 executes these primitive Boolean operations, with finite exhaustive truth-table controls in its pinned prior runtime receipt. This component adds structural proof for this plan, exact fixture/partial controls and source/kernel hash invariance.'],
 'kernel':{'path':'/home/hclau/ecdsa_research/prefilter-20261015/libmask_fused.so','sha256':result['kernel_sha256'],'source_sha256':sha(d/'mask_fused.c'),'header_sha256':sha(d/'mask_fused.h'),'prior_truth_table_and_runtime_receipt_sha256':sha(prior)},
 'polarity':'All512 raw outputs equal G, NOT knownness; caller safe=NOT G and G1 must never retain a witness.',
 'component_only':True,'runtime_operational_changes':False,'new_search_authority':False}
js(d/'COMPILATION-LINEAGE.json',lineage)
archive=p/'evidence-guard-fused-component.tar.gz';assert not archive.exists()
files=[x for x in d.iterdir()if x.is_file()]
refs=[lineage['plan'],lineage['sidecar'],{'path':'/home/hclau/ecdsa_research/guard-fused-20261016/guard512.bin','sha256':w['wrapper_sha256']},{'path':'/home/hclau/ecdsa_research/prefilter-20261015/a29-conditional-prefix-v1/public-discrepancy-guard.bin','sha256':w['original_guard_sha256']},lineage['kernel']]
manifest={'status':'IMMUTABLE_UNIVERSAL_WRAPPER_PLAN_AND_COMPONENT_VALIDATION_NO_AUTHORITY','files':[{'path':x.relative_to(d).as_posix(),'sha256':sha(x),'bytes':x.stat().st_size}for x in sorted(files)],'server_only_hashrefs':refs}
with tarfile.open(archive,'w:gz')as t:
 for x in files:t.add(x,arcname=x.relative_to(d).as_posix(),recursive=False)
 b=(json.dumps(manifest,indent=2)+'\n').encode();i=tarfile.TarInfo('MANIFEST.json');i.size=len(b);t.addfile(i,io.BytesIO(b))
with tarfile.open(archive)as t:
 for row in manifest['files']:assert hashlib.sha256(t.extractfile(row['path']).read()).hexdigest()==row['sha256']
receipt={'status':'ALL_ARCHIVED_MANIFEST_ENTRIES_VERIFY','archive':archive.name,'sha256':sha(archive),'files':len(files),'server_only_hashrefs':len(refs),'lineage_sha256':sha(d/'COMPILATION-LINEAGE.json')}
js(p/'evidence/guard-fused-archive-receipt.json',receipt);print(json.dumps(receipt))
