from pathlib import Path
import ast,shutil
root=Path(__file__).resolve().parents[2];old=root/'experiments/breakthrough-context-lease-final-20261020';r=root/'experiments/breakthrough-native-both-final-20261020';shutil.copyfile(old/'check-status.py',r/'check-status.py');s=(old/'verify-official-source.py').read_text();changes={'260b3ba0-d604-4f0d-9d55-934055d216b4':'d182a53e-be3d-4119-8298-303a9a9de07a',"{'qubits':1480,'toffoli':750705}":"{'qubits':1464,'toffoli':748691}",'1111043400':'1096083624','len(paths)==198':'len(paths)==200','d1f5e785f640fcf49a6af9b4a3b266c7aa3a61c3ef9387563c5ca6aadb9def9c':'cec71544f16da5598921a8a04e3b1416bda6f28d01878b1101ac724157a6f536',"'Q':1480,'T':750705":"'Q':1464,'T':748691","'improvement_in_T':206":"'improvement_in_T':2014"}
for a,b in changes.items():assert a in s,a;s=s.replace(a,b)
ast.parse(s);(r/'verify-official-source.py').write_text(s);print('Prepared official larger-result200/17 byte verification; no resubmission.')
