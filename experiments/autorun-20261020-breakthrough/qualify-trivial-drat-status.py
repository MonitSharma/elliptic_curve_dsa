from pathlib import Path
import hashlib,json,subprocess
r=Path(__file__).resolve().parent;old=r.parent/'breakthrough-sat-proof-tools-v5-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();c=old/'tool-repos/drat-trim/drat-trim.c';checker=c.parent/'drat-trim';f=json.loads((old/'SOURCE-FREEZE.json').read_text());assert sha(c)==f['repositories']['drat-trim']['files']['drat-trim.c'];assert sha(checker)=='7c3a20e9d34bc78def63b4a05d9839dec3697d1e150e28def354adeec9ab716a'
text=c.read_text();assert 'else if  (parseReturnValue == UNSAT)'in text and 'int sts = ERROR;'in text and 'return (sts != UNSAT);'in text
cases={'trivial_zero_variables':'p cnf 0 1\n0\n','trivial_conflicting_units':'p cnf 1 2\n1 0\n-1 0\n','satisfiable_negative':'p cnf 1 1\n1 0\n'};results={}
for name,data in cases.items():
 cnf=r/(name+'.cnf');cnf.write_text(data);proof=r/(name+'.drat');proof.write_text('0\n')
 with(r/(name+'.log')).open('xb')as log:p=subprocess.run(['timeout','20',str(checker),str(cnf),str(proof)],stdout=log,stderr=subprocess.STDOUT)
 log=(r/(name+'.log')).read_text();results[name]={'exit':p.returncode,'trivial_unsat':'c trivial UNSAT'in log,'verified':'s VERIFIED'in log,'log_sha256':sha(r/(name+'.log'))}
 assert p.returncode==1
 if name=='satisfiable_negative':assert not results[name]['verified']and not results[name]['trivial_unsat']
 else:assert results[name]['verified']and results[name]['trivial_unsat']
result={'status':'PARSE_TIME_UNSAT_EXIT_STATUS_BEHAVIOR_QUALIFIED_WITH_POSITIVE_AND_NEGATIVE_CONTROLS','checker_source_sha256':sha(c),'checker_binary_sha256':sha(checker),'controls':results,'original_fixed_input_check_sha256':sha(r/'RESULT.json'),'scope':'Unchanged official checker leaves sts=ERROR when parseReturnValue is UNSAT, prints trivial UNSAT/s VERIFIED but returns1. Both trivial positivecontrols reproduce this; SAT+invalidproof also returns1 but never VERIFIED. Original RESULT.json preserves drat_checker_verified=false under earlier strict0 rule. Independent zero-variable CNF contradiction proof alreadyPASS. No old timeout/solver/gate verdict is upgraded, no nonce screened/rejected.'}
(r/'TRIVIAL-CHECKER-QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
