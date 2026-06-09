#!/bin/bash
export CUDA_VISIBLE_DEVICES="0"
pmemd.cuda -O -i run_nvt.in -o run_nvt.out -p ../prep/HMPP_prot_cphmd.parm7 -c ../0_min/HMPP_prot_min.rst7 -r HMPP_prot_NVT.ncrst -ref ../0_min/HMPP_prot_min.rst7 -x HMPP_prot_NVT.nc
