#include <avr/io.h>
#include <util/delay.h>

//int steps[] = {0x1, 0x3, 0x2, 0x6, 0x4, 0xc, 0x8, 0x9};
int steps[] = {0x9, 0x8, 0xc, 0x4, 0x6, 0x2, 0x3, 0x1};
int curstep = 50;
int offset = 0; // since track 0 might be at some weird phase

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  DDRA = 0x0F; // four outputs
  PORTA = 0x00;
  
  DDRC = 0xFF;
  PORTC = 0xFF; // blank it for now

  // Zero it out
  stepto(0);

  Serial.println("Key commands:");
  Serial.println("z - Set current location as track 0");
  Serial.println("F, f - Fine step. Capital +, lowercase -");
  Serial.println("S, s - 48TPI step.");
  Serial.println("C, c - 32TPI step.");
  Serial.println("h - Move to position 0.");
}

void disp(int num) {
  int ones = num % 10;
  int tens = (num / 10) % 10;
  PORTC = ones | (tens << 4);
}

void outstep() {
  PORTA = steps[(curstep + offset) & 0x7];
  delay(25);
}

void stepto(int loc) {
  int incr = 1;
  if (curstep == loc) return;
  if (curstep > loc) incr = -1;
  while (curstep != loc) {
    curstep += incr;
    outstep();
  }
}

void moveby(int delta) {
  int incr = 1;
  if (delta < 0) incr = -1;
  while (delta != 0) {
    curstep += incr;
    outstep();
    delta -= incr;
  }
}

void printloc() {
  float tpipos = curstep / 3.0f;
  Serial.print("Raw: ");
  Serial.print(curstep, DEC);
  Serial.print(" - 48TPI: ");
  Serial.print(curstep >> 1, DEC);
  Serial.print(".");
  Serial.print((curstep & 1) ? "5" : "0");
  Serial.print(" - 32TPI: ");
  Serial.print(tpipos, 1);
  Serial.println("");
  disp(tpipos);
}

void loop() {
  uint8_t b;
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    b = Serial.read();
    
    // Current location is track 0
    if (b == 'z') {
      offset = (curstep + offset) & 0x7;
      curstep = 0;
      printloc();
    }

    // Fine step
    if (b == 'F' || b == 'f') {
      if (b == 'F') curstep++;
      if (b == 'f') curstep--;
      outstep();
      printloc();
    }

    // 48TPI movement
    if (b == 'S' || b == 's') {
      if (b == 'S') moveby(2);
      if (b == 's') moveby(-2);
      printloc();
    }

    // 32TPI movement
    if (b == 'C' || b == 'c') {
      if (b == 'C') moveby(3);
      if (b == 'c') moveby(-3);
      printloc();
    }

    // Go home
    if (b == 'h') {
      stepto(0);
      printloc();
    }
    
  }
}
