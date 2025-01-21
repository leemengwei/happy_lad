#!/bin/bash
set -e

echo "=====Happy Lad Recorder====="
sleep 1
echo "Happy Lad Forever Run..."
cd /home/feifeichouchou/happy_lad/src/
/usr/bin/python3 /home/feifeichouchou/happy_lad/src/start_web_and_pipe.py --device_location /dev/video0 --port 5000 --config_file=config.json
sleep 10
/usr/bin/python3 /home/feifeichouchou/happy_lad/src/start_web_and_pipe.py --device_location /dev/video2 --port 5001 --config_file=config2.json
echo "All The Best"





# DONE: cron jobs... for preventing device hang up 
# DONE: static ip

# TODO: web page: view & saved images
# TODO  add datetime on frame

# optional: add a button
# optional: rtsp server