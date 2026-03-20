void handleDataFromRPi() {
  // Only move on, if a full line is available
  if (fullLineFromRpiArrived == false) {
    return;  // Quits the function and jumps out immediately
  }

  // ??? To be implemented: Checksum XOR

  char* bufferPointer = dataFromRpiBuffer;  // set bufferPointer to point at the address of the first element in the dataFromRpiBuffer-array

  // Set a timer to always break after a set periode of time
  // ??? Maybe change to the overflow safe version
  unsigned long dataParsingEndTime = millis() + 100;  // We will not allow the parsing to take more than 100 ms

  // Loop through the data in the array using the bufferPointer until \n = end of line
  while (*bufferPointer != '\n') {
    // Jump over spaces and kommas
    if (*bufferPointer == ' ' || *bufferPointer == ',') {
      bufferPointer++;
    }
    // Is the next char a letter, then it is a command
    if (isAlpha(*bufferPointer)) {
      char commandType = *bufferPointer; // Save the command for the if-statements
      bufferPointer++;  // Move to the start of the number

      /* strtol - String To long - Get the number sent for the command
        gets the address of bufferPointer with &bufferPoiner, to make bufferPointer point
        to the next element after the number*/
      long parsedValue = strtol(bufferPointer, &bufferPointer, 10);

      // Handle the various commands and set the variables
      if (commandType == 'S') setStepperSpeed(parsedValue);
      if (commandType == 'A') setStepperAcceleration(parsedValue);
    } else {
      // Advance pointer to account for other chars
      bufferPointer++;
    }

    // check for timeout
    if (millis() > dataParsingEndTime) {
      // Failsafe to always exit the parsing function after 100 ms
      fullLineFromRpiArrived = false;  //Ignore this data line and wait for next
      break;
    }
  }
  // While loop done - all is parsed
  fullLineFromRpiArrived = false; // ready for parsing a new line
}

void handleDataFromPedal() {
  // Only move on, if a full line is available
  if (fullLineFromPedalArrived == false) {
    return;  // Quits the function and jumps out immediately
  }
  
  // ??? To be implemented: Checksum XOR

  char* bufferPointer = dataFromPedalBuffer;  // set bufferPointer to point at the address of the first element in the dataFromPedalBuffer-array

  // Set a timer to always break after a set periode of time
  unsigned long dataParsingEndTime = millis() + 100;  // We will not allow the parsing to take more than 100 ms

  // Loop through the data in the array using the bufferPointer until \n = end of line
  while (*bufferPointer != '\n') {
    // Jump over spaces and kommas
    if (*bufferPointer == ' ' || *bufferPointer == ',') {
      bufferPointer++;
    }

    // Is the next char a letter, then it is a command
    if (isAlpha(*bufferPointer)) {
      char commandType = *bufferPointer;  // Save the command for the if-statements
      bufferPointer++;  // Move to the start of the number

      /* strtol - String To long - Get the number sent for the command
        gets the address of bufferPointer with &bufferPointer, to make bufferPointer point
        to the next element after the number */
      long parsedValue = strtol(bufferPointer, &bufferPointer, 10);

      // Handle the various commands and set the variables
      if (commandType == 'P') setPedalPosition(parsedValue);
      if (commandType == 'B') setPedalButtonState(parsedValue);
    } else {
      // Advance pointer to account for other chars
      bufferPointer++;
    }

    // check for timeout
    if (millis() > dataParsingEndTime) {
      // Failsafe to always exit the parsing function after 100 ms
      fullLineFromPedalArrived = false;  // Ignore this data line and wait for next
      break;
    }
  }

  // While loop done - all is parsed
  fullLineFromPedalArrived = false;  // ready for parsing a new line
}