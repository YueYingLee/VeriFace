from threading import Event

# Event to control RFID polling and facial recognition
rfid_event = Event()
rfid_event.set()  # Start with RFID scanning enabled

# Event to control when to end attendance
end_event = Event()
end_event.clear()   # start with end_event cleared
