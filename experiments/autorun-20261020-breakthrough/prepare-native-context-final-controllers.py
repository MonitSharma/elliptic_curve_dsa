from pathlib import Path
import ast
root=Path(__file__).resolve().parents[2];ex=root/'experiments';oldprefix='breakthrough-native-both';newprefix='breakthrough-native-context';label='native-context499-exact-final-20261020-v1'
for suffix,filename in[('nonce','run.py'),('final','finalize.py'),('final','continue.py')]:
 r=ex/(newprefix+'-'+suffix+'-20261020');r.mkdir(exist_ok=True);assert not(r/filename).exists();s=(ex/(oldprefix+'-'+suffix+'-20261020')/filename).read_text()
 for tail in['-final-gate-20261020','-nonce-20261020','-final-20261020']:s=s.replace(oldprefix+tail,newprefix+tail)
 s=s.replace(oldprefix+'-finished-20261020',newprefix+'-finished-v3-20261020').replace('native-rail-g6-fixed-final-20261020-v1',label).replace('native_both_finished.rs','native_context_cache.rs').replace('FINISHED-RESULT.json','RESULT.json').replace("['native_stream_sha256']","['stream_sha256']")
 ast.parse(s);(r/filename).write_text(s);(r/'.gitattributes').write_text('* -text\n');(r/'.gitignore').write_text('candidate/\ntool/\n__pycache__/\n*resource-preflight*\npublic-before-upload.json\n')
print('Prepared qualifiednonce and unchangedbenchmark controllers; seal/local review still required before upload.')
