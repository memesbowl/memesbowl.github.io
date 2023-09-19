#!/bin/bash
current_day=$(date +%u)

if [ "$current_day" -eq 2 ]; then
    cd /home/ihrm/memesbowl.github.io
    python /home/ihrm/memesbowl.github.io/script.py   
    git add .
    git commit -m "publish"
    git push
    echo "pushed scoreboard update for week"
else
    echo "not tuesday do not update"
fi
