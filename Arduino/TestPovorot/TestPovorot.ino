#include <Servo.h>

const int CenterAngle=80;
const int MaxLeftAngle=145;
const int MaxRightAngle=85;
float curAngle=0;
float oldCurAngle=0;

int ForwardDirPin = 7; //мотор 1 движение вперед 
int ForwardSpeedPin = 6; //мотор 1 управление скоростью 
int switchPin =15;                                                                                                                                                                                                                                                          
//int ForwardDirPin2 = 4; //мотор 1 движение вперед 
//int ForwardSpeedPin2 = 5; //мотор 1 управление скоростью 

int curSpeed = 0;
const int maxSpeed=1850; //1544
const int LowSpeed = 1850; //1539
double kf = (maxSpeed - LowSpeed)/30.0; 
const int StopSpeed = 1500;
const int RoadSpeed=1530;
const int ObgonSpeed=1560;
const int ReverseSpeed=1400;
const bool debug=false;
bool IsStop=0, ClearWay=1;

Servo myServo; 
Servo motor;
bool started=0,reverseRun=0;
bool stoping=0;
String inString;
float koef=1;

bool button=0;
boolean debounыse(boolean last) {
  boolean current = digitalRead(switchPin);
  if(last != current) {
    delay(5);
    current = digitalRead(switchPin);
  }
  return current;
}
void setup() {
    Serial.begin(9600); 
      motor.attach(17);
      myServo.attach(9);
      pinMode(switchPin, INPUT);
      myServo.write(CenterAngle);
      motor.writeMicroseconds(StopSpeed);

} 

void start() {
  if (debug){
  Serial.println("START");
  }
  started=true;
  motor.writeMicroseconds(StopSpeed);
  delay(1500);
}

void stop() 
{ 
  motor.writeMicroseconds(StopSpeed);
  myServo.write(CenterAngle); 
}

void loop() 
{ 
 start();
 myServo.write(CenterAngle);
 delay(2000);
 myServo.write(CenterAngle+10);
 delay(2000);
 myServo.write(CenterAngle+20);
 delay(2000);
 myServo.write(CenterAngle+30);
 delay(2000);
 myServo.write(CenterAngle+40);
 delay(2000);
 myServo.write(CenterAngle+50);
 delay(2000);
 
}

