from pathlib import Path
import hashlib,json,re
root=Path(__file__).resolve().parent;parent='01aad987cfe03e7ca97df6f3dcd26085a21a5836aa6e661ec8fbd9c9c1b63740';out=[]
for cap in [1792,2048]:
 stream=root/f'cap{cap}/ops.bin';h=hashlib.sha256(stream.read_bytes()).hexdigest();log=(root/f'cap{cap}-generate.log').read_text()
 q=re.findall(r'peak[^\n]*?(\d+)',log)
 out.append({'cap':cap,'stream_sha256':h,'changed':h!=parent,'peak_diagnostic_matches':q[-5:],'status':'generated_not_scored'})
print(json.dumps({'parent_stream_sha256':parent,'candidates':out},indent=2))
