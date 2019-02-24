#!/usr/bin/env bash

source_dir=/home/malte/Documents/WS201819/Bachelor/Midi/lmd_matched/$1
convert_dir=/home/malte/Documents/WS201819/Bachelor/Midi/lmd_matched_converted
dest_dir=/home/malte/Documents/WS201819/Bachelor/Midi/lmd_matched_mxl
wrong_dir=/home/malte/Documents/WS201819/Bachelor/Midi/erroneous_midi

while IFS= read -r -d '' dir; do
    name_mid=${dir##*lmd_matched/}
    full_dir=${name_mid%/*.mid}
    convert_location=${convert_dir}/${name_mid}
    name_mxl=${name_mid%.mid}.mxl
    dest_file=${dest_dir}/${name_mxl}
    wrong_location=${wrong_dir}/${name_mid}
    mkdir -p ${dest_dir}/${full_dir}
    mkdir -p ${convert_dir}/${full_dir}
    (musescore -o ${dest_file} ${dir} && mv ${dir} ${convert_location}) || echo "\n\n\nNOPE\n\n\n"

done < <(find "$source_dir" -name "*.mid" -print0)
