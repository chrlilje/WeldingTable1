int serialPedalSpeed = 9600;

void setupSerialPedal() {
  // setup serial port and baud for the RPi com via USB
  // Can be 115200 since good connection and to get fast operations = Low latency
  Serial1.begin(serialPedalSpeed);
}

void readSerialFromPedal() {
  // Read a char and put it in the buffer.
  static int index = 0;  // Index pointer for the buffer?

  if (Serial1.available() > 0) {
    // Read incoming char
    char c = Serial1.read();  // Read an incoming char
    dataFromPedalBuffer[index] = c;

    // Check for newline = end of message
    if (c == '\n') {
      fullLineFromPedalArrived = true;
      index = 0;
    } else {
      index++;
      // Check for overflow of pointer and reset to 0
      if (index > 127) {
        index = 0;
      }
    }
  }
}

void writeSerialToPedal(){
  // To be implemented
}