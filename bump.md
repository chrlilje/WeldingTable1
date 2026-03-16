        # Drain the queue and display the latest data
        latest_data = None

        while not self.data_queue.empty():
            try:
                # get_nowait means: Get data immediately. If nothing is there, it raises queue.Empty exception
                latest_data = self.data_queue.get_nowait() 
            except queue.Empty:
                # Safe way to handle if the queue was emptied somewhere else for some reason
                break # break from the 'while not self.data_queue.empty()'

        if latest_data is not None:
            # keys match what data_io.py sends into the queue
            if "speed" in latest_data:
                self.speedBox.update_value(latest_data["speed"])
            if "rpm" in latest_data:
                self.rpmBox.update_value(latest_data["rpm"])
            if "status" in latest_data:
                self.set_status_text(latest_data["status"])