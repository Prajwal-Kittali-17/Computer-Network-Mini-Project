import socket
import pyaudio
import threading

# Server configuration
SERVER_IP = '192.168.9.31'  # Replace with the actual IP address of the server
SERVER_PORT = 12345

# PyAudio configuration
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Flag to control the streaming thread
streaming_active = True

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

        while streaming_active:
            try:
                data = stream.read(CHUNK_SIZE)
                client_socket.sendall(data)
            except socket.error as e:
                print(f"[ERROR] Failed to send audio data: {e}")
                break  # Break the loop on error

    except Exception as e:
        print(f"[ERROR] Connection error: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        client_socket.close()
        print("[*] Connection closed")

# Function to start the audio streaming thread
def start_audio_stream():
    global streaming_active
    streaming_active = True
    audio_thread = threading.Thread(target=send_audio)
    audio_thread.start()

# Function to stop the audio streaming thread
def stop_audio_stream():
    global streaming_active
    streaming_active = False

# Start sending audio to the server
start_audio_stream()

# Example: Keep the stream active for 10 seconds
# You can replace this with your own logic to control the duration of streaming
import time
time.sleep(30)

# Stop the audio streaming thread
stop_audio_stream()