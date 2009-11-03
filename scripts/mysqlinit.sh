#!/bin/bash

dbname=$1
mysqladmin --user=mysql --password='password' -f drop $dbname
mysqladmin --user=mysql --password='password' -f create $dbname
mysql --user=mysql --password='password' -e "drop user $dbname ; "
mysql --user=mysql --password='password' -e "create user $dbname identified by '$dbname' ; "
mysql --user=mysql --password='password' -e "grant all on $dbname.* to '$dbname'@'localhost' ; "
python2.5 manage.py syncdb
