#!/bin/sh

dbname=$1
rm $dbname
python2.5 manage.py syncdb

