#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

function error(){
    echo -e "\n${RED}Failed to Create GNU Radio Module${NC}\n"
    exit 1
}

trap error ERR

MODULE_NAME=xm_module
PYTHON_VERSION="3.12"
cd code
sudo rm -rf "gr-${MODULE_NAME}"
gr_modtool newmod $MODULE_NAME
yamlFiles=$(ls *.block.yml)
cd "gr-${MODULE_NAME}"
for file in $yamlFiles; do
    blockName=$(echo $file | sed "s/${MODULE_NAME}_//" | sed 's/\.block\.yml//')
    # Use default argument values
    gr_modtool add ${blockName} -t general -l python --copyright None --argument-list "" --add-python-qa
    cp "../${file}" "grc/${file}"
    pyFile="${blockName}.py"
    cp "../${pyFile}" "python/${MODULE_NAME}/${pyFile}"
done
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig
cd ../..
for file in $yamlFiles; do
    pyFile=$(echo $file | sed "s/${MODULE_NAME}_//" | sed 's/\.block\.yml/.py/')
    sudo cp $pyFile "/usr/local/lib/python${PYTHON_VERSION}/dist-packages/gnuradio/xm_module/$pyFile"
done

echo -e "\n${GREEN}Successfully Created GNU Radio Module${NC}\n"
