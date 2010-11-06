#!/bin/sh

cd $1
version=$2
ZIPNAME=django$version.zip
rm -Rf /tmp/django
cp -r django /tmp
cd /tmp
rm -Rf `find django/ | grep .svn`
zip -r $ZIPNAME django/__init__.py django/bin django/core \
       django/db django/dispatch django/forms \
       django/http django/middleware django/shortcuts \
       django/template django/templatetags \
       django/test django/utils django/views 
       # django/conf django/contrib
zip -r $ZIPNAME django/conf -x 'django/conf/locale/*'
zip -r $ZIPNAME django/contrib/__init__.py \
       django/contrib/formtools
cd -
mv /tmp/$ZIPNAME ../
