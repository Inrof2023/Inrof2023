const int IN = 3;

void setup(){
 
  pinMode(IN, OUTPUT);   // デジタルピンを出力に設定
  
}
 
void loop(){
 
  digitalWrite(IN, HIGH); // HIGH LOWの組み合わせでモーター回転
  // delay(100);
  // digitalWrite(IN, LOW);
 
}