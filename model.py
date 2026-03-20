import math

class WeldTable:
    # State Constants
    STATE_INIT = "INITIALIZING"
    STATE_LOCKED = "WAITING_FOR_ZERO"
    STATE_RUNNING = "RUNNING"

    def __init__(self):
        self.state = self.STATE_INIT
        self.system_status = "Initializing..."
        
        # Configuration
        self.object_diameter = 10.0
        self.max_weld_speed = 200.0
        self.stepper_steps_per_revolution = 400  # Example value, adjust as needed
        # TODO: Make a config file or UI to set these values, and persist them across runs.

        # Values
        self.speeder_rate = 0.0
        self.weld_speed = 0.0
        self.table_rpm = 0.0
        self.stepper_speed = 0.0  # Speed in steps/sec for the stepper motor (derived from weld_speed and object_diameter)
        self.stepper_acc = 0.0 # Placeholder for future acceleration control

    def set_system_status(self, message: str):
        """Allows the Controller to pass hardware/port status into the Model."""
        self.system_status = message

    def set_speeder_rate(self, raw_percentage: float):
        """
        The 'Logic Scan' - Handles state transitions and calculations
        """
        # 1. Update the raw input - Secure against the rails
        self.speeder_rate = max(0.0, min(100.0, raw_percentage))

        # When we have changed a value, we call the _handle_state to see if a state change will happen
        self._handle_state()


    def _handle_state(self):
        # 2. State Machine Logic (The PLC principle)
        if self.state == self.STATE_INIT:
            # Transition to Locked immediately to start checking for zero
            self.state = self.STATE_LOCKED

        if self.state == self.STATE_LOCKED:
            # Guard Condition: Only transition to state running if the pedal is near zero (e.g., < 1%)
            if self.speeder_rate < 1.0:
                self.state = self.STATE_RUNNING
            
        self._calculate_physics()

    def _calculate_physics(self):
        """Internal method to update dependent values"""
        self.weld_speed = (self.speeder_rate / 100.0) * self.max_weld_speed
        
        if self.object_diameter > 0:
            circumference = math.pi * self.object_diameter
            self.table_rpm = self.weld_speed / circumference
        else:
            self.table_rpm = 0.0

        # Calculate stepper speed (example calculation - adjust as needed)
        self.stepper_speed = self.table_rpm * self.stepper_steps_per_revolution  # Replace 100 with actual steps per revolution