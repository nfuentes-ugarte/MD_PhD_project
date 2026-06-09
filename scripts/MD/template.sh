#!/usr/bin/env bash
set -euo pipefail

PARM="../prep/HMPP_prot.parm7"
NREP=4

for i in $(seq 1 "$NREP"); do
  echo ">> rep$i"
cpptraj << EOF | tee "autoimage_rep${i}.log"
parm $PARM
trajin rep${i}_prod.nc
autoimage
trajout rep${i}_prod_autoimage.nc
go
EOF
done
