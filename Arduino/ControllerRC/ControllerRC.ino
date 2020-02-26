#include <Servo.h>

const int CenterAngle=80;
const int MaxLeftAngle=145;
const int MaxRightAngle=85;
float curAngle=0;
float oldCurAngle=0;
unsigned long timer=0;

int ForwardDirPin = 7; //мотор 1 движение вперед 
int ForwardSpeedPin = 6; //мотор 1 управление скоростью 
int switchPin =15;                                                                                                                                                                                                                                                          
//int ForwardDirPin2 = 4; //мотор 1 движение вперед 
//int ForwardSpeedPin2 = 5; //мотор 1 управление скоростью 

int curSpeed = 0;
const int maxSpeed=1690; //1544
const int LowSpeed = 1690; //1539
double kf = (maxSpeed - LowSpeed)/30.0; 
const int StopSpeed = 1500;
const int RoadSpeed=1530;
const int ObgonSpeed=1560;
const int ReverseSpeed=1200;
const bool debug=false;
bool IsStop=0, ClearWay=1;

Servo myServo; 
Servo motor;
bool started=0,reverseRun=0;
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
      if (debug){
      Serial.println("Setuping..."); 
      }
      motor.attach(17);
      myServo.attach(9);
      pinMode(switchPin, INPUT);
      myServo.write(CenterAngle);
      motor.writeMicroseconds(StopSpeed);
      delay(1500);
      myServo.write(CenterAngle+30);
      delay(1000);
      myServo.write(CenterAngle);

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
void Run() 
{ 

      myServo.write(CenterAngle+curAngle);
      if (millis() - timer > 2000)
      { 
            curSpeed = LowSpeed + abs(curAngle)*kf;///(2.0-cos((curAngle*1.5/180.0)*PI));
      }
    	if(!ClearWay)
    		stop();
    	else{
    		motor.writeMicroseconds(curSpeed);
    //Serial.println(curSpeed);
  }
}
void IAmReady(){
  myServo.write(CenterAngle-30);
  delay(1000);
  myServo.write(CenterAngle+30);
  delay(1000);
  myServo.write(CenterAngle);
}
 

void ReverseRun(){
  motor.writeMicroseconds(ReverseSpeed);
  delay(100);
    motor.writeMicroseconds(StopSpeed);
  delay(100);
  motor.writeMicroseconds(ReverseSpeed);
  delay(500);
}
void Calculet(int Line)
{      
        if (Line==640){
           if (oldCurAngle<0)
            curAngle=-40.0;
          if (oldCurAngle>0)
            curAngle=40.0;
          if (oldCurAngle==0)
            curAngle=oldCurAngle;
        }
        else{
	    curAngle = 320-Line; //высчитываем смещение относительно центраы
	    curAngle = curAngle*((30.0)/150.0);// пропорционально ументшаем, чтобы угол изменялся от -30 до 30 градусов
            oldCurAngle=curAngle;
        }
	//Serial.println(curAngle);// debug
}

void Lights(String Signal)
{
  	int inputCmd=Signal[0]-'0';
        if (debug){
        Serial.println(inputCmd);
        }
	switch (inputCmd) {
    case 1: //Red
		if(!ClearWay) break;
		curSpeed=LowSpeed;
                ClearWay=false;
		break;
	case 2: //Green 
                ClearWay=true;
		curSpeed = maxSpeed;
                 ClearWay=true;
		break;
	case 3: //Yellow
                ClearWay=false;
		break;
	case 4: //Red and Yellow
		if(!ClearWay) break;
		curSpeed=LowSpeed; 
		break;
    default:
		break;
    }
}

String GetResult(String s)
{
	String ans="";
	bool ws=0;
	for (int i=0;i<s.length()-1;i++)
	{
		if(ws)
			ans+=s[i];
		if(s[i]=='*')
			ws=1;
	}
        return ans;
}

void loop() 
{ 
      if (!started && digitalRead(switchPin)==HIGH){
        start();
     }
     else if (started && digitalRead(switchPin)==LOW){
                 stop();
                 started=0;
      }

      //Serial.println(digitalRead(switchPin));
      //delay(200);
      while (Serial.available()) {
               if (!started && digitalRead(switchPin)==HIGH){
                  start();
                 }
               else if (started && digitalRead(switchPin)==LOW){
                 stop();
                 started=0;
               }
                 
		char inChar = Serial.read();// читаем из порта
		inString += inChar;
		if (inChar == '#') {
                    if (debug){
                   Serial.println(inString);
                    }
                    //решётка конец ввода
		   if (inString.indexOf("Line")!=-1) {//ищем ключ по которому определяем чего передали
				Calculet(atoi(GetResult(inString).c_str()));
                                 if (started){
                                    Run();
                                  }
			  }
			  else if (inString.indexOf("Stop")!=-1) {
				    stop();
				    //delay(2000);
			  }
			  else if (inString.indexOf("Reverse")!=-1) {
			        stop();
                                  ReverseRun();
			  }else if (inString.indexOf("Start")!=-1) {
                                IAmReady();             
			  }else if (inString.indexOf("Road")!=-1) {
				  curSpeed=RoadSpeed;
                                  timer = millis();
			  }else if (inString.indexOf("Obgon")!=-1) {
				curSpeed=ObgonSpeed;
				timer = millis();
			  }else if (inString.indexOf("End")!=-1) {
				stop();
                                started=0;
				delay(2000);
			  }else if (inString.indexOf("Forward")!=-1) {
				stop();
				delay(2000);
			  }
			  else if (inString.indexOf("Light")!=-1) {
                                //Serial.println(inString);
				Lights(GetResult(inString));
			  }

			inString="";
			}
	}
}
