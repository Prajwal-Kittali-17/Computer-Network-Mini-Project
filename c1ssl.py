import socket
import pyaudio
import ssl

# Server configuration
SERVER_HOST = '10.1.20.217'
SERVER_PORT = 12345

# PyAudio configuration
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# SSL configuration
CERT_FILE = r"path/to/your/client_certificate.pem"
KEY_FILE = r"path/to/your/client_private_key.pem"

def send_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK_SIZE)

    try:
        # Create an SSL context
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

        # Create a socket and connect to the server
        with context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as client_socket:
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            print(f"[*] Connected to {SERVER_HOST}:{SERVER_PORT}")

            while True:
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

if _name_ == "_main_":
    send_audio()