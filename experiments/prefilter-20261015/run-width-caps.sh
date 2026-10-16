#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/width-caps.pid
trap 'echo $? > evidence/width-caps.exit' EXIT
bash run-width-affine-cap128.sh || exit $?
bash run-width-affine-cap512.sh || exit $?
