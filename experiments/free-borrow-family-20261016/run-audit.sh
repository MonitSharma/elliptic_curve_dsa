#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/free-borrow-family-20261016
echo $$ >audit.pid
mv audit-affine.log audit-affine-first-option-parse-negative.log
mv audit-affine.exit audit-affine-first-wrapper-marker-negative.exit
cp audit-affine.py audit-affine-current.py
python3 audit-affine.py >audit-affine.log 2>&1
status=$?;echo "$status" >audit-affine.exit;exit "$status"
