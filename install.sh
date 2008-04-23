#!/bin/sh
#install.sh

# Installs *.py package by copying all .py files to install_dir. 

install_dir=${1}
if [ ${install_dir} ]; then
    current_dir=`pwd`
    cd ${install_dir}

    cp ${current_dir}/bmrb_chemical-shift-stats.txt .
    for script in `ls ${current_dir}/*.py`; do
        cp ${script} .
    done
else
    echo "No install directory specified.  Exiting."
    echo "    install.sh install_dir"
    exit
fi

