#!/usr/bin/python
#
# create a dir and some dummy files
#

import os

def checkCreateDirs(dirname):
    try:
        if not os.path.exists(dirname):
            if os.path.isdir(dirname):

                print dirname," existe y es un directorio"
            else:
                print dirname , " no existe, creandolo"
                os.mkdir(dirname)

    except OSError, err:
        print err



checkCreateDirs("data")

for num in range(0,20):

	filename = "data/test_{0:02d}".format(num)
	os.popen("touch {}".format(filename))
	print("file {} created".format(filename))

print("finish!!!!")
