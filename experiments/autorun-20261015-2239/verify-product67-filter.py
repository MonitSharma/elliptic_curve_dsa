"""Independent complete row/marker/source-difference review of disabled67 runtime."""
from pathlib import Path
import hashlib,json,tarfile
root=Path(__file__).resolve().parents[2]/'experiments'
new=root/'product67-filter-20261016'
with tarfile.open(new/'evidence.tar.gz') as archive,tarfile.open(root/'product-dispatch-filter-20261016/evidence.tar.gz') as old:
    def read(name):return archive.extractfile(name).read()
    def rows(name,count,first):
        data=sorted(map(json.loads,read(name+'.jsonl').splitlines()),key=lambda r:r['nonce'])
        assert len(data)==count and [r['nonce'] for r in data]==list(range(first,first+count))
        assert all(not r['authoritative_rejection'] and not r['proof_accepted'] for r in data)
        assert b'CANDIDATE_OWN_FIAT_PROTECTED_4096_BYTE_CONTROLS_PASS nonces=1,2,17,255' in read(name+'.err')
        return data
    for prefix,n,first in [('shadow128',128,1),('partial',11,17)]:
        assert rows(prefix+'-generic',n,first)==rows(prefix+'-threaded',n,first)
    assert b'EARLY_FULLSTATE_AND_PHYSICAL_RNG9024_PASS nonce=1' in read('shadow128-generic.err')
    reference=rows('baseline-0',4096,1)
    for name in ['baseline-1','baseline-2','threaded-0','threaded-1','threaded-2']:assert rows(name,4096,1)==reference
    assert read('run-v2.exit').strip()==b'0' and read('run.exit').strip()==b'1'
    assert read('binary-before-v2.sha256')==read('binary-after-v2.sha256')
    names={n for n in archive.getnames() if n.startswith('tool/')}
    oldnames={n for n in old.getnames() if n.startswith('tool/')}
    assert names==oldnames
    changed={n for n in names if read(n)!=old.extractfile(n).read()}
    assert changed=={'tool/src/packed_body.rs','tool/src/transfer.rs'}
    packed=old.extractfile('tool/src/packed_body.rs').read().replace(b'180af069679ffa33b099b200d3337d6fc6c20a451a72508a40dea6617150dc64',b'268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d').replace(b'assert_eq!(n,14_142_629)',b'assert_eq!(n,17_891_821)')
    assert packed==read('tool/src/packed_body.rs')
    transfer=old.extractfile('tool/src/transfer.rs').read()
    for a,b in [
      ('cache-certificate-v2-20261016','cache-certificate67-20261016'),
      ('4857f8255c6aa85f0c6cb84720c6d5690aaca060f2758a8c517bd43fc5e2f04e','303a75ec86a4da8c3a4008646e1b8257768fa40e198f0b7172eeafd19408c7c6'),
      ('722be8db61c0a29533f3297a31192e64f7558d4c828b210c1b1dc33ce272c8b3','d774c492b94f1c6ca458cc42de82d6dbee90a316f7d80c9dc6ee32eb1fe5201f'),
      ('efc7c9583caf0d918fa555694a51aed9959b19c6b29fc198c2e82a8affc22317','5914f683bb5df08d21f94d79663c6239a84715e27b2eac7e18ce1fcafaee0167'),
      ('candidate180af069 universal25stage','candidate268aefe2 universal67stage')]:
        assert transfer.count(a.encode())==1
        transfer=transfer.replace(a.encode(),b.encode())
    assert transfer==read('tool/src/transfer.rs')
receipt={'status':'INDEPENDENT_DISABLED_PRODUCT67_ROW_SOURCE_AND_CONTROL_REVIEW_PASS','archive_sha256':hashlib.sha256((new/'evidence.tar.gz').read_bytes()).hexdigest(),'full4096_trials_checked':6,'partial_and128_crosskernel_checks':True,'own_Fiat_and9024_fullstate_MR_markers_checked':True,'exact_source_differences_only_frozen_candidate_and_certificate_bindings':True,'binary_unchanged_across_driver_correction':True,'not_a_search_authorization_or_benchmark_record':True}
(new/'ROOT_RUNTIME_VERIFIED.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
