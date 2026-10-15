#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/mask-fusion-profile.pid
trap 'echo $? > evidence/mask-fusion-profile.exit' EXIT
free -m > evidence/mask-fusion-profile.resources
prlimit --as=1073741824 -- python3 profile-mask-fusion.py > evidence/mask-fusion-profile.log 2>&1
