from pathlib import Path
import hashlib,json
r=Path(__file__).parent
expected='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
stream=r/'observer-tip/ops.bin'
digest=hashlib.sha256(stream.read_bytes()).hexdigest()
text=(r/'evidence/observer.log').read_text()
assert digest==expected
assert 'TRACE_SUMMARY family=audit shots=32 observer_equal=true score=NONE' in text
assert '\tExit status: 0' in text
report=dict(stream_sha256=digest,byte_identical_to_frozen_tip=True,observed_protected_all_state_equality=True,shots=32,observer_binary_exit=0,
            wrapper_note='Original observer wrapper trap used a relative exit-marker path after changing directories; generation, protected differential and hash check succeeded. Launcher corrected; this receipt independently verifies completed evidence.')
(r/'evidence/observer-validation.json').write_text(json.dumps(report,indent=2)+'\n')
(r/'evidence/observer-validation.exit').write_text('0\n')
print(json.dumps(report))
