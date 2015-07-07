# This script is not the setup script
# This is fot the test

supervisorctl stop upload_aplication
bash auto_setup.sh
supervisorctl start upload_application
