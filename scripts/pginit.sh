#!/bin/sh

dbname=$1
sudo -u postgres dropdb $dbname
sudo -u postgres createdb $dbname
sudo -u postgres dropuser $dbname
sudo -u postgres createuser $dbname -s
python2.5 manage.py syncdb

