from pathlib import Path
import ctypes, ctypes.util, hashlib, json, re, shutil, struct, subprocess, sys, tarfile, time

r=Path(__file__).resolve().parent
t=r/'candidate'
old=r.parent/'frozen-cache-table-20261016'
base='4b2ec52fc55da796aa8f5ef851290297e8706424'
archive_hash='e498096fe5be6296e2abf11dfaf2a6f38d1455b3a92bf07016b4149c750885b1'
old_stream_hash='180af069679ffa33b099b200d3337d6fc6c20a451a72508a40dea6617150dc64'
prefix_hash='24027e53f377f24195d290b5d343c519156cfa3ae45f64529def428a901f8480'
nonce=47449113
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,x): (r/name).write_text(json.dumps(x,indent=2)+'\n')
def git(*args): return subprocess.check_output(['git','-C',str(t),*args])
def protected():
    out={}
    for p in git('ls-files').decode().splitlines():
        if p.startswith('src/point_add/'): continue
        data=(t/p).read_bytes(); assert data==git('show','HEAD:'+p),p
        out[p]=sha(t/p)
    assert len(out)==17,len(out)
    return out
def recheck():
    f=json.loads((r/'SOURCE_FREEZE.json').read_text())
    for p,h in f['source_files'].items(): assert sha(t/p)==h,p
    assert protected()==f['protected_files']
    return f
def decode(p):
    d=Path(p).read_bytes(); assert d[:8]==b'QECCOPSZ'
    n=struct.unpack_from('<Q',d,8)[0]; assert n==14142629,n
    z=ctypes.CDLL(ctypes.util.find_library('zstd'))
    z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t]
    z.ZSTD_decompress.restype=ctypes.c_size_t
    out=ctypes.create_string_buffer(n*56); result=z.ZSTD_decompress(out,len(out),d[16:],len(d)-16)
    assert result==n*56,result
    return n,out.raw
def native_receipt():
    f=recheck()
    n,data=decode(t/'ops.bin')
    oldpath=r.parent/'product-exact-20261015/candidate-product-final25/ops.bin'
    assert sha(oldpath)==old_stream_hash
    _,prior=decode(oldpath)
    end=(n-96)*56
    assert data[:end]==prior[:end]
    assert hashlib.sha3_256(data[:end]).hexdigest()==prefix_hash
    absent=2**64-1
    for bit in range(48):
        expected=(6,absent,absent,(nonce>>bit)&1,absent,absent,absent)
        for pair in range(2): assert struct.unpack_from('<7Q',data,end+(2*bit+pair)*56)==expected
    result={'status':'NATIVE_SELECTED_NONCE_PREFIX_AND_TAIL_PASS','candidate_stream_sha256':sha(t/'ops.bin'),
       'old_stream_sha256':old_stream_hash,'ops':n,'pre_tail_ops':n-96,'pre_tail_sha3_256':prefix_hash,
       'pre_tail_byte_identical':True,'tail_ops':96,'tail_nonce':nonce,'tail_is_48_unconditional_xx_pairs':True,
       'source_freeze_sha256':sha(r/'SOURCE_FREEZE.json'),'protected_files':f['protected_files'],
       'loader_tests':4,'submission_mode':'queue'}
    save('NATIVE_RECEIPT.json',result); print(json.dumps(result),flush=True)
def prepare():
    auditor=r.parent/'product25-operational-20261016'
    assert (auditor/'terminal-audit.exit').read_text().strip()=='0'
    audit=json.loads((auditor/'ROOT_TERMINAL_AUDIT.json').read_text())
    assert audit['status']=='LOWEST_PASS_COMPLETE_JSONL_AUDIT_PASS'
    assert audit['lowest_full_protected_pass']==nonce
    assert sha(old/'point-add-source.tar.gz')==archive_hash
    assert not t.exists()
    shutil.copy2(old/'point-add-source.tar.gz',r/'original-point-add-source.tar.gz')
    shutil.copy2(auditor/'ROOT_TERMINAL_AUDIT.json',r/'SEARCH_AUDIT.json')
    shutil.copy2(auditor/'FINAL-CENSUS-PLAN.json',r/'FINAL-CENSUS-PLAN.json')
    subprocess.run(['git','-C',str(r.parent/'upstream'),'worktree','add','--detach',str(t),base],check=True)
    with tarfile.open(r/'original-point-add-source.tar.gz') as a:
        members=a.getmembers()
        assert all(m.isfile() and m.name.startswith('src/point_add/') and '..' not in Path(m.name).parts for m in members)
        a.extractall(t,filter='data')
    p=t/'src/point_add/mod.rs'; source=p.read_bytes()
    assert source.count(b'1046072871510')==1
    p.write_bytes(source.replace(b'1046072871510',str(nonce).encode()))
    assert sha(t/'src/point_add/frozen_cache25.bin')=='743286fef66ff31441bde0ef6ad9ad9c675b033d2fabc43b4b8a6d1e2379d49b'
    # Prove the selected nonce is the only difference from every archived source file.
    with tarfile.open(r/'original-point-add-source.tar.gz') as a:
        for m in a.getmembers():
            original=a.extractfile(m).read(); actual=(t/m.name).read_bytes()
            if m.name=='src/point_add/mod.rs': original=original.replace(b'1046072871510',str(nonce).encode())
            assert original==actual,m.name
    subprocess.run(['git','-C',str(t),'add','--intent-to-add','src/point_add'],check=True)
    (r/'candidate-source.patch').write_bytes(git('diff','--binary','HEAD','--','src/point_add'))
    files={str(p.relative_to(t)):sha(p) for p in sorted((t/'src/point_add').rglob('*')) if p.is_file()}
    with tarfile.open(r/'point-add-source.tar.gz','w:gz') as a:
        for p in files: a.add(t/p,arcname=p,recursive=False)
    save('SOURCE_FREEZE.json',{'status':'FROZEN_BEFORE_NATIVE_TESTS_AND_BENCHMARK','base_revision':base,
      'candidate':str(t),'nonce':nonce,'only_change_from_frozen_source':'TAIL_NONCE literal1046072871510 to47449113',
      'old_source_archive_sha256':archive_hash,'selected_source_archive_sha256':sha(r/'point-add-source.tar.gz'),
      'patch_sha256':sha(r/'candidate-source.patch'),'source_files':files,'protected_files':protected(),
      'search_audit_sha256':sha(r/'SEARCH_AUDIT.json'),'final_census_plan_sha256':sha(r/'FINAL-CENSUS-PLAN.json'),
      'old_stream_sha256':old_stream_hash,'expected_pre_tail_ops':14142533,'expected_pre_tail_sha3_256':prefix_hash,
      'submission_mode':'queue','census_owner':'root; no census launched here'})
    print('SOURCE_FREEZE_SHA256',sha(r/'SOURCE_FREEZE.json'),flush=True)
def benchmark():
    before=json.loads((r/'NATIVE_RECEIPT.json').read_text())
    native_receipt()
    after=json.loads((r/'NATIVE_RECEIPT.json').read_text()); assert before==after
    log=(r/'benchmark.log').read_text()
    for label,value in [('tested shots',9024),('classical mismatches',0),('phase-garbage batches',0),('ancilla-garbage batches',0)]:
        hits=re.findall(re.escape(label)+r'\s*:\s*(\d+)',log); assert hits==[str(value)],(label,hits)
    assert 'all 9024 shots OK' in log and '=== experiment OK ===' in log
    score=json.loads((t/'score.json').read_text()); assert set(score)=={'score','metrics'}
    assert set(score['metrics'])=={'toffoli','qubits'}
    q=score['metrics']['qubits']; tof=score['metrics']['toffoli']; assert q==1234 and score['score']==q*tof
    shutil.copy2(t/'score.json',r/'score.json'); shutil.copy2(t/'results.tsv',r/'results.tsv')
    save('BENCHMARK_RESULT.json',{'status':'UNCHANGED_BENCHMARK_PASS','candidate_stream_sha256':after['candidate_stream_sha256'],
      'qubits':q,'rounded_mean_toffoli':tof,'product':score['score'],'score_sha256':sha(r/'score.json'),
      'native_receipt_sha256':sha(r/'NATIVE_RECEIPT.json'),'source_freeze_sha256':sha(r/'SOURCE_FREEZE.json'),
      'benchmark_log_sha256':sha(r/'benchmark.log'),'tested_shots':9024,'classical_mismatches':0,
      'phase_garbage_batches':0,'ancilla_garbage_batches':0,'nonce':nonce,'submission_mode':'queue'})
    print((r/'BENCHMARK_RESULT.json').read_text(),flush=True)
if __name__=='__main__': {'prepare':prepare,'native':native_receipt,'benchmark':benchmark}[sys.argv[1]]()
