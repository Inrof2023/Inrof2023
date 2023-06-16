#include <MsTimer2.h>

#define DIR1 4
#define STP1 5
#define DIR2 6
#define STP2 7

#define SEN1 A0
#define SEN2 A1
#define SEN3 A2
#define SEN4 A3

int speed1 = 1;
int speed2 = 1;

unsigned int count = 0;
void interrupt(){
  digitalWrite(DIR1,speed1 > 0 ? LOW : HIGH);
  digitalWrite(DIR2,speed2 > 0 ? HIGH : LOW);

//   if(speed1 > 0 && count % (200 / speed1) == 0){
//     digitalWrite(STP1,HIGH);
//     digitalWrite(STP1,LOW);
//   }
//   if(speed2 > 0 && count % (200 / speed2) == 0){
//     digitalWrite(STP2,HIGH);
//     digitalWrite(STP2,LOW);
//   }

  digitalWrite(STP1,HIGH);
  digitalWrite(STP1,LOW);
  digitalWrite(STP2,HIGH);
  digitalWrite(STP2,LOW);

  if(count < 200){
    count++;
  }else{
    count = 0;
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(SEN1,INPUT);
  pinMode(SEN2,INPUT);
  pinMode(SEN3,INPUT);
  pinMode(SEN4,INPUT);
  pinMode(DIR1,OUTPUT);
  pinMode(STP1,OUTPUT);
  pinMode(DIR2,OUTPUT);
  pinMode(STP2,OUTPUT);
  MsTimer2::set(14,interrupt);
  MsTimer2::start();
  speed1 = 200;
  speed2 = 200;
}

const float P = 20;
const float I = 0;
const float D = 0;
float presen = 0;
float sumsen = 0;

void loop() {
  float sen = (analogRead(SEN1) + analogRead(SEN2) - analogRead(SEN3) - analogRead(SEN4)) / 2 / 1024.0;
  Serial.println(sen);
  float val = P * sen + I * sumsen + D * (sen - presen);
  if(val > 100)val = 100;
  presen = sen;
  sumsen += sen;
  speed1 = 100 - val;
  speed2 = 100 + val;
  delay(100);
}