#!/bin/bash

dbname=$1
rootpassword=$2

mysql --user=root --password="$rootpassword" -e "drop user $dbname ; "
mysql --user=root --password="$rootpassword" -e "create user $dbname identified by '$dbname' ; "
mysqladmin --user=root --password="$rootpassword" -f drop $dbname
mysqladmin --user=root --password="$rootpassword" -f create $dbname
mysql --user=root --password="$rootpassword" -e "grant all privileges on $dbname.* to '$dbname'@'localhost' ; "
python2.5 manage.py syncdb
