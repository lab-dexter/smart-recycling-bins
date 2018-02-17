#!/bin/bash
#------------------------------------------------------------------------------------------
# This script syncs smart recycle bin application with remote repo contents 
# from target branch.
#
# Arguments accepted:
#   1 -> BRANCH - repo branch to synch with. Defaults to 'master' branch if not specified
#------------------------------------------------------------------------------------------
# User passed arguments:

BRANCH=${1:-"master"}

#------------------------------------------------------------------------------------------
# Parameters

PENV="srb"
DPKG_LIST="python-setuptools python-pip"
DEPLOY_FILE="app-sync.sh"
DEPLOYMENT_DIR="/home/pi/smart-recycling-bins-app"

# recycle-bin.service deployment variables
DIR="smart-recycling-bins"
SERVICE_FILE="recycle-bin.service"

#-----------------------------------------------------------------------------------------
# Functions

timestamp() {
  date "+%Y-%m-%d %H:%M:%S"
}

# 
# This function checks if local HEAD matches the upstream branch commit. 
# If commits differ, updates are pulled from remote.
#
check_repo_updates() {
  git --git-dir ${DEPLOYMENT_DIR}/${DIR}/.git fetch
  
  if [ "$(git --git-dir ${DEPLOYMENT_DIR}/${DIR}/.git rev-parse HEAD)" == "$(git --git-dir ${DEPLOYMENT_DIR}/${DIR}/.git rev-parse @{u})" ]; then
    echo "Current branch MATCHES upstream branch. Exiting...";
    app_sync_finish_msg
    exit 0
  else
    echo "Current branch does NOT MATCH upstream branch commit. Pulling...";
    git --git-dir ${DEPLOYMENT_DIR}/${DIR}/.git --work-tree ${DEPLOYMENT_DIR}/${DIR} pull
  fi  
}

app_sync_finish_msg() {
  echo "$(timestamp) : Finished deploying/updating smart-recycling-bins-app"
}

#
# Installs debian packages. Creates python virtual environment 
# named by ${PENV} parameter and installs required python packages
#
deploy_package_dependencies() {

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

}

#
# Copies over service files and restarts the service.
#
setup_service() {

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

  # Printing sync finish message
  app_sync_finish_msg

}
#-----------------------------------------------------------------------------------------
# Main script execution starts below

echo "============================================================================="
echo "$(timestamp) : Started deployment of ${DIR} software"
echo "============================================================================="
echo ""
echo " Target branch is: ${BRANCH}"
echo "-----------------------------------------------------------------------------"

check_repo_updates
deploy_package_dependencies
setup_service

