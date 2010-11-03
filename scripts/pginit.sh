#!/bin/sh

dbname=$1
pgdir=$2

if [ "$pgdir" = "" ]; then
    sudo -u postgres dropdb $dbname
    sudo -u postgres createdb $dbname
    sudo -u postgres dropuser $dbname
    sudo -u postgres createuser $dbname -s
else
    sudo -u postgres $pgdir/dropdb $dbname
    sudo -u postgres $pgdir/createdb $dbname
    sudo -u postgres $pgdir/dropuser $dbname
    sudo -u postgres $pgdir/createuser $dbname -s
fi
python manage.py syncdb

