"""Port the exact new prefix after the unchanged fifteen-stage parent."""
from pathlib import Path,PurePosixPath
import ctypes,hashlib,json,shutil,struct,subprocess,tarfile,time
from ops_io import load,z
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((HERE/'PROOF_RESULT.json').read_text());assert proof['status']=='UNIVERSAL_PADDED_STAGE_PASS'
tree=HERE/'candidate';assert not tree.exists()
base='5a7c390233c72133df9b591c92e43422c5892142'
archive=ROOT/'wide15-record-20261016/evidence/final-point-add-source.tar.gz'
assert sha(archive)=='541ea5ee2026cd0a0cd01b8c73ef797dd1618c4b861fcd96bf7222dd4efac874'
before=dict(hostname=subprocess.check_output(['hostname'],text=True).strip(),
            base_head=subprocess.check_output(['git','-C',str(ROOT/'toffoli'),'rev-parse','HEAD'],text=True).strip(),
            base_branch=subprocess.check_output(['git','-C',str(ROOT/'toffoli'),'branch','--show-current'],text=True).strip(),
            base_status=subprocess.check_output(['git','-C',str(ROOT/'toffoli'),'status','--porcelain'],text=True))
assert before['hostname']=='LHC-104-070'
(HERE/'base-repository-state.json').write_text(json.dumps(before,indent=2)+'\n')
subprocess.run(['git','-C',str(ROOT/'toffoli'),'worktree','add','--detach',str(tree),base],check=True)
dest=tree/'src/point_add';parent_files={}
with tarfile.open(archive) as t:
    for member in t.getmembers():
        if member.isdir():continue
        p=PurePosixPath(member.name)
        assert member.isfile() and not p.is_absolute() and '..' not in p.parts
        assert p.parts[:2]==('src','point_add')
        raw=t.extractfile(member).read();out=tree/Path(*p.parts)
        out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw)
        parent_files[member.name]=hashlib.sha256(raw).hexdigest()
parent=ROOT/'wide15-record-20261016/evidence/final-ops.bin'
assert sha(parent)=='1d8c05eeee7b43dd694506b5efe963c771461b7e690bc62f409947b2306b7d77'
old=load(parent);new=load(HERE/'candidate.bin')
input_hash=hashlib.sha3_256(old[:-96*56]).hexdigest()
assert len(old)//56-96==10522659 and input_hash=='98414b12c1325bee9ffac8a0a4389c28ab80b7669be3c17d569934d37fa8dece'
assert len(new)//56==10523283 and old[-96*56:]==new[-96*56:]
none=2**64-1
for at in range(len(new)//56-96,len(new)//56,2):
    a=struct.unpack_from('<7Q',new,at*56);b=struct.unpack_from('<7Q',new,(at+1)*56)
    assert a==b and a[0]==6 and a[3]<=1 and all(a[i]==none for i in [1,2,4,5,6])
z.ZSTD_createCCtx.restype=ctypes.c_void_p
z.ZSTD_CCtx_setParameter.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int];z.ZSTD_CCtx_setParameter.restype=ctypes.c_size_t
z.ZSTD_compress2.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_compress2.restype=ctypes.c_size_t
z.ZSTD_freeCCtx.argtypes=[ctypes.c_void_p]
ctx=z.ZSTD_createCCtx();assert ctx
for key,val in [(100,19),(101,27)]:assert not z.ZSTD_isError(z.ZSTD_CCtx_setParameter(ctx,key,val))
buf=ctypes.create_string_buffer(z.ZSTD_compressBound(len(new)));started=time.monotonic()
size=z.ZSTD_compress2(ctx,buf,len(buf),new,len(new));assert not z.ZSTD_isError(size);z.ZSTD_freeCCtx(ctx)
blob=dest/'frozen_retained4096.bin';blob.write_bytes(b'QECCOPSZ'+struct.pack('<Q',10523283)+buf.raw[:size])
assert load(blob)==new
template=ROOT/'frozen-cache-table-20261016/frozen_cache.rs.in';text=template.read_text()
template_hash=sha(template)
for a,b in {'frozen_cache25':'frozen_retained4096','@INPUT_COUNT@':'10522659','@OUTPUT_COUNT@':'10523283',
            '@INPUT_SHA3@':input_hash,'@BLOB_SHA3@':hashlib.sha3_256(blob.read_bytes()).hexdigest()}.items():
    assert a in text;text=text.replace(a,b)
assert '@' not in text
(dest/'frozen_retained4096.rs').write_text(text)
mod=dest/'mod.rs';source=mod.read_text();needle='    let nonce: u64 = required_env("TAIL_NONCE");'
assert source.count(needle)==1
mod.write_text(source.replace(needle,'    ops = frozen_retained4096::run(ops);\n'+needle)+'\nmod frozen_retained4096;\n')
subprocess.run(['git','-C',str(tree),'add','--intent-to-add','src/point_add'],check=True)
changed=subprocess.check_output(['git','-C',str(tree),'diff','--name-only'],text=True).splitlines()
assert all(p.startswith('src/point_add/') for p in changed)
patch=subprocess.check_output(['git','-C',str(tree),'diff','--binary','HEAD','--','src/point_add'])
(HERE/'native-source.patch').write_bytes(patch)
protected={}
for rel in subprocess.check_output(['git','-C',str(tree),'ls-files'],text=True).splitlines():
    if rel.startswith('src/point_add/'):continue
    raw=(tree/rel).read_bytes();assert raw==subprocess.check_output(['git','-C',str(tree),'show','HEAD:'+rel])
    protected[rel]=hashlib.sha256(raw).hexdigest()
source_files={str(p.relative_to(tree)):sha(p) for p in dest.rglob('*') if p.is_file()}
freeze=dict(status='FULL_NATIVE_SOURCE_FROZEN_BEFORE_TEST_OR_GENERATION',base_revision=base,parent_source_archive_sha256=sha(archive),
            parent_source_files=parent_files,source_files=source_files,protected_files=protected,diff_paths=changed,
            template_sha256=template_hash,patch_sha256=sha(HERE/'native-source.patch'),blob_sha256=sha(blob),
            compression_seconds=time.monotonic()-started,input_prefix_ops=10522659,input_prefix_sha3_256=input_hash,
            expected_full_candidate_sha256=sha(HERE/'candidate.bin'),expected_canonical_sha256=hashlib.sha256(new).hexdigest(),
            expected_ops=10523283,expected_Q=1473,expected_B=3112,nonce644_is_inherited_not_searched=True,
            fixed_fresh_gate=json.loads((HERE/'DECLARATION.json').read_text())['prospective_fresh_gate'])
(HERE/'NATIVE_SOURCE_FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n')
print(json.dumps(dict(status=freeze['status'],source_files=len(source_files),protected_files=len(protected),blob_bytes=blob.stat().st_size)))
