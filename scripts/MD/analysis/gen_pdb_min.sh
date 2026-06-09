#!/bin/bash

# =========================
# VALIDACIÓN DE INPUT
# =========================
if [ $# -lt 2 ]; then
    echo "Uso: $0 <sistema> <residuos>"
    echo "Ejemplo: $0 APO 1-266"
    exit 1
fi

# =========================
# CONFIGURACIÓN
# =========================
sys="$1"
res="$2"

mkdir -p estructura_min cpptraj_inputs

cat > cpptraj_inputs/gen_pdb_min.in << EOF
parm ../prep/${sys}_prot.parm7
trajin ../0_min/${sys}_prot_min.ncrst
strip "!(${res},267-269,276-279)"
trajout estructura_min/proteina_min_${sys}.pdb pdb
run
EOF

echo "Archivo generado: cpptraj_inputs/gen_pdb_min.in"
