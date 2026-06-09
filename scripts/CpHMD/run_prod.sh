#!/bin/bash
#SBATCH -J rep1
#SBATCH -p all
#SBATCH --gres=gpu:1
#SBATCH -n 1
#SBATCH -c 1
#SBATCH -o log_rep1.out
#SBATCH -e log_rep1.err

source /usr/local/amber24/amber.sh

pmemd.cuda -O -i run_nvt.in -o rep1.out -p ../prep/HMPP_prot_cphmd.parm7 -c ../2_equilnpt/rep1.ncrst -r rep1_prod.ncrst -x rep1_prod.nc -inf rep1.mdinfo -cpout rep1.cpout -cprestrt rep1.cprestrt -cpin ../prep/cpin 
