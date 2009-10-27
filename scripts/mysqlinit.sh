#!/bin/sh

dbname=$1
mysqladmin --password='password' -f drop $dbname
mysqladmin --password='password' -f create $dbname
mysql --password='password' -e "drop user $dbname ; "
mysql --password='password' -e "create user $dbname identified by '$dbname' ; "
mysql --password='password' -e "grant all on $dbname.* to '$dbname'@'localhost' ; "
djpython manage.py syncdb
