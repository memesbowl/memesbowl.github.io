#!/bin/bash
cd /home/ihrm/memesbowl.github.io
python /home/ihrm/memesbowl.github.io/script.py
git add .
git commit -m "publish"
git push
