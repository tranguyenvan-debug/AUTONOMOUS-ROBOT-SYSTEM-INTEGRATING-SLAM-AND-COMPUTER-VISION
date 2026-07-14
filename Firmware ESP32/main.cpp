#include <Arduino.h>
#include <ArduinoJson.h>
#include <ESP32Encoder.h>

// ================= PIN =================
#define L_IN1 5
#define L_IN2 6
#define L_PWM 4

#define R_IN1 15
#define R_IN2 7
#define R_PWM 16

#define L_A 9
#define L_B 8
#define R_A 11
#define R_B 10

#define LED_PIN 2

#define PWM_FREQ 800
#define PWM_RES 10
#define PWM_MAX 1023
#define PWM_MIN 380

#define L_CH 0
#define R_CH 1

// ================= ROBOT =================
const float wheel_diameter = 0.065;
const float wheel_base = 0.18;
const float wheel_circ = PI * wheel_diameter;

const float PPR_L = 10800.0;
const float PPR_R = 11330.0;

// ================= CONTROL =================
#define CONTROL_HZ 100
#define DT (1.0 / CONTROL_HZ)

// ================= ENCODER =================
ESP32Encoder encL;
ESP32Encoder encR;

long prevTickL = 0;
long prevTickR = 0;

// ================= CMD =================
float cmd_v = 0;
float cmd_w = 0;

float cmd_v_ramp = 0;
float cmd_w_ramp = 0;

uint32_t lastCmd = 0;
const uint32_t timeout = 500;

// ================= TARGET RPM =================
float targetRPM_L = 0;
float targetRPM_R = 0;

// ================= PID =================
float Kp = 18;
float Ki = 6;
float Kd = 0.12;

float eL = 0, eR = 0;
float prevL = 0, prevR = 0;
float sumL = 0, sumR = 0;

// ================= FILTER =================
float rpmL_f = 0;
float rpmR_f = 0;
const float alpha = 0.4;

// ================= ODOM =================
float x = 0;
float y = 0;
float th = 0;

// ================= MOTOR =================
void setDir(float L, float R) {

  if (L > 0) {
    digitalWrite(L_IN1, LOW);
    digitalWrite(L_IN2, HIGH);
  }
  else if (L < 0) {
    digitalWrite(L_IN1, HIGH);
    digitalWrite(L_IN2, LOW);
  }
  else {
    digitalWrite(L_IN1, LOW);
    digitalWrite(L_IN2, LOW);
  }

  if (R > 0) {
    digitalWrite(R_IN1, LOW);
    digitalWrite(R_IN2, HIGH);
  }
  else if (R < 0) {
    digitalWrite(R_IN1, HIGH);
    digitalWrite(R_IN2, LOW);
  }
  else {
    digitalWrite(R_IN1, LOW);
    digitalWrite(R_IN2, LOW);
  }
}

void setPWM(int L, int R) {

  if (L != 0)
    L = constrain(abs(L) + PWM_MIN, PWM_MIN, PWM_MAX);

  if (R != 0)
    R = constrain(abs(R) + PWM_MIN, PWM_MIN, PWM_MAX);

  ledcWrite(L_CH, L);
  ledcWrite(R_CH, R);
}

// ================= RAMP =================
float ramp(float current, float target, float step) {

  float diff = target - current;

  if (diff > step) diff = step;
  if (diff < -step) diff = -step;

  return current + diff;
}

// ================= RECEIVE CMD =================
void readCmd() {

  if (!Serial.available()) return;

  String json = Serial.readStringUntil('\n');

  StaticJsonDocument<64> doc;

  if (!deserializeJson(doc, json)) {

    cmd_v = doc["lx"] | 0.0;
    cmd_w = doc["az"] | 0.0;

    lastCmd = millis();
  }
}

// ================= VELOCITY =================
void velocityLoop() {

  float step = 0.5 * DT;

  cmd_v_ramp = ramp(cmd_v_ramp, cmd_v, step);
  cmd_w_ramp = ramp(cmd_w_ramp, cmd_w, step);

  float vL = cmd_v_ramp - cmd_w_ramp * wheel_base / 2;
  float vR = cmd_v_ramp + cmd_w_ramp * wheel_base / 2;

  targetRPM_L = (vL / wheel_circ) * 60;
  targetRPM_R = (vR / wheel_circ) * 60;
}

// ================= RPM =================
float calcRPM(long diff, float ppr) {
  return (diff / ppr) * 60.0 * CONTROL_HZ;
}

// ================= CONTROL LOOP =================
void controlLoop() {

  static uint32_t last = 0;

  if (millis() - last < 1000 / CONTROL_HZ)
    return;

  last = millis();

  // ===== EMERGENCY STOP =====
  if (millis() - lastCmd > timeout) {

    cmd_v = 0;
    cmd_w = 0;

    cmd_v_ramp = 0;
    cmd_w_ramp = 0;

    targetRPM_L = 0;
    targetRPM_R = 0;
  }

  long tickL = encL.getCount();
  long tickR = encR.getCount();

  long diffL = tickL - prevTickL;
  long diffR = tickR - prevTickR;

  prevTickL = tickL;
  prevTickR = tickR;

  float rpmL = calcRPM(diffL, PPR_L);
  float rpmR = calcRPM(diffR, PPR_R);

  rpmL_f = alpha * rpmL + (1 - alpha) * rpmL_f;
  rpmR_f = alpha * rpmR + (1 - alpha) * rpmR_f;

  eL = targetRPM_L - rpmL_f;
  eR = targetRPM_R - rpmR_f;

  sumL += eL * DT;
  sumR += eR * DT;

  sumL = constrain(sumL, -200, 200);
  sumR = constrain(sumR, -200, 200);

  float dL = (eL - prevL) / DT;
  float dR = (eR - prevR) / DT;

  float outL = Kp * eL + Ki * sumL + Kd * dL;
  float outR = Kp * eR + Ki * sumR + Kd * dR;

  prevL = eL;
  prevR = eR;

  setDir(outL, outR);
  setPWM(outL, outR);

  // ================= ODOM =================

  float vL = rpmL_f * wheel_circ / 60;
  float vR = rpmR_f * wheel_circ / 60;

  float v = (vL + vR) / 2;
  float w = (vR - vL) / wheel_base;

  th += w * DT;

  x += v * cos(th) * DT;
  y += v * sin(th) * DT;

  // ===== SEND JSON FOR ROS2 =====
  Serial.print("{\"x\":");
  Serial.print(x,4);
  Serial.print(",\"y\":");
  Serial.print(y,4);
  Serial.print(",\"yaw\":");
  Serial.print(th,4);
  Serial.print(",\"vl\":");
  Serial.print(v,4);
  Serial.print(",\"va\":");
  Serial.print(w,4);
  Serial.println("}");

  // ===== DEBUG LED =====
  static uint32_t lastLED = 0;

  if (millis() - lastLED > 500) {
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    lastLED = millis();
  }
}

// ================= SETUP =================
void setup() {

  Serial.begin(115200);

  pinMode(L_IN1, OUTPUT);
  pinMode(L_IN2, OUTPUT);
  pinMode(R_IN1, OUTPUT);
  pinMode(R_IN2, OUTPUT);

  pinMode(LED_PIN, OUTPUT);

  ledcSetup(L_CH, PWM_FREQ, PWM_RES);
  ledcAttachPin(L_PWM, L_CH);

  ledcSetup(R_CH, PWM_FREQ, PWM_RES);
  ledcAttachPin(R_PWM, R_CH);

  encL.attachFullQuad(L_B, L_A);
  encR.attachFullQuad(R_A, R_B);

  encL.clearCount();
  encR.clearCount();

  Serial.println("ESP32 ROBOT READY (ROS2 JSON)");
}

// ================= LOOP =================
void loop() {

  readCmd();

  velocityLoop();

  controlLoop();
}