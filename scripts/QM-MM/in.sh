#!/bin/bash
rm -f group_file
for i in `seq 1 $1`; do
    sed "s/XXXXX/$RANDOM/g" in > $i.in

    echo "-O -rem 0 -i $i.in -o $i.out -c $i.rst -r $i.rst -x $i.nc -inf $i.mdinfo -p HMPPH_prot_deut.parm7" >> group_file
done

echo "N REPLICAS = $i"
echo " Done."
