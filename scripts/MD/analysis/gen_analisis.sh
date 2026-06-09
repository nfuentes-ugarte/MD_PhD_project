#!/bin/bash

# =========================
# VALIDACIÓN
# =========================
if [ $# -lt 3 ]; then
    echo "Uso: $0 <sistema> <mask_proteina> <n_replicas>"
    echo "Ejemplo: $0 APO :1-266 4"
    exit 1
fi

# =========================
# INPUT
# =========================
sys="$1"
prot="$2"
NREP="$3"

# =========================
# DIRECTORIOS
# =========================
mkdir -p rmsd rg sasa cpptraj_inputs

# =========================
# GENERACIÓN
# =========================
for i in $(seq 1 $NREP); do

cat > cpptraj_inputs/analysis_rep${i}.in << EOF
parm ../prep/${sys}_prot.parm7
trajin ../3_prod/rep${i}_prod_autoimage.nc
reference ../0_min/${sys}_prot_min.ncrst

# === RMSD ===
rms CA ${prot}@CA reference out rmsd/rmsd_CA_rep${i}.dat mass

# === Radio de giro ===
radgyr ${prot}@CA out rg/radgyr_rep${i}.dat


# === SASA ===
surf sasa_proteina ${prot} out sasa/sasa_proteina_cpptraj_rep${i}.dat

run
EOF

echo "Generado: cpptraj_inputs/analysis_rep${i}.in"

done
