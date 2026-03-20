

void setupPins(){
  // --- Stepper Motor Output ---
  pinMode(stepStepPin,   OUTPUT);
  pinMode(stepDirPin,    OUTPUT);
  pinMode(stepEnablePin, OUTPUT);
  digitalWrite(stepEnablePin, HIGH); // HIGH = disabled - Low = enabled

  // --- Input with Pullups
  pinMode(encoderAPin,   INPUT_PULLUP); // needed when we use interrupts? 
  pinMode(encoderBPin,   INPUT_PULLUP);
  pinMode(btn1Pin,       INPUT_PULLUP);
  pinMode(btn2Pin,       INPUT_PULLUP);

  // --- Status LED ---
  pinMode(ledPin1,       OUTPUT);
}