#!/bin/bash
export CUDA_VISIBLE_DEVICES="0"
pmemd.cuda -O -i run_npt.in -o run_npt.out -p ../prep/HMP_prot_cphmd.parm7 -c ../1_equilnvt/HMP_prot_NVT.ncrst -r HMP_prot_NPT.ncrst -ref ../1_equilnvt/HMP_prot_NVT.ncrst -x HMP_prot_NPT.nc
