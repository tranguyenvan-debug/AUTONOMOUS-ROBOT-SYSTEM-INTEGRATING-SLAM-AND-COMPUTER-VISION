#include <Arduino.h>
#include <ESP32Encoder.h>

/* MOTOR PINS */

#define L_IN1 5
#define L_IN2 6
#define L_PWM 4

#define R_IN1 15
#define R_IN2 7
#define R_PWM 16

/* ENCODER PINS */

#define L_A 9
#define L_B 8
#define R_A 11
#define R_B 10

/* PWM */

#define PWM_FREQ 800
#define PWM_RES 10
#define PWM_MAX 1023

#define L_CH 0
#define R_CH 1

/* WHEEL */

#define WHEEL_DIAMETER 0.065
#define WHEEL_CIRC (WHEEL_DIAMETER * PI)

/* ENCODER */

float PPR_L = 11800;
float PPR_R = 11800;

ESP32Encoder encL;
ESP32Encoder encR;

/* MOTOR CONTROL */

void setDir(int L, int R) {

  if (L > 0) {
    digitalWrite(L_IN1, LOW);
    digitalWrite(L_IN2, HIGH);
  } else if (L < 0) {
    digitalWrite(L_IN1, HIGH);
    digitalWrite(L_IN2, LOW);
  } else {
    digitalWrite(L_IN1, LOW);
    digitalWrite(L_IN2, LOW);
  }

  if (R > 0) {
    digitalWrite(R_IN1, LOW);
    digitalWrite(R_IN2, HIGH);
  } else if (R < 0) {
    digitalWrite(R_IN1, HIGH);
    digitalWrite(R_IN2, LOW);
  } else {
    digitalWrite(R_IN1, LOW);
    digitalWrite(R_IN2, LOW);
  }
}

void setPWM(int L, int R) {

  ledcWrite(L_CH, L);
  ledcWrite(R_CH, R);
}

void stopMotor() { setPWM(0, 0); }

/* RPM MEASURE */

void measureRPM(int pwm) {

  encL.clearCount();
  encR.clearCount();

  setDir(1, 1);
  setPWM(pwm, pwm);

  delay(1000);

  long tL = encL.getCount();
  long tR = encR.getCount();

  stopMotor();

  float rpmL = (tL / PPR_L) * 60.0;
  float rpmR = (tR / PPR_R) * 60.0;

  float vL = rpmL * WHEEL_CIRC / 60.0;
  float vR = rpmR * WHEEL_CIRC / 60.0;

  Serial.print("PWM ");
  Serial.print(pwm);

  Serial.print(" | L_ticks=");
  Serial.print(tL);

  Serial.print(" | R_ticks=");
  Serial.print(tR);

  Serial.print(" | L_RPM=");
  Serial.print(rpmL);

  Serial.print(" | R_RPM=");
  Serial.print(rpmR);

  Serial.print(" | L_m/s=");
  Serial.print(vL);

  Serial.print(" | R_m/s=");
  Serial.println(vR);
}

/* TEST PPR */

void testPPR_L() {

  Serial.println("DANH DAU BANH TRAI");
  Serial.println("NHAN PHIM BAT DAU");

  while (!Serial.available())
    ;
  Serial.read();

  encL.clearCount();

  setDir(1, 0);
  setPWM(650, 0);

  Serial.println("NHAN PHIM KHI BANH DU 1 VONG");

  while (!Serial.available()) {

    Serial.println(encL.getCount());
    delay(200);
  }

  Serial.read();

  stopMotor();

  PPR_L = abs(encL.getCount());

  Serial.print("PPR TRAI = ");
  Serial.println(PPR_L);
}

void testPPR_R() {

  Serial.println("DANH DAU BANH PHAI");
  Serial.println("NHAN PHIM BAT DAU");

  while (!Serial.available())
    ;
  Serial.read();

  encR.clearCount();

  setDir(0, 1);
  setPWM(0, 650);

  Serial.println("NHAN PHIM KHI BANH DU 1 VONG");

  while (!Serial.available()) {

    Serial.println(encR.getCount());
    delay(200);
  }

  Serial.read();

  stopMotor();

  PPR_R = abs(encR.getCount());

  Serial.print("PPR PHAI = ");
  Serial.println(PPR_R);
}

/* FIND MIN PWM */

void findMinPWM() {

  Serial.println("===== FIND MIN PWM =====");

  for (int pwm = 400; pwm <= 800; pwm += 20) {

    encL.clearCount();
    encR.clearCount();

    setDir(1, 1);
    setPWM(pwm, pwm);

    delay(500);

    long L = abs(encL.getCount());
    long R = abs(encR.getCount());

    stopMotor();

    Serial.print("PWM ");
    Serial.print(pwm);
    Serial.print(" | L=");
    Serial.print(L);
    Serial.print(" R=");
    Serial.println(R);

    delay(500);
  }
}

/* PWM SPEED TABLE */

void sweepPWM() {

  Serial.println("===== PWM RPM TABLE =====");

  for (int pwm = 400; pwm <= 1023; pwm += 25) {

    measureRPM(pwm);

    delay(500);
  }
}

/* BALANCE */

void balanceTest() {

  Serial.println("===== BALANCE TEST =====");

  for (int pwm = 700; pwm <= 1000; pwm += 50) {

    measureRPM(pwm);

    delay(1000);
  }
}

/* SETUP */

void setup() {

  Serial.begin(115200);

  /* MOTOR */

  pinMode(L_IN1, OUTPUT);
  pinMode(L_IN2, OUTPUT);
  pinMode(R_IN1, OUTPUT);
  pinMode(R_IN2, OUTPUT);

  /* ENCODER INPUT */

  pinMode(L_A, INPUT_PULLUP);
  pinMode(L_B, INPUT_PULLUP);
  pinMode(R_A, INPUT_PULLUP);
  pinMode(R_B, INPUT_PULLUP);

  /* PWM */

  ledcSetup(L_CH, PWM_FREQ, PWM_RES);
  ledcAttachPin(L_PWM, L_CH);

  ledcSetup(R_CH, PWM_FREQ, PWM_RES);
  ledcAttachPin(R_PWM, R_CH);

  /* ENCODER */

  encL.attachFullQuad(L_A, L_B);
  encR.attachFullQuad(R_A, R_B);

  Serial.println("READY");

  Serial.println("1 = TEST PPR LEFT");
  Serial.println("2 = TEST PPR RIGHT");
  Serial.println("3 = FIND MIN PWM");
  Serial.println("4 = PWM RPM TABLE");
  Serial.println("5 = BALANCE TEST");
}

/* LOOP */

void loop() {

  if (!Serial.available())
    return;

  char c = Serial.read();

  if (c == '1')
    testPPR_L();
  if (c == '2')
    testPPR_R();
  if (c == '3')
    findMinPWM();
  if (c == '4')
    sweepPWM();
  if (c == '5')
    balanceTest();
}