#
# Cookbook:: smart-recycling-bins
# Recipe:: setup
#
# Copyright:: 2018, The Authors, All Rights Reserved.

service 'ssh' do
  action [:enable, :start]
end

apt_update 'Update the apt cache daily' do
  frequency node['system']['update-period']
  action :periodic
end

package node['system']['packages']

# Starting application deployment
directory node['app']['dirs'] do
  recursive true
end

# Installing python dependencies
python_runtime node['app']['python-runtime']
python_virtualenv node['app']['python-venv-dir']

remote_file node['app']['python-requirements-dest'] do
  source node['app']['python-requirements-src'] 
  action :create
end

pip_requirements node['app']['python-requirements-dest']