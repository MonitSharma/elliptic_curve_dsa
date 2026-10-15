# Width-adaptive dependency-mask evaluation

All four active widths pass exact reference comparison. This tool changes no
circuit and performs no nonce search. The original validated512-input kernel
is the reference;100random DAGs compare290,496,000 node/input values, plus output
roots and invalid port/kind/aux/child/root/capacity checks.

On frozen v3's7,914,981nodes, all512roots agree at64,128,256and512active inputs.
Three fixed evaluations take about27.1,27.5,34.2and55.9milliseconds respectively.
Each width packs its scratch workspace while input/output words retain the
eight-word ABI. Library SHA256
120dc358f57329e48cdd7bdf26e86ad47b0d84b07d4338227a086ed0c07562f2.
These are component timings; integrated throughput is measured separately.
Twelve archived artifacts independently verified locally.
