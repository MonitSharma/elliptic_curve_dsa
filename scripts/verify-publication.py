"""Check staged publication links and exact experiment evidence bytes."""
import hashlib
import json
import posixpath
from pathlib import Path
import re
import subprocess

def git(*args):
    return subprocess.check_output(["git",*args])

def main():
    tracked=set(git("ls-files").decode().splitlines())
    changed=git("diff","--cached","--name-only").decode().splitlines()
    assert not any(p.startswith(("agents/","experiments/q692-readiness-20261015/")) for p in changed)
    manifests={}
    wanted={p for p in changed if p.endswith(".md")}
    for folder in ["product-focus-20261015","toffoli-readiness-20261015"]:
        root=Path("experiments")/folder
        m=json.loads((root/"local-manifest.json").read_text(encoding="utf-8-sig"))
        manifests[folder]=m
        wanted.update((root/name).as_posix() for name in m["files"])
    patch="experiments/followup-20261015/bankswap-terminal/candidate-ht25-bankswap-v2.patch"
    wanted.add(patch);names=sorted(wanted)
    data=subprocess.run(["git","cat-file","--batch"],input="".join(":"+p+"\n" for p in names).encode(),
                        stdout=subprocess.PIPE,check=True).stdout
    blobs={};at=0
    for name in names:
        end=data.index(b"\n",at);header=data[at:end].split()
        assert len(header)==3 and header[1]==b"blob",(name,header)
        size=int(header[2]);blobs[name]=data[end+1:end+1+size];at=end+size+2
    missing=[]
    for name in changed:
        if not name.endswith(".md"):continue
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',blobs[name].decode("utf-8-sig")):
            if "://" in target or target.startswith("#"):continue
            target=target.split("#")[0].split(' "')[0]
            normalized=posixpath.normpath(posixpath.join(posixpath.dirname(name),target))
            if normalized not in tracked and not any(x.startswith(normalized+"/") for x in tracked):
                missing.append([name,target])
    assert not missing,missing
    checked={}
    for folder,m in manifests.items():
        for name,row in m["files"].items():
            p=(Path("experiments")/folder/name).as_posix()
            assert hashlib.sha256(blobs[p]).hexdigest()==row["sha256"],p
        checked[folder]=len(m["files"])
    receipt=json.loads(Path("experiments/verification-20261015/independent-verification.json").read_text())
    assert hashlib.sha256(blobs[patch]).hexdigest()==receipt["candidate_patch_sha256"]
    result=dict(status="PASS",staged_files=len(changed),missing_links=missing,
                exact_evidence_files=checked,q692_patch_matches=True,
                active_submodules_and_q692_work_excluded=True)
    print(json.dumps(result,indent=2))
    out=Path("research-output/publication-20261015/validation.json")
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+"\n")

if __name__=="__main__":main()
