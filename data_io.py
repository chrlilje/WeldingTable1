import time
import math
import random
from queue import Queue
import serial.tools.list_ports
import serial

USE_MOCK_DATA = True # Flip this to test the real logic
BAUD_RATE = 9600
TARGET_ID = "FOOT_PEDAL"

def fetch_data(data_queue: Queue):
    if USE_MOCK_DATA:
        _fetch_mock_data(data_queue)
    else:
        _fetch_real_serial_data(data_queue)

def _fetch_real_serial_data(data_queue: Queue):
    # This way of finding the correct serial port loops through the ports, and find the one
    # who sends data with the expected ID (FOOT_PEDAL or something else)
    # This way we don't have to concern ourselves with what port the actual arduino is connected to
    # we just search for the one who speaks the right ID
    while True:
        # --- PHASE 1: SEARCH ---
        # This code only runs when we DON'T have a port.
        port_name = _find_port(data_queue)
        
        if not port_name:
            time.sleep(2)
            continue # Goes back to the start of 'while True' to search again
            
        # --- PHASE 2: STREAM ---
        # If we reach here, we FOUND a port. 
        # We enter a NEW loop that traps the code here as long as the port works.
        try:
            with serial.Serial(port_name, BAUD_RATE, timeout=2) as ser:
                data_queue.put({"status": f"Connected to {port_name}"})
                
                while True: # <--- This is your "port_found = True" flag in loop form
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        payload = _parse_line(line)
                        if payload:
                            data_queue.put(payload)
                            
        except (serial.SerialException, OSError):
            # If the cable is pulled, the inner 'while' crashes.
            # We land here, the 'with' block closes the port automatically,
            # and the outer 'while True' starts again at PHASE 1.
            data_queue.put({"status": "Lost Connection. Re-scanning..."})

def _parse_line(line: str) -> dict | None:
    """
    Input: "ID:FOOT_PEDAL;SPD:50.00;RPM:750"
    Output: {"speed": 50.0, "rpm": 750.0}
    """
    try:
        parts = line.split(';')
        data = {}
        for part in parts:
            if ':' in part:
                key, value = part.split(':')
                if key == "SPD":
                    data["speed"] = float(value)
                elif key == "RPM":
                    data["rpm"] = float(value)
        return data
    except (ValueError, IndexError):
        # If the string was malformed (e.g., "SPD:50.0;RP"), just ignore it
        return None

def _find_port(data_queue: Queue) -> str | None:
    """Scan all ports and look for our TARGET_ID"""
    ports = serial.tools.list_ports.comports()
    for p in ports:
        data_queue.put({"status": f"Checking {p.device}..."})
        try:
            with serial.Serial(p.device, BAUD_RATE, timeout=1) as ser:
                # Wait a moment for Arduino to reboot/send first string
                time.sleep(1.5) 
                response = ser.readline().decode('utf-8', errors='ignore')
                if TARGET_ID in response:
                    return p.device
        except (serial.SerialException, OSError):
            continue
    return None

def _fetch_mock_data(data_queue: Queue):
    """
    Generates a smooth 0-100% speeder signal using a sine wave.
    This simulates a foot pedal being pressed and released every 10 seconds.
    """
    data_queue.put({"status": "Mode: Simulation (Sine Wave)"})
    
    # Speed of the oscillation (lower = slower)
    # 0.628 means one full cycle (0 -> 100 -> 0) every ~10 seconds
    frequency = 0.0628 
    
    while True:
        # 1. Get current time to use as the 'angle' for sine
        t = time.time()
        
        # 2. Calculate Sine (result is -1.0 to 1.0)
        raw_sin = math.sin(t * frequency)
        
        # 3. Shift and Scale to 0.0 - 100.0
        # (raw_sin + 1) gives 0 to 2. Multiplying by 50 gives 0 to 100.
        percentage = (raw_sin + 1) * 50.0
        
        # 4. Create the payload
        # Note: We send 'speeder_rate' so the Model can calculate 
        # the resulting RPM and Weld Speed based on your physics.
        payload = {
            "speeder_rate": round(percentage, 2)
        }
        
        data_queue.put(payload)
        
        # Update at 10Hz (100ms) for a smooth "needle" movement
        time.sleep(0.1)
