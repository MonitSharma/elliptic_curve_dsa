#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/census-control-review-20261016
echo $$ >review.pid
{ hostname;date -Is;free -h;ps -eo pid,nlwp,pcpu,rss,args --sort=-pcpu | head -15; } >preflight.log
sha256sum ALL70.json ALL144.json inventory.py ../payload-model-20261016/before-census.bin ../product-exact-20261015/tip/ops.bin >before.sha256
/usr/bin/time -v python3 review-binding.py >review.log 2>&1
code=$?;echo "$code" >review.exit
sha256sum ALL70.json ALL144.json inventory.py ../payload-model-20261016/before-census.bin ../product-exact-20261015/tip/ops.bin >after.sha256
cmp before.sha256 after.sha256 || exit 91
exit "$code"
