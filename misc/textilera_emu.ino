
int ledpin = 13;
int val = 0;
long task_duration = 3000;
long worktime = 0;
boolean working = false;

void setup(){
  Serial.begin(9600);
  pinMode(ledpin, OUTPUT);
  digitalWrite(ledpin, LOW);
}

void loop(){
  
  //check if there is command
  if(Serial.available() > 0){
    val = Serial.read();
  }
  
  //keeps the task alive
  if(task_duration > millis() - worktime){
    working = true;
    digitalWrite(ledpin, HIGH);
  }
  else{
    working = false;
    digitalWrite(ledpin, LOW);
  }

  //evalueate serial input and acts accordingly
  if(val != 0){
    if(val == 97){
      if(!working){
        //init work
        worktime = millis();
        Serial.println("b");
      }
      else{
        //send hold message
        Serial.println("c");
      }   
    }
    else if(val != 97){
      //unknown val
      Serial.println("u");

    }
    val = 0;
  }
}


