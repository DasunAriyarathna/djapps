#!/bin/sh

dbname=$1
pgdir=$2

if [ "$pgdir" = "" ]; then
    sudo -u postgres -i dropdb -w $dbname
    sudo -u postgres -i createdb -w $dbname
    sudo -u postgres -i dropuser -w $dbname
    sudo -u postgres -i createuser -w $dbname -s
else
    sudo -u postgres -i $pgdir/dropdb -w  $dbname
    sudo -u postgres -i $pgdir/createdb -w $dbname
    sudo -u postgres -i $pgdir/dropuser -w $dbname
    sudo -u postgres -i $pgdir/createuser -w $dbname -s
fi
echo "SERVER SOFTWARE HERE: $SERVER_SOFTWARE"
# python manage.py syncdb

