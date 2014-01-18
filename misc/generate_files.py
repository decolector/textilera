#!/usr/bin/python
#
# create a dir and some dummy files
#

import os

if os.path.exists("data"):
	pass
else:
	os.mkdir("data")

for num in range(0,20):

	filename = "data/test_{0:02d}".format(num)
	os.popen("touch {}".format(filename))
	print("file {} created".format(filename))

print("finish!!!!")