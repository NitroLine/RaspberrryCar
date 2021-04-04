# RaspberrryCar

# AUTORUN instruction
cd /etc/xdg/autostart/ \n
sudo nano autoruncode.desktop \n

Paste it into file and save \n
[Desktop Entry] \n
Version=1.0 \n
Encoding=UTF-8 \n
Name=1 \n
Comment=hren \n
Exec=sh /home/pi/script.sh
Type=Application
Terminal=true

cd ~
nano script.sh
paste code
#!/bin/bash
sleep 1
echo "Hi"
#Here can be your code
#Example:
cd /home/pi/code/Cascade
sudo python3 /home/pi/code/Cascade/C_Category.py
