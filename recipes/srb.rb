#
# Cookbook:: smart-recycling-bins
# Recipe:: srb
#
# Copyright:: 2018, The Authors, All Rights Reserved.

# Setting up the service
# TODO: Use file from cookbook itself rather than pulling from github?
remote_file node['app']['py-app-dest'] do
  source node['app']['py-app-source']
  action :create
end

template node['app']['service-dest'] do
  source 'recycle-bin.service.erb'
  variables(
    python_venv: node['app']['python-venv-dir'],
    py_app_dest: node['app']['py-app-dest']
  )
  action :create
end

systemd_unit 'recycle-bin.service' do
  triggers_reload true
  action [:reload_or_restart, :enable]
end