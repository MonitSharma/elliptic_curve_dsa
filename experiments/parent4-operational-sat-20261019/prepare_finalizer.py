"""Create the parent4 finalizer from the preserved reviewed PLAIN67 tools.

Run locally; does not execute a search, benchmark, census or upload.
"""
from pathlib import Path
r=Path(__file__).resolve().parent
out=r.parent/'parent4-final-sat-20261019';out.mkdir(exist_ok=False)
old=r.parent/'plain67-final-20261016'
audit=(old/'audit-terminal.py').read_text()
audit=audit.replace('7637b24901aa75ebc885db5ca1f6e908571e883ca95e0b13509fe7f9a80f1a66','4e3b1ce9a4f36ec1a781a5e304776a79831d6b70ff82fc248f7bb5e0c92b7ec9')
audit=audit.replace('f86c561634097b712582fe04f9d45a4bafab5c8ddf62476514e7cbf0956666bb','0a01214ee6c245a00d39031f5103470cc833f9f66b5120d702f48831ddf537aa')
audit=audit.replace("'final_benchmark_and_predeclared_census_still_required':True", "'final_benchmark_required':True,'existing_predeclared_gate_must_not_be_repeated':True")
(out/'audit-terminal.py').write_text(audit)
s=(old/'finalize.py').read_text()
start=s.index('def prepare():');end=s.index('\n\ndef native_receipt():')
prepare='''def prepare():
    audit = load('ROOT_TERMINAL_AUDIT.json')
    assert audit['status'] == 'LOWEST_PASS_COMPLETE_JSONL_AUDIT_PASS'
    k = audit['lowest_full_protected_pass']
    assert type(k) is int and 1 <= k < 2 ** 48
    gate = json.loads((native / 'RESULT.json').read_text())
    assert gate['status'] == 'FAILURE_GATE_PASS' and all(gate['rules'].values())
    archive = native / 'point-add-source.tar.gz'
    assert sha(archive) == archive_hash
    assert not t.exists()
    shutil.copy2(archive, r / 'original-point-add-source.tar.gz')
    subprocess.run(['git', '-C', str(ws / 'upstream'), 'worktree', 'add', '--detach', str(t), base], check=True)
    manifest = json.loads((native / 'point-add-source.json').read_text())
    with tarfile.open(archive) as a:
        members = a.getmembers()
        assert all((m.isfile() or m.isdir()) and (m.name + '/').startswith('src/point_add/') and '..' not in Path(m.name).parts for m in members)
        assert {m.name for m in members if m.isfile()} == set(manifest)
        a.extractall(t, filter='data')
    assert all(sha(t / p) == h for p,h in manifest.items())
    p = t / 'src/point_add/mod.rs'; src = p.read_bytes()
    assert src.count(OLD_NONCE) == 1
    p.write_bytes(src.replace(OLD_NONCE, str(k).encode()))
    assert {str(p.relative_to(t)) for p in (t/'src/point_add').rglob('*') if p.is_file()} == set(manifest)
    for name,h in manifest.items():
        if name == 'src/point_add/mod.rs':
            assert (t/name).read_bytes() == src.replace(OLD_NONCE,str(k).encode())
        else: assert sha(t/name) == h, name
    subprocess.run(['git','-C',str(t),'add','--intent-to-add','src/point_add'],check=True)
    (r/'candidate-source.patch').write_bytes(git('diff','--binary','HEAD','--','src/point_add'))
    files={name:sha(t/name) for name in sorted(manifest)}
    with tarfile.open(r/'point-add-source.tar.gz','w:gz') as a:
        for name in files:a.add(t/name,arcname=name,recursive=False)
    save('SOURCE_FREEZE.json',{'status':'FROZEN_BEFORE_NATIVE_TESTS_AND_BENCHMARK','base_revision':base,'candidate':str(t),
        'nonce':k,'only_change_from_frozen_source':f'TAIL_NONCE literal {OLD_NONCE.decode()} -> {k}',
        'old_source_archive_sha256':archive_hash,'selected_source_archive_sha256':sha(r/'point-add-source.tar.gz'),
        'patch_sha256':sha(r/'candidate-source.patch'),'source_files':files,'protected_files':protected(),
        'search_audit_sha256':sha(r/'ROOT_TERMINAL_AUDIT.json'),'old_stream_sha256':old_stream_hash,
        'failure_gate_sha256':sha(native/'RESULT.json'),'expected_pre_tail_ops':N_OPS-96,'submission_mode':'queue'})
    print('SOURCE_FREEZE_SHA256',sha(r/'SOURCE_FREEZE.json'),flush=True)
'''
s=s[:start]+prepare+s[end:]
s=s.replace('PLAIN67','parent4').replace("native = ws / 'product67-native-20261016'", "native = ws / 'product-pareto-20261019/parent4-qualification'")
s=s.replace('4b2ec52fc55da796aa8f5ef851290297e8706424','0c3a0751ab66bd9144358d67563bcb79201cf636')
s=s.replace('428f0806a78c2da52ec56bf00e62d11ede22c1c9812753e42600321dbd82925d','71bbeefcfa21ea9668439210f7dfbb279e0e623aa40b33c1b7516efcb45bb43c')
s=s.replace("frozen_bin_hash = '57da98da03ee66da1af9397b607d4ce3381a7aa8f43c2fd32d5255d7a8ec58d5'\n",'')
s=s.replace("ws / 'product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin'","ws / 'product-pareto-20261019/candidate-parent4/ops.bin'")
s=s.replace('268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d','9f50f06098026882a57f5f6c436abaaf68be79be2fc7c6e33b8e884065195a3a')
s=s.replace('17_891_821','17_889_606').replace('1046072871510','1048009047001').replace('product67-frozen-20261016','pareto-parent4-gate-20261019-v1')
s=s.replace("(native / 'candidate-census.jsonl')","(native / 'candidate.jsonl')")
s=s.replace(", 'loader_tests': 4",'')
s=s.replace("'next': 'User reviews; submission note drafted from STATUS.md; never auto-submitted'","'next': 'Prepare complete evidence and submission note; do not continue searching for another score'")
# Replace the obsolete copied overview with the actual scope.
s='''"""Finalize the frozen parent4 circuit after the complete lowest-nonce audit.

Queue mode: never uploads. The existing passing statistical gate is final.
Only the identity-tail nonce changes; source, protected files, native pre-tail
bytes, tail-invariance rows and the unchanged benchmark are all checked.
"""\n'''+s[s.index('from pathlib import Path'):]
(out/'finalize.py').write_text(s)
print(out)
