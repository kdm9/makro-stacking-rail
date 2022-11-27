#include <Arduino.h>

int MOTOR_STEPS = 400;
int MOTOR_ACCEL = 2000;
int MOTOR_DECEL = 2000;
int RPM = 120;

// stoppers are active low, i.e. pulled to ground if the stopper is hit
int PINI_POSSTOP = 4;
int PINI_NEGSTOP = 15;

int PINI_NFAULT = 34;

int PIN_ENBL = 32;
int PIN_DIR = 22;
int PIN_STEP = 23;
int PIN_M2 = 21;
int PIN_M1 = 19;
int PIN_M0 = 18;

#include "DRV8825.h"
DRV8825 stepper(MOTOR_STEPS, PIN_DIR, PIN_STEP, PIN_ENBL, PIN_M0, PIN_M1, PIN_M2);

void setup() {
    Serial.begin(115200);
    stepper.begin(RPM);
    stepper.enable();
    pinMode(PINI_POSSTOP, INPUT_PULLUP);
    pinMode(PINI_NEGSTOP, INPUT_PULLUP);
    //pinMode(PIN_ENBL, OUTPUT);
    //digitalWrite(PIN_ENBL, LOW);
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
            float speed = Serial.parseFloat();
            stepper.setRPM(speed);
            Serial.print("OK # speed now ");
            Serial.println(speed);
    } else if (c == 'U') {
            int ustep = Serial.parseInt();
            int res = stepper.setMicrostep(ustep);
            if (res != ustep) {
                Serial.println("FAIL # ustep mismatch");
            } else {
                Serial.print("OK # ustep now ");
                Serial.println(res);
            }
    } else if (c == 'M') {
            long move = Serial.parseInt();
            stepper.startMove(move);
            while (true) {
                //Serial.print("#POS ");
                //Serial.print(digitalRead(PINI_POSSTOP));
                //Serial.print(" NEG ");
                //Serial.println(digitalRead(PINI_NEGSTOP));
                int at_stop = digitalRead(move > 0 ? PINI_POSSTOP : PINI_NEGSTOP);
                if (at_stop) {
                    long remaining = stepper.stop();
                    Serial.print("FAIL # Hit stopper with ");
                    Serial.print(remaining);
                    Serial.println(" moves left");
                    break;
                }
                long wait_time_micros = stepper.nextAction();
                if (wait_time_micros <= 0) {
                    Serial.print("OK # moved ");
                    Serial.println(move);
                    break;
                }
            }
    } else if (c == -1 || isSpace(c)) {
        return;
    } else {
            char chr = c;
            Serial.print("FAIL # bad input ");
            Serial.println(chr);
    }
    Serial.flush();
}
