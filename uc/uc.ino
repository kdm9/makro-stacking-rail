#include <Arduino.h>

int MOTOR_STEPS = 400;
int MOTOR_ACCEL = 600;
int MOTOR_DECEL = 600;
int RPM = 120;

int PIN_DIR = 3;
int PIN_STEP = 4;
int PIN_SLEEP = 8;
int PIN_M2 = 5;
int PIN_M1 = 6;
int PIN_M0 = 7;

#include "DRV8825.h"
DRV8825 stepper(MOTOR_STEPS, PIN_DIR, PIN_STEP, PIN_SLEEP, PIN_M0, PIN_M1, PIN_M2);

void setup() {
    Serial.begin(115200);
    stepper.begin(RPM);
    stepper.enable();
    pinMode(PIN_SLEEP, OUTPUT);
    digitalWrite(PIN_SLEEP, HIGH);
    stepper.setSpeedProfile(stepper.LINEAR_SPEED, MOTOR_ACCEL, MOTOR_DECEL);

    Serial.println("READY");
    Serial.setTimeout(10);
}

void loop() {
    if (Serial.available() < 1) {
        return;
    }
    int c = Serial.read();
    if (c == 'S') {
            float speed = Serial.parseFloat(SKIP_NONE);
            stepper.setRPM(speed);
            Serial.print("OK # speed now ");
            Serial.println(speed);
    } else if (c == 'U') {
            int ustep = Serial.parseInt(SKIP_NONE);
            int res = stepper.setMicrostep(ustep);
            if (res != ustep) {
                Serial.println("FAIL # ustep mismatch");
            } else {
                Serial.print("OK # ustep now ");
                Serial.println(res);
            }
    } else if (c == 'M') {
            long move = Serial.parseInt(SKIP_NONE);
            stepper.move(move);
            Serial.print("OK # moved ");
            Serial.println(move);
            
    } else if (c == -1 || isSpace(c)) {
        return;
    } else {
            char chr = c;
            Serial.print("FAIL # bad input ");
            Serial.println(chr);
    }
    Serial.flush();
}
