#!/bin/bash
#
# This is initial script for smart recycle bin software deployment. 
#


#======================================
# Deployment dependency variables
#======================================
PENV="srb"

#======================================
# recycle-bin.service deployment variables
#======================================
DIR="smart-recycling-bin"
SERVICE_FILE="recycle-bin.service"
#======================================

#======================================
DPKG_LIST=(python-setuptools)

echo "==================================================="
echo "Started deployment of ${DIR} software"
echo "==================================================="

rm -rf ./${DIR} && \
  echo "#----- Removed ./${DIR} directory -----#"
yes | git clone git@github.com:lab-dexter/smart-recycling-bins.git ${DIR}

echo "==================================================="
echo "Deploying dependency packages, etc."
echo "==================================================="
#
# TODO: Add debian package check/install for: python3-venv
for DPKG in $DPKG_LIST; do
  echo "Checking if $DPKG is installed..."
  if dpkg-query -W -f'${Status}' "${DPKG}" 2>/dev/null | grep -q "ok installed"; then 
    echo "...${DPKG} is INSTALLED";
  else
    echo "...${DPKG} NOT FOUND. Installing...";
    apt-get install ${DPKG} -y;
  fi
done
# e.g.: dpkg -l python3-venv | grep python3-venv 

source ${PENV}/bin/activate || \
  echo "Virtual python environment \'${PENV}\' not found. Creating..." && \
#  python3 -m venv ${PENV} && \
  virtualenv ${PENV}
  echo "==================================================="
  echo "Successfully created virtual python env: ${PENV}"
  echo "==================================================="

source ${PENV}/bin/activate
pip install -r "${DIR}/config/requirements.txt"

echo "==================================================="
echo "Setting up service related files"
echo "==================================================="
# chmod u+x "${DIR}/monitor.py"
sudo cp ${DIR}/${SERVICE_FILE} /lib/systemd/system/ && \
  echo "Copied over new service file"

sudo systemctl daemon-reload && \
  echo "Reloaded daemon config"

sudo systemctl enable ${SERVICE_FILE} && \
  echo "Enabled ${SERVICE_FILE} service"

sudo systemctl start ${SERVICE_FILE} && \
  echo "Started ${SERVICE_FILE} service"

