# Filename: auto_setup.sh
# Auteur: Chao
# But: pour deployer automatiquement l'application de upload 
echo auto deployement de l\'application de upload
mkdir -p /tmp/upload
mkdir -p ~/environments/tutorial/
cp -avr ./upload_application ~/environments/tutorial/
install_dir=$(pwd)


# installation pip, pour faciliter l'installation suivant
echo "*************"
echo installer pip
echo "*************"
sudo apt-get install python-pip
echo "*************"
echo pip fin
echo "*************"


# installation virtualenv
echo "********************"
echo installer virtualenv
echo "********************"
pip install virtualenv
echo "********************"
echo virtualenv fin
echo "********************"


# installation ngnix
echo "********************"
echo installer ngnix
echo "********************"
sudo apt-get install nginx
echo "********************"
echo ngnix fin
echo "********************"


# configuration sur ngnix
sudo mkdir -p /etc/nginx/sites-available/tmp
sudo mv /etc/nginx/sites-available/default /etc/nginx/sites-available/tmp
sudo cp $install_dir/default /etc/nginx/sites-available/


# installation gunicorn
virtualenv ~/environments/tutorial/
echo "********************"
echo virtualenv fini
echo "********************"
cd ~/environments/tutorial/
cdir=$(pwd)


pwd
source bin/activate
echo "********************"
echo activate fini
echo "********************"

pip install gunicorn
echo First /test
cd upload_application 


# Installation de supervisor
sudo apt-get install supervisor
sudo echo [program\:upload_application] > /tmp/upload_application.conf 
sudo echo directory=$(pwd)>> /tmp/upload_application.conf
sudo echo command=$cdir\/bin\/gunicorn --bind=127.0.0.1\:8004 upload\:app  >> /tmp/upload_application.conf
sudo echo user=$USER >> /tmp/upload_application.conf
sudo echo autostart=\true >> /tmp/upload_application.conf
sudo echo autorestart=\true >> /tmp/upload_application.conf
sudo echo stdout_logfile=\/var\/log\/supervisor\/%\(program_name\)s_stdout.log >> /tmp/upload_application.conf
sudo echo stderr_logfile=\/var\/log\/supervisor\/%\(program_name\)s_stderr.log >> /tmp/upload_application.conf

# test 
cat /tmp/upload_application.conf

sudo cp /tmp/upload_application.conf /etc/supervisor/conf.d/
sudo rm /tmp/upload_application.conf
sudo supervisorctl update
sudo supervisorctl status
sudo /etc/init.d/nginx restart









