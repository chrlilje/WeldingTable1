void setupStepper() {
  // Set the maximum speed (Steps per second)
  tableStepper.setMaxSpeed(stepperMaxSpeed);

  // And acceleration (Steps per second, per second)
  // Notice: acceleration is not used when using runSpeed()
  tableStepper.setAcceleration(stepperAcceleration);

  // Set start position as current position
  tableStepper.setCurrentPosition(0);

  // Enable drivers
  // ??? At some point possibly implement enable/disable linked to emergency stop
  digitalWrite(stepEnablePin, LOW);
}

void setStepperSpeed(long value) {
  // ??? Here we should implement "rails" to guard against illegal speed values
  stepperSpeed = value;

  // Set the speed of accelStepper library
  tableStepper.setSpeed(stepperSpeed);
  
}

void setStepperAcceleration(long value) {
  // Here we should implement rails to guard against illegal acceleration values
  stepperAcceleration = value;
  // Set the acceleration accelStepper will follow
  tableStepper.setAcceleration(stepperAcceleration);
}

void handleStepper() {
  // Hard stop if the emergency stop is pressed???
  // Here we call the run function of the accelStepper library
  tableStepper.runSpeed();
}
