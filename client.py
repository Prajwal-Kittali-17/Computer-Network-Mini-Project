import socket
import pyaudio

# Constants
SERVER_IP = '192.168.9.63'
SERVER_PORT = 12345
BUFFER_SIZE = 1024

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Create UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Audio setup
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=BUFFER_SIZE)

# Main client loop
try:
    while True:
        data = stream.read(BUFFER_SIZE)
        client_socket.sendto(data, (SERVER_IP, SERVER_PORT))
except KeyboardInterrupt:
    pass

# Cleanup
stream.stop_stream()
stream.close()
p.terminate()
client_socket.close()