#include <GParser.h>
#include <Servo.h>
#define MAX_TIME 5000

Servo servo[6];
unsigned long timer[6];
int runTime[6] = {100, 100, 100, 100, 100, 100};

int nums[5];
int types[5];
int vals[5];
int direc[5];

void setup() {
  for (byte i = 2; i < 22; i++) {
    pinMode(i, OUTPUT);
  }
  //Serial.begin(9600);
  Serial.begin(115200);
  Serial.setTimeout(50);
  Serial.flush(); //очищаем буфер
  digitalWrite(13, HIGH);
  delay(100);
  digitalWrite(13, LOW);
  Serial.println("READY (setup)");
}

void loop() {
  if (Serial.available()) {
    char txs[100];
    int amount = Serial.readBytesUntil(';', txs, 100);
    txs[amount] = NULL;
    GParser data(txs, ',');
    int arrData[data.amount()];
    int am = data.parseInts(arrData);
    int val = arrData[1];
    if ((val < 0) || (val > 180)) {
      Serial.print("INCORRECT VAL ");
      val = 0;
    }

    switch (arrData[0]) {
      case 10:
        Serial.print("wrist ");
        Serial.println(val);
        servoControl(0, val, MAX_TIME);
        break;
      case 1:
        val = 180 - val;
        Serial.print("thumb ");
        Serial.println(val);
        servoControl(1, val, MAX_TIME);
        break;
      case 2:
        val = 180 - val;
        Serial.print("index ");
        Serial.println(val);
        servoControl(2, val, MAX_TIME);
        break;
      case 3:
        val = 180 - val;
        Serial.print("middle ");
        Serial.println(val);
        servoControl(3, val, MAX_TIME);
        break;
      case 4:
        Serial.print("ring ");
        Serial.println(val);
        servoControl(4, val, MAX_TIME);
        break;
      case 5:
        Serial.print("pinky ");
        Serial.println(val);
        servoControl(5, val, MAX_TIME);
        break;
      case 7:
        digitalWrite(13, 1);
        delay(50);
        digitalWrite(13, 0);
        Serial.println("Init Led");
        break;
      case 11:  // rock
        Serial.println("rock");
        formData(arrData);
        direcReverse();
        if (types[0] == types[1] && types[1] == types[2] && types[2] == 180) {
          valsReverse();
          for (byte i = 0; i < 5; i++) {
            servoControl(nums[i], vals[i], MAX_TIME);
          }
        }
        else {
          servoControl(nums[0], 180 - vals[0], MAX_TIME);
          servoControl(nums[2], direc[2], vals[2]);
          servoControl(nums[3], direc[3], vals[3]);
        }
        break;
      case 12:  // v
        Serial.println("v");
        formData(arrData);
        direcReverse();
        if (types[0] == types[3] && types[3] == types[4] && types[4] == 180) {
          valsReverse();
          for (byte i = 0; i < 5; i++) {
            servoControl(nums[i], vals[i], MAX_TIME);
          }
        }
        else {
          servoControl(nums[0], 180 - vals[0], MAX_TIME);
          servoControl(nums[3], direc[3], vals[3]);
          servoControl(nums[4], vals[4], MAX_TIME);
        }
        break;
      case 13: //phone
        Serial.println("phone");
        formData(arrData);
        direcReverse();
        if (types[1] == types[2] && types[2] == types[3] && types[3] == 180) {
          valsReverse();
          for (byte i = 0; i < 5; i++) {
            servoControl(nums[i], vals[i], MAX_TIME);
          }
        }
        else {
          servoControl(nums[1], direc[1], vals[1]);
          servoControl(nums[2], direc[2], vals[2]);
          servoControl(nums[3], direc[3], vals[3]);
        }
        break;
      case 14:  //spider
        Serial.println("spider");
        formData(arrData);
        direcReverse();
        if (types[2] == types[3] && types[3] == 180) {
          valsReverse();
          for (byte i = 0; i < 5; i++) {
            servoControl(nums[i], vals[i], MAX_TIME);
          }
        }
        else {
          servoControl(nums[2], direc[2], vals[2]);
          servoControl(nums[3], direc[3], vals[3]);
        }
        break;
      case 15:  // ok
        Serial.println("ok");
        formData(arrData);
        direcReverse();
        if (types[0] == types[1] && types[1] == 180) {
          valsReverse();
          for (byte i = 0; i < 5; i++) {
            servoControl(nums[i], vals[i], MAX_TIME);
          }
        }
        else {
          servoControl(nums[0], 180 - vals[0], MAX_TIME);
          servoControl(nums[1], direc[1], vals[1]);
        }
        break;
      case 16:  // thumbs
        Serial.println("thumbs");
        formData(arrData);
        direcReverse();
        if (types[1] == types[2] && types[2] == types[3] && types[3] == types[4] && types[4] == 180) {
          valsReverse();
          for (byte i = 0; i < 5; i++) {
            servoControl(nums[i], vals[i], MAX_TIME);
          }
        }
        else {
          servoControl(nums[1], direc[1], vals[1]);
          servoControl(nums[2], direc[2], vals[2]);
          servoControl(nums[3], direc[3], vals[3]);
          servoControl(nums[4], vals[4], MAX_TIME);
        }
        break;
      case 17:  // fuck
        Serial.println("fuck");
        formData(arrData);
        direcReverse();
        if (types[0] == types[1] && types[1] == types[3] && types[3] == types[4] && types[4] == 180) {
          valsReverse();
          for (byte i = 0; i < 5; i++) {
            servoControl(nums[i], vals[i], MAX_TIME);
          }
        }
        else {
          servoControl(nums[0], 180 - vals[0], MAX_TIME);
          servoControl(nums[1], direc[1], vals[1]);
          servoControl(nums[3], direc[3], vals[3]);
          servoControl(nums[4], vals[4], MAX_TIME);
        }
        break;
      case 18:  // init
        Serial.println("init");
        formData(arrData);
        if (types[0] == types[1] && types[1] == types[2] && types[2] == types[3] && types[3] == types[4] && types[4] == 180) {
          valsReverse();
          for (byte i = 0; i < 5; i++) {
            servoControl(nums[i], vals[i], MAX_TIME);
          }
        }
        break;
      default:
        Serial.println("INCORRECT NUM");
        break;

    }
  }
  for (byte i = 0; i < 6; i++) {
    if (millis() - timer[i] > runTime[i]) {
      servo[i].detach();
    }
  }
}

int servoControl(byte num, byte val, int tm) {
  runTime[num] = tm;
  servo[num].attach(num + 2);
  timer[num] = millis();
  servo[num].write(val);
}
void valsReverse() {
  vals[0] = 180 - vals[0];
  vals[1] = 180 - vals[1];
  vals[2] = 180 - vals[2];
}

void direcReverse() {
  direc[0] = 180 - direc[0];
  direc[1] = 180 - direc[1];
  direc[2] = 180 - direc[2];
}

int formData(int* arrDataPtr) {
  for (byte i = 0; i < 5; i++) {
    nums[i] = arrDataPtr[i + 1];
  }
  for (byte i = 0; i < 5; i++) {
    types[i] = arrDataPtr[i + 6];
  }
  for (byte i = 0; i < 5; i++) {
    vals[i] = arrDataPtr[i + 11];
  }
  for (byte i = 0; i < 5; i++) {
    direc[i] = arrDataPtr[i + 16];
  }
}
