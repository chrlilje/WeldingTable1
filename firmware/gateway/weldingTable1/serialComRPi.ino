int serialRPiSpeed = 115200;

void setupSerialRpi() {
  // setup serial port and baud for the RPi com via USB
  // Can be 115200 since good connection and to get fast operations = Low latency
  Serial.begin(serialRPiSpeed);
}

void readSerialFromRPi() {
  // Read a char and put it in the buffer.
  static int index = 0;  // Index pointer for the buffer?

  if (Serial.available() > 0) {
    // Read incoming char
    char c = Serial.read();  // Read an incoming char
    dataFromRpiBuffer[index] = c;

    // Check for newline = end of message
    if (c == '\n') {
      fullLineFromRpiArrived = true;
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

void writeSerialToRPi(){
  // Check if a full line is ready
  if (fullLineToRpiReady) {
    char charToSend = dataToRpiBuffer[dataToRpiIndex];
    
    Serial.write(charToSend); // Send the char

    // If the char is \n we have sent the whole line and we reset.
    if (charToSend == '\n') {
      fullLineToRpiReady = false; 
      dataToRpiIndex = 0;
    } else {
      dataToRpiIndex++;
    }
  }
}