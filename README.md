# RaspberrryCar

AUTORUN instruction
cd /etc/xdg/autostart/
sudo nano autoruncode.desktop

Paste it into file and save
[Desktop Entry]
Version=1.0
Encoding=UTF-8
Name=1
Comment=hren
Exec=sh /home/pi/script.sh
Type=Application
Terminal=true

cd ~
nano script.sh
paste code
#!/bin/bash
sleep 1
echo "Hi"
# Here can be your code
# Example:
cd /home/pi/code/Cascade
sudo python3 /home/pi/code/Cascade/C_Category.py
