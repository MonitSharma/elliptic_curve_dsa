"""Constructive three-AND synthesis for the explicit seven-function escape."""
import argparse,hashlib,itertools,json,time
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import load

def description(net,closed):
    raw,targets,old=load(net);s=list(raw)
    for a,b in closed['gates']:s.append(combination(a,s)&combination(b,s))
    ss=Space(s);c1=old[15];c2=old[16]^c1;c3=old[17]^c2;r1=old[20]
    d=raw[2]^raw[11];L=(old[21]^r1)^((raw[1]^raw[10])&d)
    h=d^L;phi=[raw[3],raw[12],r1,h,raw[13],raw[14],raw[4]^c3]
    masks=[ss.express(v) for v in phi];assert all(mask is not None for mask in masks)
    F=((phi[4]|phi[5])&phi[6])
    for i,j in itertools.combinations(range(4),2):F^=phi[i]&phi[j]
    assert F==targets[3]^c3^raw[3]^raw[12]^L
    F7=0;rows=[]
    for row in range(128):
        a,n,r,h,k1,k2,v=[row>>i&1 for i in range(7)]
        original=r|(h<<1)|(a<<2)|(v<<3)|(r<<9)|(r<<10)|(n<<11)|(k1<<12)|(k2<<13)
        rows.append(original)
        assert sum((value>>original&1)<<i for i,value in enumerate(phi))==row
        F7|=(F>>original&1)<<row
    input7=[(1<<128)-1]+[sum((row>>i&1)<<row for row in range(128)) for i in range(7)]
    affine=Space(input7)
    restricted=[sum((value>>original&1)<<row for row,original in enumerate(rows)) for value in s]
    restricted_masks=[affine.express(value) for value in restricted]
    assert all(mask is not None for mask in restricted_masks)
    return {'status':'explicit_scalar_three_AND_description','source_lf_sha256':net['source_lf_sha256'],
            'scalar_input_order':['acc2','Nm2','R1','D+L','k1','k2','acc3+C3'],
            'scalar_identity':'OR(k1,k2)*v3 + e2(acc2,Nm2,R1,D+L)',
            'scalar_truth_hex':hex(F7),'scalar_truth_sha256':hashlib.sha256(F7.to_bytes(16,'little')).hexdigest(),
            'scalar_cases':128,'original_domain_rows':16384,'phi_affine_S23_masks':masks,
            'original_source_truth_sha256':hashlib.sha256(F.to_bytes(2048,'little')).hexdigest(),
            'restriction_original_rows':rows,'restriction_S23_affine_masks':restricted_masks,
            'seed_ANDs':closed['gates'],'qualified_score':None,
            'limits':'One scalar/restriction synthesis test. Full14-input constructor, producer admission, cleanup/phase/width and scored cost remain separate. The restriction is not claimed admitted by reduced genuineproducer domain.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('netlist',type=Path);p.add_argument('closed',type=Path)
    p.add_argument('--describe-only',action='store_true');p.add_argument('--seconds',type=int,default=600)
    p.add_argument('--query',type=Path);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    net=json.loads(args.netlist.read_bytes());closed=json.loads(args.closed.read_bytes());report=description(net,closed)
    report.update(netlist_sha256=hashlib.sha256(args.netlist.read_bytes()).hexdigest(),closed_receipt_sha256=hashlib.sha256(args.closed.read_bytes()).hexdigest())
    if args.describe_only:args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps({'status':report['status'],'scalar_cases':128,'restriction_affine':True}));return
    import z3
    def xor(values):
        value=z3.BoolVal(False)
        for v in values:value=z3.Xor(value,v)
        return value
    solver=z3.Solver();solver.set(timeout=args.seconds*1000)
    gates=[];values=[[z3.BoolVal(True)]+[z3.BoolVal(bool(row>>i&1)) for i in range(7)] for row in range(128)]
    for index in range(3):
        dimension=8+index
        a=[z3.BoolVal(False)]+[z3.Bool(f'a{index}_{i}') for i in range(1,dimension)]
        b=[z3.BoolVal(False)]+[z3.Bool(f'b{index}_{i}') for i in range(1,dimension)]
        gates.append((a,b))
        # Commutative factor symmetry only; no circuit topology is excluded.
        equal=z3.BoolVal(True);leq=z3.BoolVal(False)
        for i in reversed(range(1,dimension)):
            leq=z3.Or(leq,z3.And(equal,z3.Not(a[i]),b[i]));equal=z3.And(equal,a[i]==b[i])
        solver.add(z3.Or(leq,equal))
        for row in range(128):
            pa=xor([z3.And(coefficient,value) for coefficient,value in zip(a,values[row])])
            pb=xor([z3.And(coefficient,value) for coefficient,value in zip(b,values[row])])
            q=z3.Bool(f'g{index}_{row}');solver.add(q==z3.And(pa,pb));values[row].append(q)
    out=[z3.BoolVal(False)]+[z3.Bool(f'o{i}') for i in range(1,11)]
    truth=int(report['scalar_truth_hex'],16)
    for row in range(128):solver.add(xor([z3.And(coefficient,value) for coefficient,value in zip(out,values[row])])==bool(truth>>row&1))
    assert args.query is not None;args.query.write_bytes((solver.to_smt2()+'\n').encode())
    started=time.monotonic();status=solver.check()
    report.update(status=str(status),seconds=time.monotonic()-started,timeout_seconds=args.seconds,
                  query_sha256=hashlib.sha256(args.query.read_bytes()).hexdigest(),query_bytes=args.query.stat().st_size,
                  coefficient_variables=58,solver_version=z3.get_version_string(),solver_statistics=str(solver.statistics()),formal_proof_certificate_saved=False)
    if status==z3.sat:
        model=solver.model()
        def mask(values):return sum(int(z3.is_true(model.eval(v,model_completion=True)))<<i for i,v in enumerate(values))
        masks=[[mask(a),mask(b)] for a,b in gates];output=mask(out)
        raw7=[(1<<128)-1]+[sum((row>>i&1)<<row for row in range(128)) for i in range(7)];replay=list(raw7)
        for a,b in masks:replay.append(combination(a,replay)&combination(b,replay))
        assert combination(output,replay)==truth
        # Independently lift scalar operands into all original14-input rows.
        raw,targets,_=load(net);original=list(raw)
        for a,b in closed['gates']:original.append(combination(a,original)&combination(b,original))
        source_masks=[1]+report['phi_affine_S23_masks'];prefix=list(closed['gates'])
        for a,b in masks:
            aa=combination(a,source_masks);bb=combination(b,source_masks);prefix.append([aa,bb])
            original.append(combination(aa,original)&combination(bb,original));source_masks.append(1<<(len(original)-1))
        source_out=combination(output,source_masks)
        assert hashlib.sha256(combination(source_out,original).to_bytes(2048,'little')).hexdigest()==report['original_source_truth_sha256']
        desired=Space(raw+targets+original[-3:])
        report.update(scalar_ANDs=masks,scalar_output_mask=output,prefix_ANDs=prefix,source_output_mask=source_out,
                      scalar_cases_replayed=128,original_rows_replayed=16384,candidate_interface_rank=len(desired.values),value_AND_budget=len(desired.values)-15)
    elif status==z3.unknown:report['reason_unknown']=solver.reason_unknown()
    args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print(json.dumps({key:report[key] for key in ['status','seconds','query_sha256','query_bytes']}),flush=True)

if __name__=='__main__':main()
