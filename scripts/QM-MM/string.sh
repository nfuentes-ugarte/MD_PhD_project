#!/bin/bash
#SBATCH --job-name=PW_2I2
#SBATCH --output=%j.out
#SBATCH --error=%j.err
#SBATCH --ntasks=96
#SBATCH --cpus-per-task=1

module purge
module load oneapi/2025.0 mkl/2025.0 gcc/13.2 xtb/6.7.1 openmpi/4.1.6 amber/24
ulimit -s unlimited
export I_MPI_COMPATIBILITY=3

DIR=$(pwd)

rm -rf results
mkdir results

bash in.sh 96

srun sander.MPI -ng 96 -groupfile ${DIR}/group_file
