#include <iostream>
#include "opencv2/imgproc.hpp"
#include "opencv2/highgui.hpp"
#include "opencv2/videoio.hpp"
#include "line.h"
#include "line2.h"
#include <time.h>
using namespace std;
using namespace cv;
int minold = 320;
#include <stdio.h>      // standard input / output functions
#include <stdlib.h>
#include <string.h>     // string function definitions
#include <unistd.h>     // UNIX standard function definitions
#include <fcntl.h>      // File control definitions
#include <errno.h>      // Error number definitions
#include <termios.h>    // POSIX terminal control definitions
using namespace std;
using namespace cv;
int USB = open( "/dev/ttyUSB0", O_RDWR| O_NOCTTY );
void setupSerial(){
struct termios tty;
struct termios tty_old;
memset (&tty, 0, sizeof tty);

/* Error Handling */
if ( tcgetattr ( USB, &tty ) != 0 ) {
   std::cout << "Error " << errno << " from tcgetattr: " << strerror(errno) << std::endl;
}

/* Save old tty parameters */
tty_old = tty;

/* Set Baud Rate */
cfsetospeed (&tty, (speed_t)B9600);
cfsetispeed (&tty, (speed_t)B9600); //cfsetispeed (&tty, (speed_t)B115200);


/* Setting other Port Stuff */
tty.c_cflag     &=  ~PARENB;            // Make 8n1
tty.c_cflag     &=  ~CSTOPB;
tty.c_cflag     &=  ~CSIZE;
tty.c_cflag     |=  CS8;

tty.c_cflag     &=  ~CRTSCTS;           // no flow control
tty.c_cc[VMIN]   =  1;                  // read doesn't block
tty.c_cc[VTIME]  =  5;                  // 0.5 seconds read timeout
tty.c_cflag     |=  CREAD | CLOCAL;     // turn on READ & ignore ctrl lines

/* Make raw */
cfmakeraw(&tty);

/* Flush Port, then applies attributes */
tcflush( USB, TCIFLUSH );
if ( tcsetattr ( USB, TCSANOW, &tty ) != 0) {
   std::cout << "Error " << errno << " from tcsetattr" << std::endl;
}
}
void serWrite(string inpt){
	unsigned char cmd[13];
	strcpy((char*)cmd, inpt.c_str());
    int n_written = 0,
        spot = 0;
	
    do {
        n_written = write( USB, &cmd[spot], 1 );
        spot += n_written;
    } while (cmd[spot-1] != '\r' && n_written > 0);
    
}

int main() {
    
    VideoCapture cap(0);
	if (!cap.isOpened())
    {
        cout << "Can't open camera!";
        return -1;
    }
    Mat frame, frame_threshold;
    int View = 370, old_angle = 90;
    serWrite("Start#\r");
    time_t startTime = time(NULL);
    int k=0;
    bool started=false;
    while (true) {
        if (!started && time(NULL) - startTime > 5)
        {
             cout << "I_AM_READY\n";
             serWrite("Start#\r");
             started=true;
			 
		}
        cap >> frame;
        if (frame.empty())
            break;
        Mat gray;
        //gray = line::TransformImage(frame, View, Scalar(0, 0, 0), Scalar(188, 255, 32), false);
        //int x = line::FindLine(frame, gray, View, true);
        //if (x==0)
          //  x=640;
        if (started){
        int x = line2::FindLine(frame, minold, View,false);
        
        if (x==640 && minold!=640){
            k++;
            x=minold;
            if (k>0){

           // cout << "KOSTYALILPIP" << endl;
            k=0;
            minold=640;
            }
        }
        else{
            k=0;
            minold=x;
        }
        if (x==640)
            View=460;
        else
            View=370;
        string cmd ="Line*" +to_string(x)+"#\r";
        
        serWrite(cmd);
        //cout << x << endl;
        }
        else{
            imshow("waiting...",frame);
        }
        char key = (char)waitKey(1);
        if (key == 'q' || key == 27){
			serWrite("End#\r");
            break;
		}
    }
    return 0;
 
}
