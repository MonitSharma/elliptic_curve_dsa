"""Instrument the external paired diagnostic with source-bound failure families."""
from pathlib import Path
import runpy,sys
driver=Path(__file__).with_name('create-paired-replay.py')
runpy.run_path(str(driver),run_name='__main__')
dest=Path(sys.argv[2]).resolve()
p=dest/'src/main.rs';t=p.read_text()
t=t.replace('let curve=secp256k1();let mut packets=Vec::new();','let curve=secp256k1();let mut packets=Vec::new();let mut families=Vec::new();')
t=t.replace('packets.push([t.0,t.1,o.0,o.1,e.0,e.1]);','packets.push([t.0,t.1,o.0,o.1,e.0,e.1]);families.push(family);')
t=t.replace('for (batch,points) in packets.chunks(64).enumerate(){','let mut family_bad=std::collections::BTreeMap::new();\n for (batch,points) in packets.chunks(64).enumerate(){')
needle='left_bad+=usize::from(!good(&ls));right_bad+=usize::from(!good(&rs));'
new='''left_bad+=usize::from(!good(&ls));right_bad+=usize::from(!good(&rs));
    let family=families[batch*64+lane];let counts=family_bad.entry(family).or_insert((0usize,0usize,0usize));
    counts.0+=1;counts.1+=usize::from(!good(&ls));counts.2+=usize::from(!good(&rs));
    if !good(&ls)&&counts.1<=4 {
     println!("COUNTEREXAMPLE index={} family={family} target_x={:#x} target_y={:#x} offset_x={:#x} offset_y={:#x} expected_x={:#x} expected_y={:#x} got_x={:#x} got_y={:#x}",batch*64+lane,v[0],v[1],v[2],v[3],v[4],v[5],ls.get_register(&regs[0],lane),ls.get_register(&regs[1],lane));
    }'''
assert t.count(needle)==1;t=t.replace(needle,new)
t=t.replace('assert_eq!(mismatches,0,"exact transformation', 'println!("FAMILY_DIAGNOSTIC {family_bad:?}");\n assert_eq!(mismatches,0,"exact transformation')
p.write_text(t,newline='\n')
