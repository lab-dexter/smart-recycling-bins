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


