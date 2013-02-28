textilera
=========

Tools for converting qrcode images to Janome .jef files. It uses [python-showjef (https://bitbucket.org/dboddie/python-showjef)] to convert svg files to .jef format

requirements:

Do 
    pip install -r requirements.txt

PyQt4 must be installed system wide manually or with your prefered package manager, after that you can copy the module into site-packages of your virtualenv. For example for debian/ubuntu do:

    cp -r /usr/lib/python2.7/dist-packages/PyQt4/ env/lib/python2.7/site-packages

SIP is not installable with pip as well, so: 

    cp /usr/lib/python2.7/dist-packages/sip.so env/lib/python2.7/site-packages/
    cp /usr/lib/python2.7/dist-packages/sipconfig_nd.py env/lib/python2.7/site-packages/
    cp /usr/lib/python2.7/dist-packages/sipconfig.py env/lib/python2.7/site-packages/
    cp /usr/lib/python2.7/dist-packages/sipdistutils.py env/lib/python2.7/site-packages/

