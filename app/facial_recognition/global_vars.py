import queue
from threading import Event

frame_queue = queue.Queue()

# Event to control when to end attendance
end_event = Event()
end_event.clear()   # start with end_event cleared