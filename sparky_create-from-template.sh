#!/bin/bash
# sparky_create-from-template.sh

# Takes all pH values in input_file and generates a sparky file using a template
# sparky.save file.  All instances where the pH occurs should be changed to 
# REPLACE_PLEASE in the template file.

input_file=${1}
save_template_file=${2}

for x in `cat ${input_file}`; do
    cp ${save_template_file} ${x}_cbcgco.save
    sed -i "s/REPLACE_PLEASE/$x/g" ${x}_cbcgco.save
    mv ${x}_cbcgco.save sparky_save/
done


