import time
import math
from queue import Queue, Empty
import serial.tools.list_ports
import serial

USE_MOCK_DATA = False # Flip this to test the real logic
BAUD_RATE = 9600
TARGET_ID = "TABLE1"

# Only do serial transmission every 100ms
TX_INTERVAL_SECONDS = 0.1

def run_data_service(rx_queue: Queue, tx_queue: Queue):
    if USE_MOCK_DATA:
        _fetch_mock_data(rx_queue)
    else:
        _fetch_real_serial_data(rx_queue, tx_queue) # Fetch serial data and put it in the rx_queue for the app to consume

def _fetch_real_serial_data(rx_queue: Queue, tx_queue: Queue):
    """
    Main real-serial loop:
    1) Find the right port
    2) Open it
    3) Alternate between reading and writing
    4) Re-scan automatically on disconnect
    """
    # This way of finding the correct serial port loops through the ports, and find the one
    # who sends data with the expected ID (FOOT_PEDAL or something else)
    # This way we don't have to concern ourselves with what port the actual arduino is connected to
    # we just search for the one who speaks the right ID
    while True:
        # --- PHASE 1: SEARCH ---
        # This code only runs when we DON'T have a port.
        port_name = _find_port(rx_queue)
        
        if not port_name:
            time.sleep(1)
            continue # Goes back to the start of 'while True' to search again
            
        # --- PHASE 2: STREAM ---
        # If we reach here, we FOUND a port. 
        # We enter a NEW loop that traps the code here as long as the port works.
        # --- PHASE 2: OPEN + SERVICE ---
        try:
            # timeout=0 means non-blocking read calls.
            # This allows us to alternate read/write without blocking for 2 seconds.
            with serial.Serial(port_name, BAUD_RATE, timeout=0) as ser:
                rx_queue.put({"status": f"Connected to {port_name}"})

                # Last successful transmit time for rate limiting
                last_tx_time = 0.0

                # Keep only the newest outgoing command packet
                latest_tx_packet = None

                while True:
                    # Step A: Try one read cycle (non-blocking)
                    _read_once(ser, rx_queue)

                    # Step B: Drain TX queue and keep only newest command
                    latest_tx_packet = _drain_tx_queue_keep_latest(tx_queue, latest_tx_packet)

                    # Step C: Send at most once every 100ms
                    now = time.monotonic()
                    if latest_tx_packet is not None and (now - last_tx_time) >= TX_INTERVAL_SECONDS:
                        tx_line = _build_tx_line(latest_tx_packet)
                        if tx_line is not None:
                            ser.write(tx_line.encode("utf-8"))
                            last_tx_time = now

                        # We sent the newest packet, so clear it.
                        # If app queues newer data, it will be picked up in next loops.
                        latest_tx_packet = None

                    # Tiny sleep to avoid spinning CPU at 100%
                    time.sleep(0.01)

        except (serial.SerialException, OSError):
            rx_queue.put({"status": "Lost Connection. Re-scanning..."})

def _read_once(ser: serial.Serial, rx_queue: Queue):
    """
    Read one line if data is available.
    Non-blocking mode means this returns quickly when no data is present.
    """
    try:
        # Read one line. In non-blocking mode this is quick.
        raw = ser.readline()
        if not raw:
            return

        line = raw.decode("utf-8", errors="ignore").strip()
        if not line:
            return

        payload = _parse_line(line)
        if payload:
            rx_queue.put(payload)

    except (serial.SerialException, OSError):
        # Let outer loop reconnect by re-raising
        raise


def _parse_line(line: str) -> dict | None:
    """
    Input: "ID:TABLE1;PEDPOS:50.00;RPM:750"
    Output: {"speeder_rate": 50.0, "rpm": 750.0}
    """
    try:
        parts = line.split(';')
        data = {}
        for part in parts:
            if ':' in part:
                key, value = part.split(':')
                if key == "PEDPOS":
                    data["speeder_rate"] = float(value)
                elif key == "RPM":
                    data["rpm"] = float(value)
        return data
    except (ValueError, IndexError):
        # If the string was malformed (e.g., "SPD:50.0;RP"), just ignore it
        return None
    
def _drain_tx_queue_keep_latest(tx_queue: Queue, current_latest: dict | None) -> dict | None:
    """
    Pull all queued TX packets and keep only the latest one.
    This prevents backlog if app produces updates faster than serial send rate.
    """
    latest = current_latest
    while True:
        try:
            latest = tx_queue.get_nowait()
        except Empty:
            break
    return latest


def _build_tx_line(packet: dict) -> str | None:
    """
    Convert tx packet dict into protocol line:
    Input dict: {"stepper_speed": 123, "stepper_acc": 213}
    Output line: "S123,A213\\n"
    """
    # Check required keys
    if "stepper_speed" not in packet or "stepper_acc" not in packet:
        return None

    try:
        # Convert to integers for the wire format
        speed = int(round(float(packet["stepper_speed"])))
        acc = int(round(float(packet["stepper_acc"])))
    except (TypeError, ValueError):
        return None

    return f"S{speed},A{acc}\n"

def _find_port(rx_queue: Queue) -> str | None:
    """Scan all ports and look for our TARGET_ID"""
    ports = serial.tools.list_ports.comports()
    for p in ports:
        rx_queue.put({"status": f"Checking {p.device}..."})
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
