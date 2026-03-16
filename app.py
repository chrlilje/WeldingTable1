# imports
import tkinter as tk
import threading
import queue
from ui.components import NumberBox, StatusLabel
from ui import styles
from model import WeldTable
import data_io  # this is the module that fetch our data

# main app class
class App:
    def __init__(self):
        # initialize app
        self.root = tk.Tk()
        self.root.title("Boxes and numbers")
        self.root.configure(bg=styles.BACKGROUND)
        self.status_text:str = ""

        # Connect to the model of the weld table
        self.model = WeldTable()
        self.model.state = self.model.STATE_INIT

        # Size the window to 50 % of the screen, then centre it
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        win_w    = screen_w // 2
        win_h    = screen_h // 2
        offset_x = (screen_w - win_w) // 2
        offset_y = (screen_h - win_h) // 2
        self.root.geometry(f"{win_w}x{win_h}+{offset_x}+{offset_y}")

        # Tell tkinter's grid that both columns share the available width equally,
        # and that the single row may grow to fill the window height.
        # weight=1 means: give all available extra space to this column/row.
        # uniform="boxes" forces both columns to always stay the same width,
        # so a wider value in one box cannot steal space from the other.
        self.root.columnconfigure(0, weight=1, uniform="boxes")
        self.root.columnconfigure(1, weight=1, uniform="boxes")
        self.root.rowconfigure(0, weight=1)

        # Create a Queue for thread safe data communication with the serial-thingy
        self.data_queue: queue.Queue = queue.Queue()

        # Make the boxes - User interface
        self.speedBox = NumberBox(self.root, "Speed", 23,  0, "mm/min")
        self.rpmBox   = NumberBox(self.root, "RPM",   123, 1, "rpm")
        self.statusLabel = StatusLabel(self.root, self.status_text)

        # Place the boxes
        # sticky="nsew" makes each box stretch to fill its entire grid cell.
        # The inner edges use BOX_GAP so there is more breathing room between
        # the two boxes than between a box and the window edge.
        outer = styles.BOX_OUTER_PADDING
        gap   = styles.BOX_GAP
        self.speedBox.grid(row=0, column=0, padx=(outer, gap), pady=outer, sticky="nsew")
        self.rpmBox.grid(  row=0, column=1, padx=(gap, outer), pady=outer, sticky="nsew")
        self.statusLabel.grid(row=1, column=0, columnspan=2, padx=outer, pady=(0, outer), sticky="ew")

        # Keep model text and UI label in sync from one place
        self.set_status_text("Status: Ready")

    def set_status_text(self, text: str):
        self.status_text = text
        self.statusLabel.update_text(self.status_text)

    def update_model(self):
        """Consumes the queue and updates the internal state of the Model."""
        while not self.data_queue.empty():
            try:
                packet = self.data_queue.get_nowait()
            
                if "speeder_rate" in packet:
                    self.model.set_speeder_rate(packet["speeder_rate"])
            
                if "status" in packet:
                    self.model.set_system_status(packet["status"])
                
            except queue.Empty:
                break
        

    def update_ui(self) -> None:
        """Read data from the model and update the user interface"""
        # The model has the truth - we don't look at the data or the serial port here
        self.speedBox.update_value(self.model.weld_speed)
        self.rpmBox.update_value(self.model.table_rpm)

        # One source of truth for the text
        self.set_status_text(self.model.system_status)


    def update_loop(self) -> None:
        """ This is the heartbeat of the app - handles model and ui updates"""
        # 1: Update logic and physics model from the input data_queue
        self.update_model()

        # 2: Update the visual user interface controls
        self.update_ui()

        
        # schedule the next run of the check for updates in 100ms
        self.root.after(100, self.update_loop)



    def run(self):
        # Start fetching data in another thread to keep the UI thread responsive
        data_thread = threading.Thread(
            target=data_io.fetch_data,
            args=(self.data_queue,),
            daemon=True
        )
        data_thread.start()

        # Start the "heartbeat" the updates the ui at regular intervals
        self.update_loop()

        # Start the main event loop of tkinter
        self.root.mainloop()

# main entry point
if __name__ == "__main__":
    # create app instance
    app = App()

    # run app
    app.run()
