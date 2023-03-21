#!/bin/bash

name="rigify_gamerig_extension"
version="_release_002"
dirpath=$(pwd)
dirpath=${dirpath:-/}
dirname="${dirpath##*/}"
echo $dirname

zipcmd() {
    zip -r $dirname/$name$version.zip $dirname \
    -x "__MAXOSX/*" -x "*.DS_Store" \
    -x "*venv*" -x "*.idea*" -x "*.git*" \
    -x "*__pycache__*" -x "*docs*" -x "*setup*" \
    -x "*swp", -x "*test*"
}

cd ..
echo $(zipcmd)
# zipcmd
# cd $name
