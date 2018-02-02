#!/bin/bash
#------------------------------------------------------------------------------------------
# This is initial script for smart recycle bin software deployment. 
# Arguments accepted:
#   1 -> BRANCH - repo branch to clone to. Defaults to 'master' branch if not specified
#------------------------------------------------------------------------------------------

BRANCH=${1:-"master"}

#------------------------------------------------------------------------------------------
# Parameters

PENV="srb"
DPKG_LIST="python-setuptools python-pip"

# recycle-bin.service deployment variables
DIR="smart-recycling-bin"
SERVICE_FILE="recycle-bin.service"
#--------------------------------------------------------

echo "==================================================="
echo "Started deployment of ${DIR} software"
echo "==================================================="
echo ""
echo "Target branch is: ${BRANCH}"
echo "---------------------------------------------------"

rm -rf ./${DIR} && \
  echo "Removed ./${DIR} directory"
git clone -b ${BRANCH} https://github.com/lab-dexter/smart-recycling-bins.git ${DIR}

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
/usr/bin/easy_install virtualenv

source ${PENV}/bin/activate || \
  echo "Virtual python environment \'${PENV}\' not found. Creating..." && \
#  python3 -m venv ${PENV} && \
  virtualenv ${PENV} && source ${PENV}/bin/activate

pip install -r "${DIR}/config/requirements.txt"

echo "==================================================="
echo " Setting up service related files"
echo "==================================================="
# chmod u+x "${DIR}/monitor.py"
sudo cp ${DIR}/${SERVICE_FILE} /lib/systemd/system/ && \
  echo "Copied over new service file"

sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_FILE} 
sudo systemctl start ${SERVICE_FILE} 
