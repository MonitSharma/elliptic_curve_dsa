from pathlib import Path
root=Path(__file__).resolve().parent
s=(root.parent/'zero-payload-20261015/run-observer.sh').read_text().replace('/zero-payload-20261015','/equal-division-20261015').replace('prepare-observer.py','prepare.py')
(root/'run.sh').write_text(s,newline='\n')
s=(root.parent/'wide-phase-20261015/collect.py').read_text().replace("['origin.exit']","['observer.exit','fold.exit']").replace("['origin-b3']","['observer-b3','fold-b3']")
s=s.replace("assert (root/'origin-equality.log').read_text().strip()=='BYTE_IDENTICAL_STREAM=true'",'')
s=s.replace("'source_trace_byte_identical':True","'source_trace_byte_identical':False").replace("'HEO_TOTAL'","'HEO_TOTAL','DIVISION_INPUT','DIVISION_TICK','DIVISION_OUTPUT'")
s=s.replace('terminal gate-inert source observation; not a candidate benchmark','terminal raw arithmetic and fold-headroom probes; not a candidate benchmark')
s=s.replace('Allocator tests establish bookkeeping invariants, not quantum cleanliness; fixed replay checks dirty ancillas separately.','The raw control is probed with one denominator and four predeclared payloads. Both observers agree with the protected simulator, using all-zero outcomes; no full-point qualification follows.')
(root/'collect.py').write_text(s)
(root/'verify-local.py').write_text((root.parent/'wide-phase-20261015/verify-local.py').read_text())
