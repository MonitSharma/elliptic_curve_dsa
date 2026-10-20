from pathlib import Path
import hashlib,json
def sha(p):
 with p.open("rb")as source:return hashlib.file_digest(source,"sha256").hexdigest()
def verify_search(sr):
 expected=1;total=0;passes=[]
 for prefix in sr['prefixes']:
  path=Path(prefix['path']);assert prefix['first']==expected and sha(path)==prefix['sha256'];seen=bytearray(prefix['screens']);found=[]
  with path.open()as inp:
   for line in inp:
    row=json.loads(line);k=row['nonce'];i=k-expected;assert 0<=i<len(seen)and not seen[i];seen[i]=1;assert row['rejection_policy']=='exact_full_state_only'
    if row['pass']:found.append(k)
  assert all(seen)and sorted(found)==prefix['passes'];assert prefix['highest']==expected+len(seen)-1;expected=prefix['highest']+1;total+=len(seen);passes.extend(found)
 assert total==sr['production_screens']and expected-1==sr['highest_screened'];assert passes and min(passes)==sr['selected_nonce'];return sorted(passes)
