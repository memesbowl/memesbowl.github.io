#!/bin/bash
cd /home/ian/code/memesbowl.github.io-master
/usr/bin/python script.py
git add .
git commit -m "publish"
git push
