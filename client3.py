import socket
import pyaudio

# Server configuration
SERVER_IP = '192.168.9.31'  # Replace with the actual IP address of the server
SERVER_PORT = 3333

# PyAudio configuration
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Function to send audio data to the server
def send_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))
        print(f"[*] Connected to {SERVER_IP}:{SERVER_PORT}")

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

# Start sending audio to the server
send_audio()