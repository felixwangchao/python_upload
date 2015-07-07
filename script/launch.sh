# This script is not the setup script
# This is fot the test

supervisorctl stop all
sudo rm /var/log/supervisor/*
bash auto_setup.sh
supervisorctl start upload_application
gedit /var/log/supervisor/upload_application_stderr.log
