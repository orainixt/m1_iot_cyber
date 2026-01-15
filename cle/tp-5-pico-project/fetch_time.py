import serial
from datetime import datetime

pico = serial.Serial('/dev/ttyACM0', 115200)
now = datetime.now()
pico.write(f"{now.hour:02d}:{now.minute:02d}:{now.second:02d}\n".encode())

