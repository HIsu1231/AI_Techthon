
#include <SoftwareSerial.h>
#include<DFPlayer_Mini_Mp3.h>

#define BT_TX 5                    //블루투스 RX핀을 3으로 정의
#define BT_RX 4                    //블루투스 TX핀을 2으로 정의

SoftwareSerial HM10(BT_TX,BT_RX);  // RX핀(3번)은 HM10의 TX에 연결 
                                   // TX핀(2번)은 HM10의 RX에 연결  
SoftwareSerial mySerial(9,10);

int trigPin = 12;
int echoPin = 11;
char n;
char a;
int nn=0;
int nnn;
int py;

void setup() {
    
  Serial.begin(9600);              //아두이노-PC 시리얼통신 시작
  HM10.begin(9600);                //HM10 시리얼통신 시작
  mySerial.begin(9600);            //mp3모듈
  mp3_set_serial(mySerial); 
  mp3_set_volume(100);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  
  
  delay(3000);

}



void loop() {
  HM10.listen();
  
  /*int bb = 1; 그냥 if문을 돌렸을 때는 통신 됨 근데 블투모듈과 관련된 변수로 돌렸을 때는 통신이 안됨

  if (bb){
    Serial.print("b");
    Serial.println(); //무조건 println이 있어야 파이썬 코드에 출력 
  }*/

  if (HM10.available()) {         //HM-10에서 신호가 온다면?
    //Serial.write(HM10.read());//시리얼통신 창에 HM-10값을 써라
    n=HM10.read();
    
    if (n=='1')  //n에 연결됐다는 문구도 읽혀서 if문으로 처리
      a = n;
   }
    
   if (a=='1'){
      while(1){
        mySerial.listen();
        digitalWrite(trigPin, HIGH);
        delay(10);
        digitalWrite(trigPin, LOW);

        float duration = pulseIn(echoPin, HIGH);
        float distance = ((float)(340*duration)/10000)/2;

        /*Serial.print("Duration: ");
        Serial.print(duration);
        Serial.print("\n\nDistance: ");
        Serial.print(distance);
        Serial.print("cm\n\n");*/

        if (distance < 30){
         mp3_play(2);//한발 물러나
        }
        
        else if(distance>=30&&distance<=50){
         //Serial.end();
         mp3_play(1);//적정거리입니다
         nn = 1;
         //Serial.println("2");
         a = 1;
         break;    
        }
         
        else{
            mp3_play(3);//가까이
         }
        
        delay(6000);
          //HM10.println(distance);
      }     
      //Serial.end();
    }
    
    //nn = 1;
    if (nn){
      Serial.println("2");
      
      while(Serial.available() > 0){
      char c = Serial.read();
      
      if ( c == 'a' )
        mp3_play(4);
      else if ( c == 'b')
        mp3_play(5);
      else if (c == 'c')
        mp3_play(6);
      else if (c == 'd')
        mp3_play(7);
      else if (c == 'e')
        mp3_play(8);
      }
    }
    
  delay(500);  

}
