// Include the AccelStepper Library
#include <AccelStepper.h>

// Define motor interface type. 1 = Stepper with Driver
#define motorInterfaceType 1

// GP0 : Serial1 Tx -> HC-12 Rx     - pin1
// GP1 : Serial1 Rx -> HC-12 Tx     - pin2
// GND for HC-12                    - pin3
//                                  - pin4
const int stepStepPin   = 3; // GP3 - pin5
const int stepDirPin    = 4; // GP4 - pin6
const int stepEnablePin = 5; // GP5 - pin7
//                              GND - pin8
const int encoderAPin   = 6; // GP6 - pin9
const int encoderBPin   = 7; // GP7 - pin10
const int btn1Pin       = 8; // GP8 - pin11
const int btn2Pin       = 9; // GP9 - pin12
//                              GND - pin13

const int ledPin1       = 25; // InternalLed pin on the pico


// Create an instance of the AccelStepper object
AccelStepper tableStepper(motorInterfaceType, stepStepPin, stepDirPin);

// data variables for state and values

long stepperSpeed = 0; // Steps pr minute
long stepperMaxSpeed = 800;
long stepperAcceleration = 200; // Acceleration not used in runSpeed mode
long pedalPosition = 0;
long pedalButton = 0; // the state of the button of the pedal. Future option
long buttonPosition = 0; 


// Buffers for incoming and outgoing communication
char dataFromRpiBuffer[128];
char dataToRpiBuffer[128]; // data buffers for serial data
char dataFromPedalBuffer[128];

bool fullLineFromRpiArrived = false;
bool fullLineFromPedalArrived = false;
bool fullLineToRpiReady = false; // A message to the Rpi has been constructed and is to be sent
long dataToRpiIndex = 0;

void setup() {
  setupSerialRpi(); // Using the Serial port for USB
  setupSerialPedal(); // Using Serial1 
  setupPins(); // Setup pinmodes.
  setupInterrupts();
  setupStepper(); // Setup initial values for the accelstepper
}

void loop() {
  // Function calls that need to happen evenry loop

  // ??? At some point we should implement a state machine, that handles if the Pi is unresponsive

  readSerialFromRPi(); // Read a char from the USB-serial port and write it to the dataFromRpiBuffer
  writeSerialToRPi(); // Write one char from the dataToRpiBuffer to the USB-serial port 
  readSerialFromPedal(); // read a char from the Pedal-serial port and write it to dataFromPedalBuffer
  writeSerialToPedal(); // Not implemented yet.
  handleStepper(); // Stepper related functions. Called often to run smooth. NB: Has safety built in??? 

  // Function that is done as needed
  handleDataFromRPi(); // Read incoming data from Rpi and set variables to the values
  handleDataFromPedal(); // Read incoming data from the Pedal and set variables accordingly

  // functions that run at timed interval
  messageToRpiTime();  // Construct message to send to the RPi from data variables
}
