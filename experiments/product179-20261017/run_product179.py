"""Run the separately declared fixed 124..179 continuation from the completed 123 endpoint."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/"product-to179-rank-20261017";plan=json.loads((d/"DECLARATION.json").read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=r/"product-to123-rank-20261017";assert (src/"launcher.exit").read_text().strip()=="0"
assert sha(r/plan["source_stage_declaration"])==plan["source_stage_declaration_sha256"]
lines=(src/"chain.manifest").read_text().splitlines();assert len(lines)==123
previous=r/lines[-1].split()[0];assert not (d/"chain.manifest").exists()
manifest=d/"chain.manifest";shutil.copy2(src/"chain.manifest",manifest)
(d/"INPUT_BINDING.json").write_text(json.dumps({"input_stream":str(previous.relative_to(r)),"input_sha256":sha(previous)},indent=2)+"\n")
env=os.environ.copy();env.update(RAYON_NUM_THREADS="1",OMP_NUM_THREADS="1")
for i,spec in enumerate(plan["stages"][123:],124):
    name=d/f"product-{i}-{spec[family]}-{spec[atom_cap]}-{spec[rank]}";output=Path(str(name)+".bin");log=Path(str(name)+"-generate.log")
    env.update(EXACT_MODE="cache-"+spec["family"],CACHE_ATOM_CAP=str(spec["atom_cap"]),ANF_PAIR_CAP="64",CACHE_PRODUCT_CAP="1000000",CACHE_SPLIT="1",CACHE_RANK=spec["rank"])
    with log.open("wb") as out:subprocess.run(["/usr/bin/time","-v",str(r/"target-flags/release/product_paired_diagnostic"),str(previous),str(output)],stdout=out,stderr=subprocess.STDOUT,env=env,check=True)
    mapping="=" if sha(output)==sha(previous) else str(log.relative_to(r))
    with manifest.open("a") as out:out.write(str(output.relative_to(r))+" "+mapping+"\n")
    with (d/"streams.sha256").open("a") as out:out.write(sha(output)+" "+str(output.relative_to(r))+"\n")
    previous=output
    if i in plan["checkpoints"]:
        checkpoint=d/f"stage-{i}.manifest";shutil.copy2(manifest,checkpoint)
        for packet in ["independent","structured"]:
            with (d/f"stage-{i}-{packet}.log").open("wb") as out:subprocess.run(["/usr/bin/time","-v",str(r/"target-anchored-replay/release/product_paired_diagnostic"),str(r/"tip/ops.bin"),str(previous),"+"+str(checkpoint),packet,str(d/f"stage-{i}-{packet}.tsv")],stdout=out,stderr=subprocess.STDOUT,env=env,check=True)
        with (d/f"stage-{i}-resources.jsonl").open("w") as out:subprocess.run(["python3",str(r/"stream_resources.py"),str(previous)],stdout=out,check=True)
print("FIXED179_GENERATION_AND_ALL_CHECKPOINTS_PASS",flush=True)
