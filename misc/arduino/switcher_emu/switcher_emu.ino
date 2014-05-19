int ledpin = 13;
int val = 0;
void setup(){
  Serial.begin(9600);
  pinMode(ledpin, OUTPUT);
  digitalWrite(ledpin, LOW);
}

void loop(){
  if (Serial.available() > 0) {
    val = Serial.read();
    if(val == 'r'){
      digitalWrite(ledpin, HIGH);
      delay(3000);
      digitalWrite(ledpin, LOW);
    }
  }
}
