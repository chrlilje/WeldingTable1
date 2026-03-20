void setup() {
  // USB Serial
  Serial.begin(9600); 
  
  // Hardware Serial 1 (GP0 TX, GP1 RX)
  Serial1.begin(9600); 
}

void loop() {
  // Read from Serial1, write to USB Serial
  if (Serial1.available()) {
    Serial.write(Serial1.read());
  }

  // Optional: Read from USB Serial, write to Serial1 
  // (Handy for sending commands back to the device)
  if (Serial.available()) {
    Serial1.write(Serial.read());
  }
}