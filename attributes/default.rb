
# Setup prerequisites
default['system']['update-period'] = 86_400
default['system']['packages'] = %w(git vim)

default['app']['dirs'] = '/home/pi/smart-recycling-bins-app/smart-recycling-bins'
default['app']['python-runtime'] = '2'
default['app']['python-venv-dir'] = '/home/pi/smart-recycling-bins-app/srb'

default['app']['python-requirements-dest'] = '/home/pi/smart-recycling-bins-app/requirements.txt'
default['app']['python-requirements-src'] = 'https://raw.githubusercontent.com/lab-dexter/smart-recycling-bins/master/config/requirements.txt'

# SRB related config
default['app']['py-app-dest'] = '/home/pi/smart-recycling-bins-app/smart-recycling-bins/monitor.py'
default['app']['py-app-source'] = 'https://raw.githubusercontent.com/lab-dexter/smart-recycling-bins/master/monitor.py'

default['app']['service-dest'] = '/lib/systemd/system/recycle-bin.service'
default['app']['service-source'] = 'https://raw.githubusercontent.com/lab-dexter/smart-recycling-bins/master/recycle-bin.service'
