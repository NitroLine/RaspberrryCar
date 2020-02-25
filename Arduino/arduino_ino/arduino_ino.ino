#include <Servo.h> 
const int CenterAngle=80;
const int MaxLeftAngle=145;
const int MaxRightAngle=85;
float curAngle=0;
float oldCurAngle=0;
unsigned long timer=0;

int ForwardDirPin = 7; //мотор 1 движение вперед 
int ForwardSpeedPin = 6; //мотор 1 управление скоростью 
                                                                                                                                                                                                                                                          
//int ForwardDirPin2 = 4; //мотор 1 движение вперед 
//int ForwardSpeedPin2 = 5; //мотор 1 управление скоростью 

int curSpeed = 0;
const int maxSpeed=1545;
const int LowSpeed = 1545;
double kf = (maxSpeed - LowSpeed)/30.0; 
const int StopSpeed = 1500;

bool IsStop=0, ClearWay=1;

Servo myServo; 
Servo motor;

String inString;
float koef=1;
void setup() {
    Serial.begin(115200); 
    Serial.println("Setuping..."); 
      motor.attach(17);
      myServo.attach(9);
      myServo.write(CenterAngle);
      motor.writeMicroseconds(StopSpeed);
      delay(1500);

} 

void start() {
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
      curSpeed = maxSpeed-abs(curAngle)*kf;///(2.0-cos((curAngle*1.5/180.0)*PI));
      Serial.println(curSpeed);
        /*if (millis() - timer > 7000)
        {
                curSpeed = maxSpeed;
        }*/
    	if(!ClearWay)
    		stop();
    	else{
    		motor.writeMicroseconds(curSpeed);
}
} 

void Calculet(int Line)
{      
        if (Line==640){
           if (oldCurAngle<0)
            curAngle=-30.0;
          if (oldCurAngle>0)
            curAngle=30.0;
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
        Serial.println(inputCmd);
	switch (inputCmd) {
    case 1: //Red
		if(!ClearWay) break;
		curSpeed=LowSpeed;
                ClearWay=false;
		break;
	case 2: //Green 
		curSpeed = maxSpeed;
                ClearWay=true;
		break;
	case 3: //Yellow
		if(!ClearWay) break;
		curSpeed=LowSpeed; 
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
	while (Serial.available()) {
		char inChar = Serial.read();// читаем из порта
		inString += inChar;
		if (inChar == '#') {
                   Serial.println(inString);
                    //решётка конец ввода
		   if (inString.indexOf("Line")!=-1) {//ищем ключ по которому определяем чего передали
				Calculet(atoi(GetResult(inString).c_str()));
                                Run();
			  }
			  else if (inString.indexOf("Stop")!=-1) {
				stop();
				delay(2000);
			  }
			  else if (inString.indexOf("Right")!=-1) {
				stop();
				delay(2000);
			  }else if (inString.indexOf("Start")!=-1) {
                                start();
			  }else if (inString.indexOf("Road")!=-1) {
				stop();
				delay(2000);
			  }else if (inString.indexOf("Pedast")!=-1) {
				curSpeed=LowSpeed;
				timer = millis();
			  }else if (inString.indexOf("Left")!=-1) {
				stop();
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

