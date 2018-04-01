# smart-recycling-bins

## Setup a new RPI

```
wget https://raw.githubusercontent.com/lab-dexter/smart-recycling-bins/cm-poc/old/chef/chef-bootstrap.sh
chmod +x ./chef-bootstrap.sh
sudo ./chef-bootstrap.sh

echo <<< EOL
<VALIDATOR_KEY> # have be distributed manually atm>
EOL >> /etc/chef/dexter-lab-srb-validator.pem

sudo chef-client -j /etc/chef/first-boot.json
```

## HLD
![hld](https://github.com/lab-dexter/smart-recycling-bins/blob/cm-poc/images/srb-hld.png)

## Tooling

### Currently used:
* Configuration Management - [Chef](http://chef.io/). [Register to get free account here](http://manage.chef.io/).  
* IoT Solution Builder - [My Devices (a.k.a Cayenne)](https://mydevices.com/). 

### Envisioned to be used:

* Container Application Platform - [OpenShift](https://www.openshift.com/).
* API design/build/documentation tools - [Swagger](https://swagger.io/) / [Apiary](https://apiary.io/) / [StopLight](https://stoplight.io/)


