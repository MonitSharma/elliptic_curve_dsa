from pathlib import Path
import ast,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-public-acd0-reproduction-20261020';r=ex/'breakthrough-public1829-reproduction-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
s=(old/'run.py').read_text().replace('7499c902d7989e5a995ccd2331104a532197851b','3eefcf216ca37cba0ae3f56212d6b1302844a249').replace('acd0d88e-7445-4430-ba59-3c24c9bf4e0f','1829986e-675c-4fbf-bb28-22f2f95246c4').replace('756265','755314').replace('933231010','932057476').replace('EXACT_UNMODIFIED_PUBLIC_ACD0_BENCHMARK_REPRODUCED','EXACT_UNMODIFIED_PUBLIC1829_BENCHMARK_REPRODUCED')
s=s.replace("assert not t.exists();subprocess.run", "assert not t.exists();subprocess.run(['git','-C',str(ws/'toffoli'),'fetch','https://github.com/Layr-Labs/ecdsafail-challenge',revision],check=True);subprocess.run")
needle="historical=(t/'results.tsv').read_bytes();start=time.time();"
replacement="assert f['protected_files']==json.loads((ws/'breakthrough-public-acd0-reproduction-20261020/SOURCE-FREEZE.json').read_text())['protected_files'];subprocess.run(['cp','-a','--reflink=auto',str(ws/'breakthrough-public-acd0-reproduction-20261020/parent/target'),str(t/'target')],check=True);historical=(t/'results.tsv').read_bytes();start=time.time();"
assert s.count(needle)==1;s=s.replace(needle,replacement)
s=s.replace("with tarfile.open(r/'point-add-source.tar.gz'", "assert sha(t/'ops.bin')=='16567ee18910b8ee9f7aca60c33f0aa88df9679e6528fa5a7884e74e1a877baf'\n with tarfile.open(r/'point-add-source.tar.gz'")
ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Exact new public product-record reproduction before new research

Refresh19:54UTC: accepted1829986e/Q1234/T755314/product932057476,
source3eefcf216ca37cba0ae3f56212d6b1302844a249. Fetch official public Git objects,
separate detached worktree, verify EVERY source/protected blob, same17official
protected files as priorpublicacd0. Freeze before unchangedbenchmark.sh. Build
with2Cargo/1library threads and dedicatedlogs/PID; copiedtarget only cache, all
source/harness unchanged. Restorehistoricalresults aftersavingbenchmark evidence.
Requireall9024PASS, exactmetrics andpublishedstream16567ee1, archiveallsource.

No candidate, freshgate, nonce selection or score claim from oldreports. This
new source has new square cut-offs inherited from its public parent; do not
assume all mechanisms exact. Research should isolate exact sharedsum/reduction/
workspace/cache mechanisms and preserve allsource/stream bindings. Anynew
candidate needs its OWN declared finalgate against thisexact publicstream.
OldcandidatePASS vsacd0 remainsfinal butobsolete ascurrentproducttarget.
''');print(r)
