#
# Cookbook:: smart-recycling-bins
# Recipe:: srb
#
# Copyright:: 2018, The Authors, All Rights Reserved.

# Setting up the service

remote_file '/home/pi/smart-recycling-bins-app/smart-recycling-bins/monitor.py' do
  source 'https://raw.githubusercontent.com/lab-dexter/smart-recycling-bins/master/monitor.py'
  action :create
end

remote_file '/lib/systemd/system/recycle-bin.service' do
  source 'https://raw.githubusercontent.com/lab-dexter/smart-recycling-bins/master/recycle-bin.service'
  action :create
end

systemd_unit 'recycle-bin.service' do
  triggers_reload true
  action [:reload_or_restart, :enable]
end