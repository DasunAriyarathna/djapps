#!/bin/sh

dbname=$1
pgdir=$2

if [ "$pgdir" = "" ]; then
    sudo -u postgres -i dropdb $dbname
    sudo -u postgres -i createdb $dbname
    sudo -u postgres -i dropuser $dbname
    sudo -u postgres -i createuser $dbname -s
else
    sudo -u postgres -i $pgdir/dropdb $dbname
    sudo -u postgres -i $pgdir/createdb $dbname
    sudo -u postgres -i $pgdir/dropuser $dbname
    sudo -u postgres -i $pgdir/createuser $dbname -s
fi
python manage.py syncdb

