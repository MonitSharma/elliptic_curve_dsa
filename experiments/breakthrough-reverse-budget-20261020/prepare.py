import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-reverse-plan7-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert not t.exists() and (old/'run.exit').read_text().strip()=='0';assert all(sha(old/'observer'/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in (old/'observer/src/point_add').rglob('*'):
 if p.is_file():q=t/p.relative_to(old/'observer');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes()
def change(a,b):
 global raw
 assert raw.count(a)==1,(a,raw.count(a));raw=raw.replace(a,b)
change(b'let reverse7=at.0&&nbits==50&&drop>=2&&super::super::phase_fit::cap()<1233&&cells::cap()<1233;',b'let reverse7=at.0&&nbits==50&&min_budget==10&&drop<=2&&super::super::phase_fit::cap()<1233&&cells::cap()<1233;')
a=b'        if what=="reverse"&&nbits==50&&budget==7&&drop>=2&&super::super::phase_fit::cap()<1233{return(Y28_PLAN7.0.to_vec(),lean45,Y28_PLAN7.1.to_vec());}\n';assert raw.count(a)==1;raw=raw.replace(a,b'')
a=b'    if drop > 0 && merged_plan(nbits - 1, budget).is_none() && merged_plan(nbits, budget).is_none() {'
b=b'''    if what=="reverse"&&nbits==50&&(7..=9).contains(&budget)&&super::super::phase_fit::cap()<1233&&merged_plan(nbits-1,budget).is_none()&&merged_plan(nbits,budget).is_none(){
        let (p,d):(&[usize],&[usize])=match budget{7=>(&Y28_PLAN7.0,&Y28_PLAN7.1),8=>(&Y28_PLAN8.0,&Y28_PLAN8.1),_=>(&Y28_PLAN9.0,&Y28_PLAN9.1)};return(p.to_vec(),lean45,d.to_vec());
    }
'''+a;change(a,b)
start=raw.index(b'#[cfg(test)]mod reverse_plan7_tests{');region=raw[start:];raw=raw[:start]
for a,b in [(b'reverse_plan7_tests',b'reverse_budget_tests'),(b'fn build(inverse:bool)',b'fn build(budget:usize,inverse:bool)'),(b'1232-5-c.active_qubits()',b'1232-(budget-2)-c.active_qubits()'),(b'fold_plan_d(c,56,"reverse",2)',b'fold_plan_d(c,56,"reverse",9-budget)'),(b'assert_eq!(plan,Y28_PLAN7.0);assert_eq!(drops,Y28_PLAN7.1);',b'let(p,d):(&[usize],&[usize])=match budget{7=>(&Y28_PLAN7.0,&Y28_PLAN7.1),8=>(&Y28_PLAN8.0,&Y28_PLAN8.1),_=>(&Y28_PLAN9.0,&Y28_PLAN9.1)};assert_eq!(plan,p);assert_eq!(drops,d);'),(b'fn run(inverse:bool,',b'fn run(budget:usize,inverse:bool,'),(b'=build(inverse)',b'=build(budget,inverse)'),(b'for inverse in[false,true]{',b'for budget in 7..=9{for inverse in[false,true]{'),(b'run(inverse,',b'run(budget,inverse,'),(b'Some(p));}}}',b'Some(p));}}}}')]:assert a in region,a;region=region.replace(a,b)
raw+=region;p.write_bytes(raw);subprocess.run(['cp','-a','--reflink=auto',str(old/'observer/target'),str(t/'target')],check=True);assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
f['source_files']={p.relative_to(t).as_posix():sha(p)for p in (t/'src/point_add').rglob('*')if p.is_file()};f['scope']='Extend source-proven reverse preflight credit to old drop hints0/1/2 using exact carry budgets9/8/7 respectively, hard/walk<=1232,50bit only. Native controls now exercise all three planners with arbitrary affine/shared sources, everyguard, inverse andRNGtoggle. Original capacity assertions stay; new exact finite schedules replace unsupported layout only. Rename newtest module to avoid overlap with oldplan7 testfilter. No arithmeticcuts/windows/iterations/finalgate/nonce/score.';(r/'SOURCE_FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
