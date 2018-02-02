# smart-recycling-bins

## Setup a new RPI

```
mkdir /home/pi/smart-recycle-bins-app
cd /home/pi/smart-recycle-bins-app
git clone -b <TARGET_BRANCH> https://github.com/lab-dexter/smart-recycling-bins.git smart-recycling-bins-repo
cp ./smart-recycling-bins-repo/app-sync.sh ./
```

Add new cronjob to run app-sync.sh on the target branch each hour:
crontab -e

0 * * * * sudo /home/pi/smart-recycle-bins-app/app-sync.sh <TARGET_BRANCH> >> /home/pi/smart-recycle-bins-app/smart-recycle-bins-sync.log 


## recycle-bin service

```
# service file goes to /lib/systemd/system/
systemctl daemon-reload
systemctl recycle-bin.service
systemctl start recycle-bin.service
```
