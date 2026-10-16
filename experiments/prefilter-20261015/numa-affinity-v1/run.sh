#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015/numa-affinity-v1
echo $$ > run.pid
trap 'echo $? > run.exit' EXIT
if test "${NUMA_BUDGET_RELEASED:-}" != ROOT_RELEASED; then echo 'coordinator budget release required' >&2; exit 3; fi
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
numactl --hardware > topology.txt
numactl --show > parent-policy.txt
free -m > preflight-memory.txt
ps -eo pid,psr,nlwp,pcpu,rss,args --sort=-pcpu > preflight-processes.txt
timeout 600 /usr/bin/time -v prlimit --as=17179869184 -- python3 run.py > comparison.log 2> comparison.err
