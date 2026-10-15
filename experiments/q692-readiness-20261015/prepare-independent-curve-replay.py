"""Reuse the protected-simulator adapter on the independent valid curve pairs."""
from pathlib import Path
import hashlib,json,subprocess,sys
lib,dest=map(Path,sys.argv[1:3]);root=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(root/'prepare-fixed-replay-v9.py'),str(lib),str(dest)],check=True)
p=dest/'src/main.rs';s=p.read_text(encoding='utf8');assert s.count('let chosen=[2726usize,2913,3532];')==1
s=s.replace('let chosen=[2726usize,2913,3532];','''let chosen=[0usize,1,2];
 // Independently confirm the constructed coordinates with the protected curve reference.
 let curve=quantum_ecc::weierstrass_elliptic_curve::WeierstrassEllipticCurve{a:U256::ZERO,b:U256::from(7),modulus:U256::from_str_radix("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F",16).unwrap(),gx:U256::from_str_radix("79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798",16).unwrap(),gy:U256::from_str_radix("483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8",16).unwrap(),order:U256::from_str_radix("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141",16).unwrap()};
 for case in packets["packets"].as_array().unwrap(){let read=|group:&str,coord:usize|U256::from_str_radix(case[group][coord].as_str().unwrap(),16).unwrap();let got=curve.add(read("target",0),read("target",1),read("offset",0),read("offset",1));assert_eq!(got,(read("expected",0),read("expected",1)));}
''')
s=s.replace('fixed failing v6 inputs, independent measurement seed','independent valid curve counterexamples from the fixed 50000-input audit, protected curve reference checked, independent measurement seed');p.write_text(s,encoding='utf8')
binding=json.loads((dest/'source-binding.json').read_text(encoding='utf8'));binding['program_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();binding['scope']='All three retained independent policy failures constructed as valid curve points and checked against protected curve addition; diagnostic only.';(dest/'source-binding.json').write_text(json.dumps(binding,indent=2)+'\n',encoding='utf8')
