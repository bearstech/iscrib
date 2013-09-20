#! /bin/bash

ISCRIB_ADMIN=maudin@itaapy.com
ISCRIB_PWD=foobar

# virtualenv
cd /opt/iscrib
# mkdir -p prod ; cd prod
virtualenv --system-site-packages -p /usr/bin/python2.6 gip-iscrib_prod ; cd gip-iscrib_prod

# pip install
./bin/pip install pytz

# get template
wget --no-check-certificate --user=guest --password=fr33m1nd42 https://filer.itaapy.com/iscrib/template.tar.gz
tar xvzf template.tar.gz

# remove vt-env libs
rm -fr template/lib/python2.6/site-packages/pip-0.7.2-py2.6.egg/
rm -fr template/lib/python2.6/site-packages/setuptools.pth
rm -fr template/lib/python2.6/site-packages/easy-install.pth
rm -fr template/lib/python2.6/site-packages/distribute-0.6.10-py2.6.egg/

# copy bins
for i in `ls bin`; do rm template/bin/$i; done
cp template/bin/* bin/

# copy libs
cp -r template/lib/python2.6/site-packages/* lib/python2.6/site-packages/

# dumb fix... utf8
sed -i 's/^# Copyright.*//g' /opt/iscrib/gip-iscrib_prod/lib/python2.6/site-packages/itools/pdf/css.py


# instance
rm -f ~/.gitconfig
git config --global --add user.email $ISCRIB_ADMIN
git config --global --add user.name $ISCRIB_ADMIN
./bin/icms-init.py -p 8080 -e $ISCRIB_ADMIN -w $ISCRIB_PWD -r iscrib iscrib.instance
