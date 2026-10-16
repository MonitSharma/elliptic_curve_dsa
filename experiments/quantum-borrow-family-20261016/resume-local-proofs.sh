#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/quantum-borrow-family-20261016
echo $$ >resume-local-proofs.pid
mkdir -p preserved-first-proof-count-check
cp local-quantum-proofs.log local-quantum-proofs.exit quantum-proofs.exit old-quantum-contract-0.* preserved-first-proof-count-check/
python3 run-local-quantum-proofs.py >local-quantum-proofs.log 2>&1
status=$?; echo $status >local-quantum-proofs.exit; echo $status >quantum-proofs.exit; exit "$status"
