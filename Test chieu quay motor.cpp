#include <Arduino.h>
#include <ESP32Encoder.h>

// ===============================
// PIN
// ===============================
#define L_IN1 5
#define L_IN2 6
#define L_PWM 4

#define R_IN1 15
#define R_IN2 7
#define R_PWM 16

#define LED 2

#define L_A 9
#define L_B 8
#define R_A 11
#define R_B 10

#define PWM_FREQ 800
#define PWM_RES 10
#define L_PWM_CH 0
#define R_PWM_CH 1
#define TEST_PWM 400 // PWM cố định để test ~40% duty

ESP32Encoder L_Encoder;
ESP32Encoder R_Encoder;

// ===============================
// setMotorDir
// L > 0 = tiến, L < 0 = lùi  (tương tự R)
// Bánh phải đảo IN1/IN2 so với trái vì motor gắn đối xứng
// ===============================
void setMotorDir(float L, float R) {
  // --- Bánh TRÁI ---
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

  // --- Bánh PHẢI ---
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

void stopMotors() {
  setMotorDir(0, 0);
  ledcWrite(L_PWM_CH, 0);
  ledcWrite(R_PWM_CH, 0);
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(L_IN1, OUTPUT);
  pinMode(L_IN2, OUTPUT);
  pinMode(R_IN1, OUTPUT);
  pinMode(R_IN2, OUTPUT);
  pinMode(LED, OUTPUT);

  ledcSetup(L_PWM_CH, PWM_FREQ, PWM_RES);
  ledcAttachPin(L_PWM, L_PWM_CH);
  ledcSetup(R_PWM_CH, PWM_FREQ, PWM_RES);
  ledcAttachPin(R_PWM, R_PWM_CH);

  L_Encoder.attachFullQuad(
      L_B, L_A); // Đảo A/B để encoder trái đúng dấu (+tiến, -lùi)
  R_Encoder.attachFullQuad(R_A, R_B);
  L_Encoder.clearCount();
  R_Encoder.clearCount();

  stopMotors();
  digitalWrite(LED, HIGH);

  Serial.println("==============================");
  Serial.println("     HARDWARE TEST MODE");
  Serial.println("==============================");
  Serial.println("Lenh:");
  Serial.println("  1 = Motor TRAI tien  (L tang duong)");
  Serial.println("  2 = Motor TRAI lui   (L giam am)");
  Serial.println("  3 = Motor PHAI tien  (R tang duong)");
  Serial.println("  4 = Motor PHAI lui   (R giam am)");
  Serial.println("  5 = CA HAI tien      (L,R tang duong)");
  Serial.println("  6 = CA HAI lui       (L,R giam am)");
  Serial.println("  0 = DUNG");
  Serial.println("  r = Reset encoder ve 0");
  Serial.println("------------------------------");
  Serial.println("Kiem tra: tien => encoder tang (+), lui => giam (-)");
  Serial.println("Neu sai chieu => swap 2 day motor cua banh do");
  Serial.println("Encoder se hien thi lien tuc");
}

void loop() {
  // --- Nhận lệnh từ Serial Monitor ---
  if (Serial.available()) {
    char cmd = Serial.read();

    if (cmd == '1') {
      Serial.println("[CMD] Motor TRAI => TIEN");
      setMotorDir(1, 0);
      ledcWrite(L_PWM_CH, TEST_PWM);
      ledcWrite(R_PWM_CH, 0);
    } else if (cmd == '2') {
      Serial.println("[CMD] Motor TRAI => LUI");
      setMotorDir(-1, 0);
      ledcWrite(L_PWM_CH, TEST_PWM);
      ledcWrite(R_PWM_CH, 0);
    } else if (cmd == '3') {
      Serial.println("[CMD] Motor PHAI => TIEN");
      setMotorDir(0, 1);
      ledcWrite(L_PWM_CH, 0);
      ledcWrite(R_PWM_CH, TEST_PWM);
    } else if (cmd == '4') {
      Serial.println("[CMD] Motor PHAI => LUI");
      setMotorDir(0, -1);
      ledcWrite(L_PWM_CH, 0);
      ledcWrite(R_PWM_CH, TEST_PWM);
    } else if (cmd == '5') {
      Serial.println("[CMD] CA HAI => TIEN");
      setMotorDir(1, 1);
      ledcWrite(L_PWM_CH, TEST_PWM);
      ledcWrite(R_PWM_CH, TEST_PWM);
    } else if (cmd == '6') {
      Serial.println("[CMD] CA HAI => LUI");
      setMotorDir(-1, -1);
      ledcWrite(L_PWM_CH, TEST_PWM);
      ledcWrite(R_PWM_CH, TEST_PWM);
    } else if (cmd == '0') {
      Serial.println("[CMD] DUNG");
      stopMotors();
    } else if (cmd == 'r') {
      L_Encoder.clearCount();
      R_Encoder.clearCount();
      Serial.println("[CMD] Reset encoder = 0");
    }
  }

  // --- In encoder mỗi 300ms ---
  static uint32_t last_print = 0;
  if (millis() - last_print >= 300) {
    last_print = millis();
    int32_t L = L_Encoder.getCount();
    int32_t R = R_Encoder.getCount();
    Serial.printf("Encoder  L: %7ld  |  R: %7ld\n", L, R);
    digitalWrite(LED, !digitalRead(LED));
  }
}