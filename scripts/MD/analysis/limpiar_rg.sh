#!/bin/bash
sed '/^#Frame/d' rg/radgyr_rep*.dat | awk '{print $2}' > rg/radgyr_all.dat
