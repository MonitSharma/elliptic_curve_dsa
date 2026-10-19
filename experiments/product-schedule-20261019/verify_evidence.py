import hashlib,json,tarfile,re
from pathlib import Path
r=Path(__file__).resolve().parent
archive=r/'evidence.tar.gz'
expected=(r/'EVIDENCE.sha256').read_text().split()[0]
assert hashlib.sha256(archive.read_bytes()).hexdigest()==expected
manifest=json.loads((r/'EVIDENCE-MANIFEST.json').read_text())
with tarfile.open(archive) as tar:
    names={m.name:m for m in tar.getmembers() if m.isfile()}
    assert set(manifest)<=set(names)
    for name,digest in manifest.items():
        assert hashlib.sha256(tar.extractfile(names[name]).read()).hexdigest()==digest,name
    source=json.loads(tar.extractfile('TERMINAL.json').read())
    assert source['parent_status']==''
    assert source['parent_stream_sha256']=='99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683'
    assert set(source['terminal_exits'].values())=={'0'}
    count=0
    for name in ('last-carry-tests.log','commute-tests.log'):
        log=tar.extractfile(name).read().decode()
        assert 'test result: FAILED' not in log
        count+=sum(map(int,re.findall(r'test result: ok\. (\d+) passed;',log)))
    assert count==31,count
    commute=json.loads(tar.extractfile('commute-parent.json').read())
    assert commute['unconditional_Toffolis_removed']==0
    assert commute['input_sha3_256']==commute['output_sha3_256']
result={'status':'LOCAL_EVIDENCE_VERIFIED','archive_sha256':expected,
        'verified_files':len(manifest),'tool_tests_passed':count,
        'parent_unchanged':True,'all_five_launchers_exited_zero':True,
        'qualified_product_improvement':False}
(r/'LOCAL-VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
