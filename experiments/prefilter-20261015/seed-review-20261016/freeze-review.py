from pathlib import Path
import json,hashlib,tarfile,io
r=Path(__file__).resolve().parent;s=r/'source'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((s/'seed-bdd-contract.json').read_text());marks=json.loads((s/'actual-seed-markers.json').read_text());prefix=json.loads((r/'seed-prefix-pinned-v1/RECEIPT.json').read_text());decl=json.loads((s/'PREDECLARATION.json').read_text());meta=json.loads((s/'seed-prefix-source.json').read_text())
target=marks['markers'][0]['target'];scratch=proof['original_source']['scratch_preconditions_zero']
assert len(target)==len(set(target))==256 and len(scratch)==len(set(scratch))==48 and not(set(target)&set(scratch))
assert marks['actual_stream_sha256']=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
assert [m['at']for m in marks['markers']]==[618858,619791]
assert marks['source_counts']=={'seed':2} and marks['unknown_regions']==0
assert prefix['before_after_all_identical'] and prefix['all48scratch_exact_zero_for_all_symbolic_ABI_inputs_and_MR']
assert sha(s/'PREDECLARATION.json')==prefix['original_declaration_sha256']=='98ccedaa3eaed8efa99458d2daa84aa7968d3e19ee765855aa47d606c30115c6'
for name in ['actual-seed-markers.json','seed-bdd-contract.json','seed-prefix-source.json']:
 assert sha(s/name)==prefix['files_before_after']['/home/hclau/ecdsa_research/current-value-attribution-20261016/'+name]
for name in ['seed_prefix_zeros.rs','seed_support.rs']:
 assert sha(s/name)==meta['files']['tool/src/bin/'+name]
before=json.loads((r/'seed-prefix-pinned-v1/before.json').read_text());after=json.loads((r/'seed-prefix-pinned-v1/after.json').read_text());assert before==after==prefix['files_before_after']
q=json.loads((r/'seed-prefix-pinned-v1/replay.log').read_text().splitlines()[0]);assert q['q']==scratch and all(q['exact_zero']) and q['at']==618858
assert sha(r/'seed-prefix-pinned-v1/replay.log')==prefix['new_log_sha256']
report={
 'status':'INDEPENDENT_SEED_HELPER_VALUE_PHASE_SCRATCH_AND_PINNED_PREFIX_SOURCE_REVIEW_PASS',
 'source_stream_sha256':marks['actual_stream_sha256'],'actual_span':[618858,619791],
 'restored_region_sha256':proof['source_raw_region_sha256'],'old_region_sha256':proof['actual_region_sha256'],
 'source_files':[{'path':p.relative_to(r).as_posix(),'sha256':sha(p)}for p in sorted(s.iterdir())if p.is_file()],
 'prefix_binding_receipt_sha256':sha(r/'seed-prefix-pinned-v1/RECEIPT.json'),
 'review':[
  'BDD XOR/AND Shannon recurrences, canonical node interning and fresh variable ordering are sound;1million-node cap asserts/UNKNOWN and cannot silently accept.',
  'All256 target entry bits are arbitrary. All48 distinct required scratch wires are explicitly initialized0; they are disjoint from target. No arbitrary-dirty scratch correctness is claimed.',
  'Independent borrow recurrence proves the exact finite low53-bit subtraction of(2^32+977)*parity, then parity-loaded right rotation; it is not ideal modular halving for every input.',
  'No quantum value update reads a classical/MR guard; every phase guard must be an earlier HMR result. Thus q coefficients are input-only and phase is a sum of96 independent fresh MR variables times exact BDD coefficients. All coefficients0 proves phase0 for all measurement choices.',
  'R and HMR each contribute their own fresh MR phase and reset target0. Classical HMR results record the same MR ordinal. No unconditional phase or unsupported opcode is silently ignored.',
  'The restored/current helpers differ only at one unconditional CX/CCX quantum update; all classical events, R/HMR positions/targets and phase/classical operations are identical. Their classical transducers are therefore exactly equal under identical MR tapes, independent of quantum entry.',
  'Whole-prefix Support initializes declared quantum/classical ABI values symbolically, aux0; propagates actual operations, captured Push snapshots, conditional classical stores and fresh HMR muxes. Fresh immutable caps/cache eviction lose identities, never invent zero. Ignored rewrite return does not change propagated actual q state.',
  'Separate new before/after-hash-pinned replay binds actual2a, exact markers, proof/driver/Support/binary/Cargo/build log. It proves precisely the same48 scratch wires0 at actual entry618858 and reproduces the preserved old query.',
  'All source mod_halve_pm calls are observed by a wrapper of the unique function definition, gate-inert rawstream tied toff5163. Two markers mean one complete933-op helper. Exact full raw/final region diff is one census row11 CCX(881,1106->1134) reduced toCX; source family restores all matching seed dropped-control edits(size1).',
  'Candidate transform binds the entire frozen posttable input digest, locates one complete933-op body, restores only relative142, rejects conditional/wrong-control/ambiguous cases, checks depth0 and exact ABI preservation. Prefix before the edit is unchanged, discharging clean entry for this candidate.',
  'Existing protected structured/mixed captured-guard tests supplement the universal argument; their empirical success does not replace the local BDD or global clean-prefix proof.'
 ],
 'historical_finding':{'detail':'Original prefix driver/wrapper lacked explicit stream/markers before-after hashes.','resolution':'Separate pinned replay receipt preserved old evidence and bound all inputs, source and binary; reviewed and verified.','resolved':True},
 'remaining':['Full native candidate stream/source-byte verification still required.','Fresh predeclared32768 full point-addition census, unchanged benchmark and record comparison remain separate.','No transfer of original4b mask or existing conditionalA29 mask is established by this review.','No complete point-addition correctness, final failure-rate improvement, record or submission authority is claimed.'],
 'workloads_launched_by_reviewer':False,'original_files_modified':False}
out=r/'REVIEW.json';assert not out.exists();out.write_bytes((json.dumps(report,indent=2)+'\n').encode())
archive=r.parent/'evidence-seed-independent-review.tar.gz';assert not archive.exists()
files=[p for p in r.rglob('*')if p.is_file()]
manifest={'status':'INDEPENDENT_SOURCE_REVIEW_COMPONENT_ONLY','files':[{'path':p.relative_to(r).as_posix(),'sha256':sha(p)}for p in sorted(files)]}
with tarfile.open(archive,'w:gz')as t:
 for p in files:t.add(p,arcname=p.relative_to(r).as_posix(),recursive=False)
 b=(json.dumps(manifest,indent=2)+'\n').encode();i=tarfile.TarInfo('MANIFEST.json');i.size=len(b);t.addfile(i,io.BytesIO(b))
with tarfile.open(archive)as t:
 for row in manifest['files']:assert hashlib.sha256(t.extractfile(row['path']).read()).hexdigest()==row['sha256']
print(json.dumps({'review_sha256':sha(out),'archive_sha256':sha(archive),'files':len(files)}))
