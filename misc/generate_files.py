#!/usr/bin/python

import os

os.mkdir("data")

for num in range(0,20):

	filename = "data/test_{0:02d}".format(num)
	os.popen("touch {}".format(filename))
	print("file {} created".format(filename))

print("finish!!!!")