//// Foot pedal for welding table - version 0.1
/*
Operation:
  - Read analog input
  - maybe apply some smoothing using a running average
  - send the value to the HC-12 
*/

// Pins
int potmeterPin = A0;

// Smoothing 
float averagePct = 0.0;
unsigned long sendTime = 0;
unsigned long sendDelay = 100;


void setup() {
  Serial.begin(9600);
  Serial1.begin(9600);

  // Set up the power pins for the Potentiometer
  pinMode(potmeterPin, OUTPUT);

  // Give the serial port a moment to stabilize
  // delay(500);
}


void loop() {
  readAnalogValue(); // read, smooth and store

  serialSendTimed(); // At intervals (100ms?) compose serial message and send it
}


float readAnalogValue(){
  // 1. Read the raw 10-bit value (0 to 1023)
  int rawValue = analogRead(potmeterPin);

//  Serial.println(rawValue);

  // 2. Map it to a percentage (0.0 to 100.0)
  // We use float for precision
  float percentage = (rawValue / 1023.0) * 100.0;

  // Running average smoothing the pedal data
  averagePct = 0.01*percentage + 0.99*averagePct;
}

void serialSendTimed(){
  // Send if it is time to send (millis has grown over timeToSend)
  if(millis() - sendTime > sendDelay){
    float val = averagePct; // Get the stored average value. Maybe we will round it later???

    // Serial1 is connected to the HC-10
    // We should make a checksum at some point???
    Serial1.print("I1234,P");
    Serial1.println(val,0); // 1 decimal place

    // Send the same to the serial port usb for debugging
    Serial.print("I1234,P");
    Serial.println(val,0); // 1 decimal place

    sendTime = millis();
  }

}