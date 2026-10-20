from pathlib import Path
import shutil,py_compile
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-native-context-finished-v2-20261020';r=root/'experiments/breakthrough-native-context-finished-v3-20261020';r.mkdir(exist_ok=False)
for p in['.gitattributes','.gitignore','PLAN.md','cache-tests.rs']:shutil.copyfile(old/p,r/p)
s=(old/'run.py').read_text();needle="for p in pfsource['source_files']:dest=t/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(parent/'candidate'/p,dest)";assert s.count(needle)==1;s=s.replace(needle,"for source_path in pfsource['source_files']:dest=t/source_path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(parent/'candidate'/source_path,dest)");(r/'run.py').write_text(s);py_compile.compile(str(r/'run.py'),doraise=True)
with(r/'PLAN.md').open('a')as out:out.write('\nAssembly correction: V1 andV2 both stopped before source freeze/compilation because the source-copy loop reused the proof-row variablep. V2 also corrected a latent u64/usize template conversion, but the actual earlier failure was assembly. V3 uses a distinctsource_path variable, leaving proof rows, source arithmetic and all prior evidence unchanged. Original failures remain.\n')
print(r)
