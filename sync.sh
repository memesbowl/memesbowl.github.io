#!/bin/bash
cd /home/ian/code/memesbowl.github.io-master
python script.py
git add .
git commit -m "publish"
git push
