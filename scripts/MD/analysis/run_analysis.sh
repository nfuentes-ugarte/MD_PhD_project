#!/bin/bash
#SBATCH --job-name=MD_HMPPH_analysis
#SBATCH --partition=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=12
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --output=logs/MD_HMPPH_analysis_%j.out
#SBATCH --error=logs/MD_HMPPH_analysis_%j.err

set -euo pipefail

# =========================
# CONFIGURACIÓN
# =========================
SYSTEM="HMPPH"
MASK_PROT=":1-266"
MASK_RMSF=":1-266@CA,C,N,O"
N_REPS=4
NPROC="${SLURM_NTASKS:-12}"
PYTHON="python3.10"

mkdir -p logs

echo "===================================="
echo "Análisis MD sistema: $SYSTEM"
echo "Job ID: ${SLURM_JOB_ID:-local}"
echo "Nodo: ${SLURM_NODELIST:-local}"
echo "NPROC: $NPROC"
echo "===================================="

# =========================
# PREPARACIÓN
# =========================
bash scripts/prep.sh
bash scripts/gen_pdb_min.sh "$SYSTEM" "$MASK_PROT"

# =========================
# GENERAR INPUTS CPPTRAJ
# =========================
bash scripts/gen_analisis.sh "$SYSTEM" "$MASK_PROT" "$N_REPS"
bash scripts/gen_rmsf.sh "$SYSTEM" "$MASK_RMSF" "$MASK_RMSF" "$N_REPS"

# =========================
# EJECUTAR ANÁLISIS POR RÉPLICA
# =========================
cpptraj -i cpptraj_inputs/gen_pdb_min.in

# =========================
# EJECUTAR ANÁLISIS POR RÉPLICA
# =========================
cpptraj -i cpptraj_inputs/gen_pdb_min.in

for i in $(seq 1 "$N_REPS"); do
    echo "Ejecutando análisis réplica $i"
    mpirun -np "$NPROC" cpptraj.MPI -i "cpptraj_inputs/analysis_rep${i}.in"
done

for i in $(seq 1 "$N_REPS"); do
    echo "Ejecutando RMSF réplica $i"
    cpptraj -i "cpptraj_inputs/rmsf_rep${i}.in"
done

# =========================
# LIMPIEZA
# =========================
bash scripts/limpiar_rg.sh
bash scripts/limpiar_rmsd.sh

# =========================
# GRAFICAR
# =========================
$PYTHON scripts/plot_rg.py   -d rg/   --out "$SYSTEM"
$PYTHON scripts/plot_rmsd.py -d rmsd/ --out "$SYSTEM"
$PYTHON scripts/plot_rmsf.py -d rmsf/ --out "$SYSTEM"

echo "===================================="
echo "Análisis terminado correctamente"
echo "===================================="
