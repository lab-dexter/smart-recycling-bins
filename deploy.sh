#!/bin/bash

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


rm -rf ./${DIR} && \
  echo "----- Removed ./${DIR} directory -----"
yes | git clone git@github.com:lab-dexter/smart-recycling-bins.git ${DIR}

echo "===== Deploying dependency packages, etc. ====="
python3 -m venv ${PENV} && \
  echo "----- Successfully created virtual python env: ${PENV}"
source ${PENV}/bin/activate
pip install -r "${DIR}/requirements.txt"

# chmod u+x "${DIR}/monitor.py"

sudo cp ${DIR}/${SERVICE_FILE} /lib/systemd/system/ && \
  echo "----- Copied over new service file -----"

sudo systemctl daemon-reload && \
  echo "----- Reloaded daemon config -----"

sudo systemctl enable ${SERVICE_FILE} && \
  echo "----- Enabled ${SERVICE_FILE} service -----"

sudo systemctl start ${SERVICE_FILE} && \
  echo "----- Started ${SERVICE_FILE} service -----"

