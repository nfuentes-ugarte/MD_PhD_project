#!/bin/bash

if [ $# -lt 4 ]; then
    echo "Uso: $0 <sistema> <mask_alineamiento> <mask_rmsf> <n_replicas>"
    echo "Ejemplo: $0 HMP :1-266@CA,C,N,O :1-266@CA,C,N,O 4"
    exit 1
fi

sys="$1"
align_mask="$2"
rmsf_mask="$3"
NREP="$4"

mkdir -p rmsf cpptraj_inputs

for i in $(seq 1 "$NREP"); do

cat > cpptraj_inputs/rmsf_rep${i}.in << EOF
parm ../prep/${sys}_prot.parm7
trajin ../3_prod/rep${i}_prod_autoimage.nc
center :1-269

rms first ${align_mask}
average crdset MyAvg
run
rms ref MyAvg ${align_mask}
atomicfluct out rmsf/rmsf_prot_rep${i}.dat ${rmsf_mask} byres
run
EOF

echo "Generado: cpptraj_inputs/rmsf_rep${i}.in"

done
