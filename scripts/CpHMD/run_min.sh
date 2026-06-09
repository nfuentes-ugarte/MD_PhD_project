#!/bin/bash
export CUDA_VISIBLE_DEVICES="0"
pmemd.cuda_DPFP -O -i min.in -o min.out -p ../prep/HMPP_prot_cphmd.parm7 -c ../prep/HMPP_prot.rst7 -r HMPP_prot_min.rst7 > run.log
