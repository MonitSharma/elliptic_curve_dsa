"""Copy frozen v2 research source and change only explicit table-branch plumbing."""
from pathlib import Path
import difflib,hashlib,json,shutil,tarfile
root=Path(__file__).resolve().parents[2];ex=root/'experiments';old=ex/'breakthrough-public1829-width-port-local-v2-20261020';r=ex/'breakthrough-public1829-width-port-local-v4-20261020';r.mkdir(exist_ok=False);t=r/'observer';t.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest();f=json.loads((old/'SOURCE-FREEZE.json').read_bytes())
for rel,h in {**f['source_files'],**f['protected_files']}.items():
 data=(old/'observer'/rel).read_bytes();assert sha(data)==h,rel;p=t/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
p=t/'src/point_add/stream_edits.rs';raw=p.read_bytes();needle=b'pub(super) fn run(mut v:Vec<Op>)->Vec<Op>{';assert raw.count(needle)==1;raw=raw.replace(needle,b'pub(super) fn run(mut v:Vec<Op>,resource_changed:bool)->Vec<Op>{');needle=b'if std::env::var("STACK_WIDTH_RESEARCH").is_ok_and(|s|s!="public"){';assert raw.count(needle)==1;raw=raw.replace(needle,b'if resource_changed{');p.write_bytes(raw)
p=t/'src/point_add/mod.rs';raw=p.read_bytes();needle=b'ops = stream_edits::run(ops);';assert raw.count(needle)==1;raw=raw.replace(needle,b'ops = stream_edits::run(ops,config.is_some());');p.write_bytes(raw)
for n in ['.gitattributes','.gitignore','additional-tests.rs','phase-compare-compact.rs','drop-policy-tests.rs','ported-native-tests.rs','run.py']:shutil.copyfile(old/n,r/n)
stats=r/'stats-tool';stats.mkdir()
for n in ['Cargo.toml','Cargo.lock','stats.rs','io.rs']:shutil.copyfile(old/'stats-tool'/n,stats/n)
original={}
with tarfile.open(ex/'breakthrough-public1829-reproduction-20261020/point-add-source.tar.gz')as archive:
 for m in archive.getmembers():original[m.name]=archive.extractfile(m).read()
patch=[]
for p in sorted((t/'src/point_add').rglob('*')):
 if p.is_file():
  rel=p.relative_to(t).as_posix();before=original.get(rel,b'');after=p.read_bytes()
  if before!=after:patch.extend(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
(r/'source.patch').write_text(''.join(patch));f.update(source_files={p.relative_to(t).as_posix():sha(p.read_bytes())for p in(t/'src/point_add').rglob('*')if p.is_file()},scope=f['scope']+' Corrected explicit bool parameter selects uncached research branch after clear_process_env; no inherited process selector is read. Publicfalse path retains every original boundtable. Originalv2 hashguard failures preserved.',previous_frozen_source_sha256=sha((old/'SOURCE-FREEZE.json').read_bytes()));(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
(r/'prepare.py').write_text('''import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE-FREEZE.json').read_text());assert all(hashlib.sha256((r/'observer'/p).read_bytes()).hexdigest()==h for p,h in {**f['source_files'],**f['protected_files']}.items())
''')
for n in ['run-local.sh','launch-local.sh']:(r/n).write_bytes((old/n).read_text().replace(old.name,r.name).encode())
(r/'PLAN.md').write_text((old/'PLAN.md').read_text()+'''\nV4 corrects the research selector: constructor clears EVERY process variable,
so v2 stream_edits env check did not see STACK_WIDTH_RESEARCH and preserved
hash guards correctly stopped variants. Pass config.is_some() as an explicit
bool to stream_edits; unchanged public mode passesfalse. No hash guards changed
or silenced. Source/17protected copies checked against frozen failedv2 before
this plumbing change, fullpatch against originalpublic recorded. Repeat native9
and exact public bytecontrol before fresh variants. Prior failures stay final.
''')
partial=ex/'breakthrough-public1829-width-port-local-v3-20261020';(partial/'.gitignore').write_text('observer/\n');(partial/'SETUP-FAILURE.txt').write_text('Nested preparation stopped before research source changes because the upstream generator failed its replacement assertion and did not create server-v2 setup files. Partial verified public source retained, no native/input tests. V4 copies frozenv2 and patches direct bool plumbing explicitly.\n')
print(r.name,'explicit selector frozen')
