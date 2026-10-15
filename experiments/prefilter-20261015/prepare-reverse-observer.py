from pathlib import Path
import subprocess,hashlib,json
root=Path('/home/hclau/ecdsa_research/prefilter-20261015')
base=root/'observer-tip/src/point_add'
p=base/'value_trace.rs';s=p.read_text()
assert 'MODEL_REV' not in s
needle='                            let rs=seen.entry((m.phase,"rev")).or_insert(vec![false;rows.len()]);'
assert s.count(needle)==1
s=s.replace(needle,'''                            for lane in 0..rows.len(){
                                eprintln!("MODEL_REV shot={} phase={} tick={} r0={:#x} r1={:#x}",batch*64+lane,m.phase,m.tick,vals[lane][0],vals[lane][1]);
                            }
'''+needle)
s=s.replace('pub fn run(ops:&[Op]){','''#[derive(Clone)]
struct PointMark{at:usize,stage:&'static str,regs:[Vec<QubitId>;2]}
static POINTS:Mutex<Vec<PointMark>>=Mutex::new(Vec::new());
pub fn point_mark(at:usize,stage:&'static str,x:&[QubitId],y:&[QubitId]){POINTS.lock().unwrap().push(PointMark{at,stage,regs:[x.to_vec(),y.to_vec()]});}
fn point_word(qs:&[QubitId],words:&[u64],lane:usize)->U256{let mut v=U256::ZERO;for(i,q)in qs.iter().enumerate(){if words[q.0 as usize]>>lane&1!=0{v|=U256::from(1)<<i;}}v}
pub fn run(ops:&[Op]){
    let point_marks=POINTS.lock().unwrap().clone();
''')
s=s.replace('let mut entry=Vec::<[U256;2]>::new();let mut cursor=0;','let mut entry=Vec::<[U256;2]>::new();let mut point_cursor=0;let mut cursor=0;')
needle='            sim.apply_observed(ops.iter(),|idx,s,_,_|{'
assert s.count(needle)==1
s=s.replace(needle,needle+'''
                while point_cursor<point_marks.len()&&point_marks[point_cursor].at==idx{
                    let mark=&point_marks[point_cursor];point_cursor+=1;
                    for lane in 0..rows.len(){eprintln!("POINT_OBS shot={} stage={} x={:#x} y={:#x}",batch*64+lane,mark.stage,point_word(&mark.regs[0],&s.qubits,lane),point_word(&mark.regs[1],&s.qubits,lane));}
                }
''')
p.write_text(s)
p=base/'mod.rs';s=p.read_text()
needle='        if seams { leapfrog::divide_seamed(circ, y, x, ox); } else { leapfrog::divide(circ, y, x); }'
assert s.count(needle)==1
s=s.replace(needle,needle+'\n        value_trace::point_mark(circ.op_count(),"after_divide",x,y);')
needle='        if seams { leapfrog::multiply_seamed(circ, y, x, ox); } else { leapfrog::multiply(circ, y, x); }'
assert s.count(needle)==1
s=s.replace(needle,'        value_trace::point_mark(circ.op_count(),"after_square",x,y);\n'+needle+'\n        value_trace::point_mark(circ.op_count(),"after_multiply",x,y);')
p.write_text(s)
tip=Path('/home/hclau/ecdsa_research/product-exact-20261015/tip')
patch=subprocess.run(['diff','-ruN',str(tip/'src'),str(root/'observer-tip/src')],capture_output=True).stdout
(root/'evidence/observer-reverse.patch').write_bytes(patch)
(root/'evidence/observer-reverse.patch.sha256').write_text(hashlib.sha256(patch).hexdigest()+'\n')
print('Reverse and coordinate boundary observer prepared')
