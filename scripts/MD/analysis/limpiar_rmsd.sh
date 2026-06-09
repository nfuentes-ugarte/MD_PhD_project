sed '/^#Frame/d' rmsd/rmsd_CA_rep*.dat | awk '{print $2}' > rmsd/rmsd_CA_all.dat
