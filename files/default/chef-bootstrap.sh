#!/bin/bash
#------------------------------------------------------------------------------------------
# This script performs initial RPI device bootstrap to hosted chef server.
#
# TODO: 
#   - Create a secure way to get place validator.pem. Possibly creating an RPI image.
#   - Initial run_list retrieval/creation
#   - ...

#------------------------------------------------------------------------------------------
# Parameters
ORG_NAME="dexter-lab-srb"

#------------------------------------------------------------------------------------------

apt-get update
apt-get install ruby ruby-dev -y
gem install chef

# Do some chef pre-work
/bin/mkdir -p /etc/chef
/bin/mkdir -p /var/lib/chef
/bin/mkdir -p /var/log/chef

# Empty run_list
cat > "/etc/chef/first-boot.json" << EOF
{
   "run_list" :[
     "role[smart-recycling-bins]"
   ]
}
EOF

NODE_NAME=rpi-$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 4 | head -n 1)

hostnamectl set-hostname ${NODE_NAME}

# Create client.rb
/bin/echo 'log_location     STDOUT' >> /etc/chef/client.rb
/bin/echo -e "chef_server_url  \"https://api.chef.io/organizations/${ORG_NAME}\"" >> /etc/chef/client.rb
/bin/echo -e "validation_client_name \"${ORG_NAME}-validator\"" >> /etc/chef/client.rb
/bin/echo -e "validation_key \"/etc/chef/${ORG_NAME}-validator.pem\"" >> /etc/chef/client.rb
/bin/echo -e "node_name  \"${NODE_NAME}\"" >> /etc/chef/client.rb

sudo chef-client -j /etc/chef/first-boot.json