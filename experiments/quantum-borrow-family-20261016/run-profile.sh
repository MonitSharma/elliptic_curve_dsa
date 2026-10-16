#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/quantum-borrow-family-20261016
echo $$ >profile.pid
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -15; } >preflight.log
python3 test-classical-guards.py >guard-tests.log 2>&1
status=$?;echo "$status" >guard-tests.exit;[ "$status" = 0 ] || exit "$status"
python3 profile-families.py >profile.log 2>&1
status=$?;echo "$status" >profile.exit;exit "$status"
