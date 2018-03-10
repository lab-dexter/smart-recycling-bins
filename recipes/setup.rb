#
# Cookbook:: smart-recycling-bins
# Recipe:: setup
#
# Copyright:: 2018, The Authors, All Rights Reserved.

service 'ssh' do
  action [:enable, :start]
end

apt_update 'Update the apt cache daily' do
  frequency 86_400
  action :periodic
end

package %w(git vim)

# Starting application deployment
directory '/home/pi/smart-recycling-bins-app/smart-recycling-bins' do
  recursive true
end

# Installing python dependencies
python_runtime '2'

python_virtualenv '/home/pi/smart-recycling-bins-app/srb'

remote_file '/home/pi/smart-recycling-bins-app/requirements.txt' do
  source 'https://raw.githubusercontent.com/lab-dexter/smart-recycling-bins/master/config/requirements.txt'
  action :create
end

pip_requirements '/home/pi/smart-recycling-bins-app/requirements.txt'