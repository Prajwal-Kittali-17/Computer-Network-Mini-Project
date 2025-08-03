import socket
import pyaudio
import ssl

# Server configuration
SERVER_IP = '192.168.43.16'  # Replace with the actual IP address of the server
SERVER_PORT = 12345

# PyAudio configuration
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Function to send audio data to the server without SSL certificate verification
def send_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Wrap the socket with SSL, disabling certificate verification
        ssl_client_socket = ssl.wrap_socket(client_socket, ssl_version=ssl.PROTOCOL_TLS, cert_reqs=ssl.CERT_NONE)

        ssl_client_socket.connect((SERVER_IP, SERVER_PORT))
        print(f"[*] Connected to {SERVER_IP}:{SERVER_PORT} with SSL certificate verification")

        while True:
            data = stream.read(CHUNK_SIZE)
            ssl_client_socket.sendall(data)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        ssl_client_socket.close()

# Start sending audio to the server without SSL certificate verification
send_audio()