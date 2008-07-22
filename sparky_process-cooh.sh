#!/bin/bash
# sparky_process-cooh.sh

# Processes the raw data from COOH titrations using nmrpipe scripts.  This 
# assumes that the scripts have already been generated in each directory.

input_file=${1}
for x in `cat ${input_file}`; do
    echo ${x}
    cd spectra/${x}
    ./fid.com
    ipap_proc test.fid 4
    ./ipap_ft2.com
    pipe2ucsf total.ft2 ${x}_cbcgco.ucsf
    cd ../..
done
