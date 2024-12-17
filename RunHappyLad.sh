#!/bin/bash
set -e

echo "=====Happy Lad Recorder====="
sleep 1
echo "Happy Lad Forever Run..."
cd /home/feifeichouchou/happy_lad/src/
/usr/bin/python3 web.py &
/usr/bin/python3 /home/feifeichouchou/happy_lad/src/deepstream_test_1_usb.py /dev/video0
echo "All The Best"
