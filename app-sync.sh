#!/bin/bash
#------------------------------------------------------------------------------------------
# This is initial script for smart recycle bin software deployment. 
# Arguments accepted:
#   1 -> BRANCH - repo branch to clone to. Defaults to 'master' branch if not specified
#------------------------------------------------------------------------------------------
# User passed arguments:

BRANCH=${1:-"master"}

#------------------------------------------------------------------------------------------
# Parameters

PENV="srb"
DPKG_LIST="python-setuptools python-pip"
DEPLOY_FILE="app-sync.sh"
DEPLOYMENT_DIR="/home/pi/smart-recycle-bins-app"

# recycle-bin.service deployment variables
DIR="smart-recycling-bins-repo"
SERVICE_FILE="recycle-bin.service"
#-----------------------------------------------------------------------------------------
# Functions
timestamp() {
  date "+%Y-%m-%d %H:%M:%S"
}

#-----------------------------------------------------------------------------------------


echo "============================================================================="
echo "$(timestamp) : Started deployment of ${DIR} software"
echo "============================================================================="
echo ""
echo " Target branch is: ${BRANCH}"
echo "-----------------------------------------------------------------------------"

rm -rf ${DEPLOYMENT_DIR}/${DIR} && \
  echo "Removed ${DEPLOYMENT_DIR}/${DIR} directory"
git clone -b ${BRANCH} https://github.com/lab-dexter/smart-recycling-bins.git ${DEPLOYMENT_DIR}/${DIR}

echo "-----------------------------------------------------------------------------"
echo " Deploying dependency packages, etc."
echo "-----------------------------------------------------------------------------"
for DPKG in $DPKG_LIST; do
  echo "Checking if $DPKG is installed..."
  if dpkg-query -W -f'${Status}' "${DPKG}" 2>/dev/null | grep -q "ok installed"; then 
    echo "...${DPKG} is INSTALLED";
  else
    echo "...${DPKG} NOT FOUND. Installing...";
    apt-get install ${DPKG} -y;
  fi
done

# Simple checking if virtualenv is installed/available. Installing if not
virtualenv --version || /usr/bin/easy_install virtualenv

# Checking if python virtual environment is created
if [ ! -f "${DEPLOYMENT_DIR}/${PENV}/bin/activate" ]; then
  echo "Virtual python environment \"${DEPLOYMENT_DIR}/${PENV}\" not found. Creating..."
  virtualenv ${DEPLOYMENT_DIR}/${PENV}  
  source ${DEPLOYMENT_DIR}/${PENV}/bin/activate
else
  echo "Virtual python environment found."
  source ${DEPLOYMENT_DIR}/${PENV}/bin/activate
fi

pip install -r "${DEPLOYMENT_DIR}/${DIR}/config/requirements.txt"

echo "-----------------------------------------------------------------------------"
echo " Setting up service related files"
echo "-----------------------------------------------------------------------------"
# chmod u+x "${DIR}/monitor.py"
sudo cp ${DEPLOYMENT_DIR}/${DIR}/${SERVICE_FILE} /lib/systemd/system/ && \
  echo "Copied over new service file"
cp ${DEPLOYMENT_DIR}/${DIR}/${DEPLOY_FILE} ${DEPLOYMENT_DIR}/${DEPLOY_FILE} && \
  echo "Copied over new ${DEPLOY_FILE}"

sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_FILE} 
sudo systemctl start ${SERVICE_FILE} 
echo "$(timestamp) : Finished deploying/updating smart-recycle-bins"
