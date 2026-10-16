from pathlib import Path
import hashlib,json,tarfile,io
r=Path(__file__).resolve().parent;e=r/'evidence';h=lambda b:hashlib.sha256(b).hexdigest()
assert(e/'candidate67-static-abi.exit').read_text().strip()=='0' and(e/'mask-validate-transfer67.exit').read_text().strip()=='0'
for prefix in['candidate67-static-abi','mask-validate-transfer67']:assert(e/f'{prefix}-before.sha256').read_bytes()==(e/f'{prefix}-after.sha256').read_bytes()
a=json.load(open(e/'candidate67-static-abi.json'));assert a['all_four_physical_ABI_identical'] and a['required_joint_q_capacity']==1234 and a['required_joint_bit_capacity']==54995
reports=[json.load(open(e/f'mask-validate-transfer67-{name}.json'))for name in['audit','all-failing-tip','sensitivity-structured','sensitivity-arbitrary']];assert sum(x['shots']for x in reports)==2214 and all(x['candidate_protected_vs_original_zeroMR_known_bit_containment_passed']and x['independent_candidate_physical_mr_streams']==8 for x in reports)
cert=r.parent/'product-exact-20261015/cache-certificate67-20261016';assert h((cert/'CACHE_EQUIVALENCE_CERTIFICATE.json').read_bytes())=='303a75ec86a4da8c3a4008646e1b8257768fa40e198f0b7172eeafd19408c7c6';assert h((cert/'PER_INPUT_MASK_TRANSFER.json').read_bytes())=='d774c492b94f1c6ca458cc42de82d6dbee90a316f7d80c9dc6ee32eb1fe5201f'
text='''# Candidate67 source binding and protected known-bit controls

Frozen candidate stream268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d has17891821 operations,Q1234,B54995. Independent protected loader/analyze_ops confirms all four ordered256-slot physical ABIs equal original4b. Candidate-sized Q1234/B54995 workspace covers original Q1234/B45701. This check concerns actual physical IDs, not only register lengths.

Pinned original source2a522394, frozen mask560c12d5, unchanged validated executable9b83de8e and candidate source were checked before/after. Universal67 cache certificate303a75ec86a4da8c3a4008646e1b8257768fa40e198f0b7172eeafd19408c7c6 and conditional per-input transferd774c492b94f1c6ca458cc42de82d6dbee90a316f7d80c9dc6ee32eb1fe5201f were available and explicitly hash-bound before replay. Their provenance and proof obligations remain those separate certificate artifacts.

Protected Simulator tests compare all certified-known coordinate bits on2214 fixed inputs, each under8 independent candidate physicalMR streams, to ORIGINAL zeroMR values. All17712 containment checks pass, including541 preserved failing inputs (421 certified wrong),32 audit inputs (24 certified wrong),256 structured inputs (125 certified wrong),1385 arbitrary inputs (containment only, placeholder expected values make no failure claim). This is an empirical supplement to the separately supplied universal transfer, not a replacement for it. Phase/garbage behavior is outside this coordinate certificate and still requires exact fallback. No candidate search or operational source/library was changed here.
''';(r/'candidate67-knownbit-report.md').write_text(text)
files={Path(__file__).resolve(),r/'candidate67-knownbit-report.md',r/'run-candidate67-static-abi.sh',r/'run-mask-validate-transfer67.sh',r/'tool/src/bin/stream_abi_audit.rs',r/'tool/src/mask_validate_transfer_body.rs',r/'tool/src/bin/mask_validate_transfer.rs'}|set(e.glob('candidate67-static-abi*'))|set(e.glob('mask-validate-transfer67*'));rows=[];payload=[]
for p in sorted(files):
 if not p.is_file():continue
 b=p.read_bytes();name=str(p.relative_to(r));rows.append(dict(path=name,sha256=h(b),size=len(b)));payload.append((name,b))
refs=[]
for p in[r/'tool/target/release/stream_abi_audit',r/'tool/target/release/mask_validate_transfer',e/'mr-mask-tip-v3.bin',cert/'CACHE_EQUIVALENCE_CERTIFICATE.json',cert/'PER_INPUT_MASK_TRANSFER.json',r.parent/'product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin',r.parent/'product-exact-20261015/tip/ops.bin']:
 b=p.read_bytes();refs.append(dict(path=str(p),sha256=h(b),size=len(b)))
manifest=dict(status='CANDIDATE67_STATIC_ABI_WORKSPACE_AND_PROTECTED_KNOWNBIT_CONTROLS_PASS',files=rows,server_only_refs=refs)
p=r/'evidence-candidate67-controls.tar.gz'
with tarfile.open(p,'w:gz')as t:
 for name,b in payload:
  i=tarfile.TarInfo(name);i.size=len(b);t.addfile(i,io.BytesIO(b))
 b=(json.dumps(manifest,indent=2)+'\n').encode();i=tarfile.TarInfo('MANIFEST.json');i.size=len(b);t.addfile(i,io.BytesIO(b))
with tarfile.open(p)as t:
 for f in rows:assert h(t.extractfile(f['path']).read())==f['sha256']
rec=dict(status='ALL_MANIFEST_ENTRIES_VERIFY',archive=p.name,sha256=h(p.read_bytes()),files=len(rows),server_refs=len(refs));(e/'candidate67-controls-archive-receipt.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec))
