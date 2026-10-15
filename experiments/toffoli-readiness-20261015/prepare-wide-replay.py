from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
dest=Path(sys.argv[1])
subprocess.run([sys.executable,str(root/'prepare-replay.py'),str(dest)],check=True)
p=dest/'src/main.rs';s=p.read_text()
needle='assert_eq!(nq,rq);assert_eq!(regs,rregs);';assert s.count(needle)==1
s=s.replace(needle,'assert!(rq>=nq);assert_eq!(regs,rregs);')
needle='&&r.bits[nb as usize..].iter().all(|b|b&mask==0);';assert s.count(needle)==1
s=s.replace(needle,'&&r.bits[nb as usize..].iter().all(|b|b&mask==0)&&r.qubits[nq as usize..].iter().all(|q|q&mask==0);')
p.write_text(s)
