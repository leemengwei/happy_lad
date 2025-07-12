# happy_lad
A happy lad is happy

# Instruction

# Jetpack 5.1.4
sudo apt update
sudo apt install python3 python3-pip proxychains4 -y           # proxychains4 can be used when set to use My PC with its clash LAN port
sudo pip3 install -U pip 
sudo pip3 install jetson-stats 

pip install -r requirements

sudo cp happy_lad.service /etc/systemd/system/happy_lad.service
sudo systemctl daemon-reload;sudo systemctl restart happy_lad.service;sleep 2;sudo systemctl status happy_lad.service
sudo journalctl -u happy_lad.service -f
sudo crontab -e   # reboot every monday 3'o clock: 0 3 * * 1 /sbin/reboot   #不重启了 新系统开机无法主动发现摄像头必须插拔 费劲
sudo service cron restart
sudo crontab -l  
