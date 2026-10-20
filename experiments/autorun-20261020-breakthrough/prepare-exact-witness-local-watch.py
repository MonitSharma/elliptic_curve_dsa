from pathlib import Path
import ast
a=Path(__file__).parent
s=(a/'collect-depth12-final.py').read_text().replace('breakthrough-depth12-final-20261020','breakthrough-exact-witness-final-20261020').replace('final depth12','final exactwitness');s=s.replace("sha((r/'final-evidence.tar.gz').read_bytes())","hashlib.file_digest((r/'final-evidence.tar.gz').open('rb'),'sha256').hexdigest()");ast.parse(s);(a/'collect-exact-witness-final.py').write_text(s)
s=(a/'watch-product-best-local.py').read_text().replace('breakthrough-public-best-drop-final-20261020','breakthrough-exact-witness-final-20261020').replace('collect-product-best-final.py','collect-exact-witness-final.py').replace("receipt['source_files']==177","receipt['source_files']==205").replace('Final benchmark/packaging failed; preserve evidence and inspect, no upload','Verification pipeline stopped; preserve gate/benchmark/packaging evidence and inspect before any upload').replace('fresh public product comparison','fresh public independentToffoli comparison');ast.parse(s);(a/'watch-exact-witness-local.py').write_text(s)
print('Independent local205-source/member verification and one-shot user-authorized uploader prepared.')
