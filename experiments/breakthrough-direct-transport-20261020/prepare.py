import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-terminal-integration-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert not t.exists()and(old/'run.exit').read_text().strip()=='0';assert all(sha(old/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
ad=json.loads((old/'ADMISSION-RESULT.json').read_text());assert ad['cases'][1]['raw_sha256']=='40c3863db687abfb5895cfefc459f048b0d09a5cce883c120d2c464538e32cef'
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in(old/'observer/src/point_add').rglob('*'):
 if p.is_file():dest=t/p.relative_to(old/'observer');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
p=t/'src/point_add/width_composition.rs';raw=p.read_bytes();needle=b'    if c.current_phase()!="square"{return false;}';assert raw.count(needle)==1;raw=raw.replace(needle,b'    // Exact plain mapped chunk in any arithmetic phase; outer boundary callbacks stay intact.')
raw+=(r/'tests.rs').read_bytes();p.write_bytes(raw)
assert not(t/'target').exists();subprocess.run(['cp','-a','--reflink=auto',str(old/'observer/target'),str(t/'target')],check=True)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()},'caps':[1234,1233],'scope':'Extend already exact mapped chunk adapter to all arithmetic phases. Keep outer normal/deferred/recover/held/unheld boundary functions intact. Native allsmall parity maps+livecin/guards, allRNGpositions, inverse/recover/held roundtrips, deliberate omittedrecover fault, exactcomponentpeak controls before complete1234/1233 source generation. No finalgate/nonce/record.'},indent=2)+'\n')
