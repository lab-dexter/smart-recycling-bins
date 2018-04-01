#
# Cookbook:: smart-recycling-bins
# Recipe:: srb
#
# Copyright:: 2018, The Authors, All Rights Reserved.

# Setting up the service

remote_file node['app']['py-app-dest'] do
  source node['app']['py-app-source']
  action :create
end

remote_file node['app']['service-dest'] do
  source node['app']['service-source']
  action :create
end

systemd_unit 'recycle-bin.service' do
  triggers_reload true
  action [:reload_or_restart, :enable]
end