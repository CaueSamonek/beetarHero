#include "BluetoothSerial.h"

BluetoothSerial BT;

const int btns[] = {27, 26, 25, 33};
bool last[] = {1, 1, 1, 1}; // 1 == HIGH == Botao Solto

void setup() {
  for (int b : btns)
    pinMode(b, INPUT_PULLUP);

  BT.begin("ESP32_Controle");
}

void loop(){
  for (int i = 0; i < 4; i++) {
    bool cur = digitalRead(btns[i]);

    if (cur != last[i]) {
      BT.printf("BTN/%d:%d\n", i + 1, !cur);
      last[i] = cur;
    }
  }

  delay(10);
}
