import socket
import pyaudio

# Server configuration
SERVER_HOST = '192.168.9.31'
SERVER_PORT = 12345

# PyAudio configuration
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (SERVER_HOST, SERVER_PORT)

    try:
        client_socket.connect(server_address)
        print(f"[*] Connected to {server_address}")

        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK_SIZE)

        while True:
            data = stream.read(CHUNK_SIZE)
            client_socket.sendall(data)

    except KeyboardInterrupt:
        print("[*] Client shutting down.")
    except Exception as e:
        print(f"Error in client: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        client_socket.close()

if __name__ == "_main_":
    start_client()