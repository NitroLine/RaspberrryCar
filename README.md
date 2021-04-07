# RaspberrryCar
Код для машинки Raspberry Pi + Arduino Mega
- A_Category - тест рекации на распознование знаков
- B_Category - гонки/скорость. Лучший код на C++
- C_Category - город: движение + распознование 


# AUTORUN instruction
Run this commands in terminal
```
cd /etc/xdg/autostart/ 
sudo nano autoruncode.desktop 
```
In opened window paste this and save and exit by clicking CTRL + X
```
[Desktop Entry] 
Version=1.0 
Encoding=UTF-8 
Name=1 
Comment=hren 
Exec=sh /home/pi/script.sh
Type=Application
Terminal=true
```
Now go to home folder
```
cd ~
```
Create script
```
nano script.sh
```
paste your bash code in this file <br/>
Example code:
```
#!/bin/bash
sleep 1
echo "Hi"
#Here can be your code
#Example:
cd /home/pi/code/Cascade
sudo python3 /home/pi/code/Cascade/C_Category.py
```
Exit and save. Now script should start, when desktop loaded
