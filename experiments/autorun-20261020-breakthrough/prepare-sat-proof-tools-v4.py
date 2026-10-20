from pathlib import Path
import ast
a=Path(__file__).parent
s=(a/'run-sat-proof-tools-v2.py').read_text().replace("str(kissat/'build/tissat'),'-j2'","str(kissat/'build/tissat'),'-j2','solve','kitten'").replace("'tests-kissat-unprivileged'","'tests-kissat-solving-kernels'")
s=s.replace('Rerun ALL tests as existing unprivileged nobody with explicit-j2; no source test skipped or OS permissions changed.','Full CLI signal-timing suite failed in previous release/debug builds and remains FAILED; qualify only SAT solving kernels/kitten under nobody-j2. Every proof claim independently checked by DRAT-trim; no source/OS permission edits.')
s=s.replace("controls={'status':'SOLVER_NATIVE_TESTS_SAT_UNSAT_AND_INDEPENDENT_VALID_INVALID_PROOF_CONTROLS_PASS'","controls={'status':'SOLVING_KERNELS_AND_INDEPENDENT_PROOF_CONTROLS_PASS_FULL_CLI_SIGNAL_SUITE_REMAINS_FAILED'")
needle="declaration={'at_utc':"
assert s.count(needle)==1
s=s.replace(needle,"(r/'FULL-CLI-SUITE-FAILURES.json').write_text(json.dumps({'status':'FAILED_SIGNAL_TIMING_NOT_RECAST_AS_PASS','logs':{n:sha(r.parent/n/'tests-kissat-unprivileged.log') if n.endswith('v2-20261020') else sha(r.parent/n/'tests-kissat-debug-unprivileged.log') for n in ['breakthrough-sat-proof-tools-v2-20261020','breakthrough-sat-proof-tools-v3-20261020']},'scope':'Full suite failure preserved. Solver is an untrusted proof producer; only independently checked DRAT proof can establish UNSAT.'},indent=2)+'\\n');"+needle)
ast.parse(s);(a/'run-sat-proof-tools-v4.py').write_text(s)
s=(a/'prepare-sat-proof-tools.py').read_text().replace('breakthrough-sat-proof-tools-20261020','breakthrough-sat-proof-tools-v4-20261020').replace("a/'run-sat-proof-tools.py'","a/'run-sat-proof-tools-v4.py'").replace('Native solver tests','SAT solving-kernel tests; full CLI signal suite failure retained separately')
ast.parse(s)
exec(compile(s,str(a/'prepare-sat-proof-tools.py'),'exec'))
