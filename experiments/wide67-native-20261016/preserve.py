from pathlib import Path
import runpy
root=Path(__file__).resolve().parent
source=(root/'preserve-template.py').read_text().replace("dest=root/'product67'","dest=root/'wide67'")
source=source.replace("assert census['failure_gate_pass']","assert not census['failure_gate_pass']")
source=source.replace('COMPLETE_NATIVE_REPRODUCTION_AND_FRESH_FAILURE_GATE_PASS_PENDING_NONCE_BENCHMARK','COMPLETE_NATIVE_REPRODUCTION_FRESH_FAILURE_GATE_FAILED_NO_NONCE')
source=source.replace("'active_candidate_retained_for_qualification':True","'active_candidate_retained_pending_independent_source_archive_verification':True")
exec(compile(source,str(root/'preserve-template.py'),'exec'),{'__file__':str(root/'preserve-template.py')})
