import socket
import pyaudio
import ssl
import time

# Server configuration
SERVER_IP = '192.168.75.31' 
SERVER_PORT = 12345

# PyAudio configuration
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Function to send audio data to the server with SSL certificate verification
def send_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)

    client_socket = None  # Initialize the variable outside the try block

    start_time = time.time()  # Record the start time

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Manually create an SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.check_hostname = False  
        context.verify_mode = ssl.CERT_NONE  

        # Wrap the socket with SSL using the context
        ssl_client_socket = context.wrap_socket(client_socket, server_hostname=SERVER_IP)

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
        if client_socket:
            client_socket.close()

        end_time = time.time()  # Record the end time
        total_duration = end_time - start_time
        print(f"[*] Sent audio for {total_duration:.2f} seconds.")

# Start sending audio to the server with SSL certificate verification
send_audio()







# Function to receive audio data from the server with SSL certificate verification
def receive_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    frames_per_buffer=CHUNK_SIZE)

    client_socket = None  # Initialize the variable outside the try block

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Manually create an SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # Wrap the socket with SSL using the context
        ssl_client_socket = context.wrap_socket(client_socket, server_hostname=SERVER_IP)

        ssl_client_socket.connect((SERVER_IP, SERVER_PORT))
        print(f"[*] Connected to {SERVER_IP}:{SERVER_PORT} with SSL certificate verification")

        while True:
            # Receive audio data from the server
            data = ssl_client_socket.recv(CHUNK_SIZE)
            if not data:
                break

            # Play the received audio data locally
            stream.write(data)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        if client_socket:
            client_socket.close()

# Start receiving audio from the server with SSL certificate verification
receive_audio()