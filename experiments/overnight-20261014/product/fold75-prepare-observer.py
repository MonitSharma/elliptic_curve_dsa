"""Read-only exact source producer snapshots around two implicated forward folds."""
from pathlib import Path
import subprocess,sys
base,output,evidence=map(Path,sys.argv[1:4])
subprocess.run([sys.executable,str(Path(__file__).with_name('prepare-body-boundaries-v2.py')),str(base),str(output),str(evidence)],check=True)
s=(base/'src/point_add/y15_onefold.rs').read_text()
def frame(label,sp2='0',cc='&[]',e='&[]',comp='false',open='false'):
 return f'    product_fold_frame(c,t,rev,"{label}",tg,b,s,k1,k2,{sp2},{cc},{e},{comp},{open});\n'
needle='    let (e_start, a_start) = (c.expected_total(), c.active_qubits());'
start=s.index('fn body(');end=s.index('/// y16-late: [`body`]',start);part=s[start:end];assert part.count(needle)==1
part=part.replace(needle,frame('entry')+needle)
needle='    let e_add2 = c.expected_total();';assert part.count(needle)==1
# All open ripple carries live here, and E sums are written immediately afterwards.
needle='    let room_now = cells::cap().saturating_sub(c.active_qubits() as usize);';assert part.count(needle)==1
part=part.replace(needle,frame('before-fold-producer','sp2','&cc','&[x256,x257,x258]','true','true')+needle)
needle='    let logf = y18_log();';assert part.count(needle)==1
part=part.replace(needle,needle+'\n'+frame('after-fold-producer','sp2','&cc','&[x256,x257,x258]','true','true'))
needle='    let e_end = c.expected_total();';assert part.count(needle)==1
part=part.replace(needle,frame('after-ripple-close')+needle)
s=s[:start]+part+s[end:]
s+=r'''
#[allow(clippy::too_many_arguments)]
fn product_fold_frame(c:&Builder,t:usize,rev:bool,label:&str,tg:&[QubitId],b:&[QubitId],s:[QubitId;3],k1:QubitId,k2:QubitId,sp2:usize,cc:&[QubitId],e:&[QubitId],comp:bool,open:bool){
 if rev || ![75,104].contains(&t){return;}
 use std::io::Write;let ids=|q:&[QubitId]|if q.is_empty(){"-".to_owned()}else{q.iter().map(|q|q.0.to_string()).collect::<Vec<_>>().join(",")};
 let mut file=std::fs::OpenOptions::new().append(true).create(true).open(PRODUCT_FOLD_PATH).unwrap();
 writeln!(file,"{label}\t{t}\t{}\t{}\t{}\t{}\t{sp2}\t{}\t{}\t{comp}\t{open}",c.op_count(),ids(tg),ids(b),ids(&[s[0],s[1],s[2],k1,k2]),ids(cc),ids(e)).unwrap();
}
'''
s+='\nconst PRODUCT_FOLD_PATH:&str="'+str((evidence/'fold-frames.tsv').resolve()).replace('\\','/')+'";\n'
(output/'y15_onefold.rs').write_text(s,newline='\n')
