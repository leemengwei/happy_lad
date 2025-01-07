#!/bin/bash
set -e

echo "=====Happy Lad Recorder====="
sleep 1
echo "Happy Lad Forever Run..."
cd /home/feifeichouchou/happy_lad/src/
/usr/bin/python3 /home/feifeichouchou/happy_lad/src/start_web_and_pipe.py
echo "All The Best"


# sudo systemctl stop happy_lad.service;sudo systemctl daemon-reload;sudo systemctl disable happy_lad.service;sudo systemctl enable happy_lad.service
# sudo systemctl daemon-reload;sudo systemctl restart happy_lad.service;sleep 2;sudo systemctl status happy_lad.service



# DONE: cron jobs... for preventing device hang up 
# DONE: static ip

# TODO: web page: view & saved images
# TODO  add datetime on frame

# optional: add a button
# optional: rtsp server