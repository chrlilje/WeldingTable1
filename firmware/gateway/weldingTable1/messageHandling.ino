
unsigned long lastTimeMessageToRpi = 0;
unsigned long messageToRpiDelay = 400;

void messageToRpiTime(){
  // Is it time to send a message?
  if(millis() - lastTimeMessageToRpi >= messageToRpiDelay){
    if(fullLineToRpiReady == false){
      messageToRpi(); // Construct and send message

      // Set the time to send again forward by the delay
      lastTimeMessageToRpi = millis();
    }
  }
}

void messageToRpi(){
  if(fullLineToRpiReady) {return;} // A line is already waiting to be sent - DOnt add a new. Return immediately from here

/*  // Construct the message
  // This is the simplified message format for faster reading at the arduino
  String message = "ID:TABLE1";
  message += ",S" + String(stepperSpeed);
  message += ",A" + String(stepperAcceleration);
  message += ",P" + String(pedalPosition);
  message += ",B" + String(buttonPosition);
*/
  // Construct the message
  String message = "ID:TABLE1";
  message += ";SSPEED:" + String(stepperSpeed);
  message += ";ACC:" + String(stepperAcceleration);
  message += ";PEDPOS:" + String(pedalPosition);
  message += ";BUTPOS:" + String(buttonPosition);

  // fill the message into the buffer
  int length = message.length();
  int i = 0; // We want to know the last index
  for(i = 0; i < length && i < 126;i++){
    dataToRpiBuffer[i] = message[i];
  }
  // Add \n for termination
  dataToRpiBuffer[i] = '\n';
  dataToRpiIndex = 0;
  fullLineToRpiReady = true; // Mark that a line is ready to be sent

}

