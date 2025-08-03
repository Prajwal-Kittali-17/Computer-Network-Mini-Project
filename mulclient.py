import socket
import pyaudio
import threading

# Server configuration
HOST = '192.168.9.63'
PORT = 9999

# PyAudio configuration
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Function to handle sending audio data to the server
def send_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        print(f"[*] Connected to {HOST}:{PORT}")

        while True:
            data = stream.read(CHUNK_SIZE)
            client_socket.sendall(data)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        client_socket.close()

# Function to create and start a new thread for sending audio
def start_audio_thread():
    audio_thread = threading.Thread(target=send_audio)
    audio_thread.start()

# Create multiple clients
num_clients = 3
for _ in range(num_clients):
    start_audio_thread()
